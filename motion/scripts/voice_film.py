"""Voice the launch film's script with local Kokoro and write timings for the composition.

    backend/.venv/Scripts/python motion/scripts/voice_film.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from pragyan.engines.tts import Narrator  # noqa: E402

LINES = {
    "open": "Every question deserves a great explanation.",
    "team": "Pragyan reads what you ask, and assembles a team of agents to answer it.",
    "think": "It understands. It solves. And it checks its own work.",
    "board": "A creative director storyboards every scene,",
    "maths": "and the maths moves exactly the way it should.",
    "loop": "Then it renders, inspects its own frames, and fixes what it finds.",
    "local": "No cloud. No API keys. Just one laptop.",
    "end": "Pragyan. Ask anything, and watch it explained.",
}

out_dir = ROOT / "motion" / "public" / "film"
out_dir.mkdir(parents=True, exist_ok=True)
n = Narrator(voice="am_onyx", speed=0.97)
timings = {}
for key, line in LINES.items():
    sa = n.synth_scene([line], out_dir / f"{key}.wav")
    seg = sa.segments[0]
    timings[key] = {
        "text": line,
        "seconds": round(sa.seconds, 3),
        "words": [{"w": w, "s": round(a, 3), "e": round(b, 3)} for w, a, b in seg.words],
    }
    print(f"{key:6} {sa.seconds:5.2f}s  {line}")
(ROOT / "motion" / "src" / "film" / "narration.json").write_text(json.dumps(timings, indent=1), "utf8")
