"""Runtime configuration. Everything is local: Ollama, Kokoro, Manim, Remotion, ffmpeg."""
from __future__ import annotations

import sys
import shutil
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    # --- storage -----------------------------------------------------------
    mongodb_uri: str = ""
    mongodb_db: str = "pragyan_ai"
    storage_dir: Path = ROOT / "storage"
    steering_dir: Path = ROOT / "steering"
    motion_dir: Path = ROOT / "motion"

    # --- server ------------------------------------------------------------
    host: str = "127.0.0.1"
    port: int = 8000
    public_base: str = "http://127.0.0.1:8000"  # used by the renderer to fetch audio/clips
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- LLMs (all via Ollama) ---------------------------------------------
    ollama_host: str = "http://127.0.0.1:11434"
    model_reason: str = "qwen3.5:9b"  # intent, planning, storyboard, scene design
    model_code: str = "qwen3.5:9b"  # Manim code + fixer (qwen2.5-coder:7b also works)
    model_vision: str = "qwen3.5:9b"  # image ingest + visual critic (llava:7b fallback)
    model_embed: str = "nomic-embed-text"
    llm_concurrency: int = 1  # one 8 GB GPU => serialise; raise if you have VRAM to spare
    llm_ctx: int = 16384
    llm_keep_alive: str = "30m"
    solver_think: bool = True  # let the solver use Qwen's thinking mode

    # --- media --------------------------------------------------------------
    kokoro_model: Path = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
    kokoro_voices: Path = ROOT / "models" / "kokoro" / "voices-v1.0.bin"
    default_voice: str = "af_heart"
    fps: int = 30
    manim_timeout: int = 240
    manim_attempts: int = 3
    render_concurrency: int = 0  # 0 => auto
    node_bin: str = shutil.which("node") or "node"
    python_bin: str = sys.executable

    @property
    def jobs_dir(self) -> Path:
        return self.storage_dir / "jobs"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.jobs_dir.mkdir(parents=True, exist_ok=True)
    return s


settings = get_settings()
