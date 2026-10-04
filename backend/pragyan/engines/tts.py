"""Narration: Kokoro-82M (local ONNX) -> Windows SAPI (pyttsx3) -> silent timing fallback.

Each scene's narration arrives as ordered segments (segment k = on-screen item k).
We synthesise sentence by sentence, stitch with natural pauses and return
frame-accurate segment + word timings so visuals reveal exactly on cue.
"""
from __future__ import annotations

import asyncio
import logging
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf

from ..config import settings

log = logging.getLogger("pragyan.tts")

SR = 24000
GAP_SENTENCE = 0.1
GAP_SEGMENT = 0.24

LANG_BY_PREFIX = {"a": "en-us", "b": "en-gb", "h": "hi", "e": "es", "f": "fr-fr", "i": "it", "p": "pt-br", "j": "ja", "z": "cmn"}
DEFAULT_VOICE_BY_LANG = {"en": "af_heart", "hi": "hf_alpha", "es": "ef_dora", "fr": "ff_siwis", "it": "if_sara", "pt": "pf_dora", "ja": "jf_alpha", "zh": "zf_xiaobei"}

_kokoro = None
_kokoro_lock = threading.Lock()
_synth_lock = threading.Lock()


def _get_kokoro():
    global _kokoro
    with _kokoro_lock:
        if _kokoro is None and settings.kokoro_model.exists():
            import os

            import onnxruntime as rt
            from kokoro_onnx import Kokoro

            # Benchmarked on this class of laptop: fp32 + ~12 intra-op threads is fastest
            # (int8 is slower without VNNI; DirectML can't run Kokoro's ConvTranspose).
            so = rt.SessionOptions()
            so.intra_op_num_threads = max(2, min(12, (os.cpu_count() or 8) // 2))
            so.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess = rt.InferenceSession(str(settings.kokoro_model), so, providers=["CPUExecutionProvider"])
            _kokoro = Kokoro.from_session(sess, str(settings.kokoro_voices))
    return _kokoro


# ---------------------------------------------------------------------------
# Make text speakable: LLM narration often leaks symbols and LaTeX.
# ---------------------------------------------------------------------------
_SYMBOLS = [
    (r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1 over \2"),
    (r"\\sqrt\{([^{}]+)\}", r"the square root of \1"),
    (r"\\(left|right|displaystyle|,|;|!|quad)", " "),
    (r"\\cdot|\\times|×", " times "),
    (r"\\approx|≈", " approximately "),
    (r"\\pi|π", " pi "),
    (r"\\lambda|λ", " lambda "),
    (r"\\theta|θ", " theta "),
    (r"\\alpha|α", " alpha "),
    (r"\\beta|β", " beta "),
    (r"\\Delta|Δ", " delta "),
    (r"\\infty|∞", " infinity "),
    (r"\\int|∫", " the integral of "),
    (r"\\sum|∑", " the sum of "),
    (r"\\leq|≤", " less than or equal to "),
    (r"\\geq|≥", " greater than or equal to "),
    (r"\\neq|≠", " not equal to "),
    (r"\\rightarrow|→|->", " goes to "),
    (r"√", " square root of "),
    (r"\^\s*2\b|²", " squared"),
    (r"\^\s*3\b|³", " cubed"),
    (r"\^\s*\{?(-?\w+)\}?", r" to the power \1"),
    (r"(?<=\d)\s*/\s*(?=\d)", " over "),
    (r"(?<=\d)\s*%", " percent"),
    (r"(?<=[\w)])\s*=\s*(?=[\w(-])", " equals "),
    (r"(?<=[\w)])\s+\+\s+(?=[\w(])", " plus "),
    (r"(?<=\d)\s+[-−]\s+(?=\d)", " minus "),
    (r"[{}$\\_*#`]", " "),
]


def speakable(text: str) -> str:
    t = text
    for pat, rep in _SYMBOLS:
        t = re.sub(pat, rep, t)
    return re.sub(r"\s+", " ", t).strip()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?।])\s+", text.strip())
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Kokoro is happiest under ~400 chars per call.
        while len(p) > 380:
            cut = p.rfind(",", 0, 380)
            cut = cut if cut > 120 else 380
            out.append(p[: cut + 1].strip())
            p = p[cut + 1 :].strip()
        if p:
            out.append(p)
    return out


@dataclass
class TimedSegment:
    text: str
    start: float  # seconds within the scene audio
    end: float
    words: list[tuple[str, float, float]] = field(default_factory=list)


@dataclass
class SceneAudio:
    path: Path | None
    seconds: float
    segments: list[TimedSegment]
    engine: str


def _trim(audio: np.ndarray) -> np.ndarray:
    """Cut leading/trailing near-silence. Threshold is relative to the clip's peak (voices differ in level)."""
    if len(audio) == 0:
        return audio
    # 10 ms RMS envelope is far more robust than per-sample amplitude.
    win = int(0.01 * SR)
    n = len(audio) // win
    if n == 0:
        return audio
    env = np.sqrt(np.mean(audio[: n * win].reshape(n, win) ** 2, axis=1))
    thresh = max(1e-4, float(env.max()) * 0.04)
    loud = np.where(env > thresh)[0]
    if len(loud) == 0:
        return audio
    a = max(0, loud[0] * win - int(0.02 * SR))
    b = min(len(audio), (loud[-1] + 1) * win + int(0.05 * SR))
    return audio[a:b]


def _word_times(text: str, t0: float, t1: float) -> list[tuple[str, float, float]]:
    """Distribute a sentence's span over its words, weighted by length + punctuation pauses."""
    words = text.split()
    if not words:
        return []
    weights = [len(re.sub(r"\W", "", w)) + 2 + (3 if re.search(r"[,;:]$", w) else 0) + (4 if re.search(r"[.!?]$", w) else 0) for w in words]
    total = sum(weights)
    out, t = [], t0
    for w, wt in zip(words, weights):
        d = (t1 - t0) * wt / total
        out.append((w, t, t + d * 0.92))
        t += d
    return out


class Narrator:
    def __init__(self, voice: str | None = None, language: str = "en", speed: float = 1.0):
        lang2 = (language or "en")[:2]
        self.voice = voice or DEFAULT_VOICE_BY_LANG.get(lang2, settings.default_voice)
        self.lang = LANG_BY_PREFIX.get(self.voice[0], "en-us")
        self.speed = speed
        self.engine = "kokoro" if _get_kokoro() else "sapi"

    def _synth_kokoro(self, text: str, speed: float) -> np.ndarray:
        k = _get_kokoro()
        # espeak-ng (Kokoro's phonemizer) is not thread-safe; scenes are voiced from parallel threads.
        with _synth_lock:
            samples, sr = k.create(text, voice=self.voice, speed=speed, lang=self.lang)
        if sr != SR:
            idx = np.linspace(0, len(samples) - 1, int(len(samples) * SR / sr))
            samples = np.interp(idx, np.arange(len(samples)), samples)
        return _trim(np.asarray(samples, dtype=np.float32))

    def _synth_sapi(self, text: str, tmp: Path, speed: float = 1.0) -> np.ndarray:
        import pyttsx3

        with _synth_lock:  # SAPI via COM deadlocks when driven from several threads at once
            eng = pyttsx3.init()
            eng.setProperty("rate", int(175 * speed))
            eng.save_to_file(text, str(tmp))
            eng.runAndWait()
        data, sr = sf.read(str(tmp), dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != SR:
            idx = np.linspace(0, len(data) - 1, int(len(data) * SR / sr))
            data = np.interp(idx, np.arange(len(data)), data).astype(np.float32)
        return _trim(data)

    def _synth(self, text: str, tmp: Path, speed: float) -> np.ndarray:
        """Per-sentence fallback chain. A failure never switches engines for the rest of the job."""
        if self.engine == "kokoro":
            for attempt in range(2):
                try:
                    return self._synth_kokoro(text if attempt == 0 else re.sub(r"[^\w\s.,!?'-]", " ", text), speed)
                except Exception as e:  # pragma: no cover
                    log.warning("kokoro failed on %r (%s)", text[:60], e)
        # SAPI only has the system's (usually English) voices — useless for other languages.
        if self.lang.startswith("en"):
            try:
                return self._synth_sapi(text, tmp, speed)
            except Exception as e:  # pragma: no cover
                log.warning("SAPI failed (%s)", e)
        log.warning("using silent timing for %r", text[:60])
        secs = max(0.8, len(text.split()) / 2.6)
        return np.zeros(int(secs * SR), dtype=np.float32)

    def synth_scene(self, segments: list[str], out: Path, pauses: dict[int, float] | None = None, speed: float | None = None) -> SceneAudio:
        """Blocking: synthesise ordered segments into one WAV with timings."""
        speed = speed or self.speed
        out.parent.mkdir(parents=True, exist_ok=True)
        chunks: list[np.ndarray] = []
        timed: list[TimedSegment] = []
        t = 0.0
        tmp = out.with_suffix(".tmp.wav")
        for si, seg in enumerate(segments):
            if pauses and si in pauses and t > 0:
                chunks.append(np.zeros(int(pauses[si] * SR), dtype=np.float32))
                t += pauses[si]
            seg = (seg or "").strip()
            if not seg:
                timed.append(TimedSegment("", t, t))
                continue
            seg_start = t
            words: list[tuple[str, float, float]] = []
            sents = sentences(seg)
            for k, sent in enumerate(sents):
                audio = self._synth(speakable(sent), tmp, speed)
                dur = len(audio) / SR
                words += _word_times(sent, t, t + dur)
                chunks.append(audio)
                t += dur
                if k < len(sents) - 1:  # the segment gap below replaces the last sentence gap
                    chunks.append(np.zeros(int(GAP_SENTENCE * SR), dtype=np.float32))
                    t += GAP_SENTENCE
            timed.append(TimedSegment(seg, seg_start, t, words))
            chunks.append(np.zeros(int(GAP_SEGMENT * SR), dtype=np.float32))
            t += GAP_SEGMENT
        tmp.unlink(missing_ok=True)
        if not chunks:
            return SceneAudio(None, 0.0, timed, self.engine)
        audio = np.concatenate(chunks)
        peak = float(np.max(np.abs(audio))) or 1.0
        audio = (audio / peak * 0.89).astype(np.float32)
        sf.write(str(out), audio, SR, subtype="PCM_16")
        return SceneAudio(out, len(audio) / SR, timed, self.engine)

    async def synth_scene_async(self, segments: list[str], out: Path, pauses: dict[int, float] | None = None, speed: float | None = None) -> SceneAudio:
        return await asyncio.to_thread(self.synth_scene, segments, out, pauses, speed)


def list_voices() -> list[str]:
    k = _get_kokoro()
    if k:
        try:
            return sorted(k.get_voices())
        except Exception:
            pass
    return ["sapi-default"]
