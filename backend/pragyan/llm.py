"""Thin, robust Ollama client.

Small local models drift out of shape. Every structured call therefore:
  1. constrains decoding with a JSON schema (Ollama `format`),
  2. validates with pydantic,
  3. on failure, shows the model its own output + the validation error and asks for a repair.
"""
from __future__ import annotations

import asyncio
import base64
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .config import settings

T = TypeVar("T", bound=BaseModel)

_sem: asyncio.Semaphore | None = None


def _semaphore() -> asyncio.Semaphore:
    global _sem
    if _sem is None:
        _sem = asyncio.Semaphore(max(1, settings.llm_concurrency))
    return _sem


class LLMError(RuntimeError):
    pass


class LLMTimeout(LLMError):
    pass


BRIEF_NUDGE = "Your previous answer ran far too long. Return the JSON again, short and complete: the minimum number of list items, no repetition, every list closed."


class LLMStats:
    """Process-wide counters surfaced in the UI."""

    calls = 0
    tokens_out = 0
    seconds = 0.0
    repairs = 0


def _inline_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Ollama's grammar converter is happiest without $refs; inline them."""
    defs = schema.pop("$defs", {})

    def walk(node: Any, is_props: bool = False) -> Any:
        if isinstance(node, dict):
            if "$ref" in node and not is_props:
                name = node["$ref"].split("/")[-1]
                return walk(dict(defs[name]))
            if is_props:  # keys here are field names — keep every one (incl. a field called "title")
                return {k: walk(v) for k, v in node.items()}
            return {
                k: walk(v, is_props=(k == "properties"))
                for k, v in node.items()
                if not (k in ("title", "default") and not isinstance(v, (dict, list)))
            }
        if isinstance(node, list):
            return [walk(x) for x in node]
        return node

    return walk(schema)


def schema_for(model: type[BaseModel]) -> dict[str, Any]:
    return _inline_refs(model.model_json_schema())


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.M)


def _extract_json(text: str) -> Any:
    text = _FENCE.sub("", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def _encode_image(p: str | Path) -> str:
    return base64.b64encode(Path(p).read_bytes()).decode()


async def chat(
    messages: list[dict[str, Any]],
    *,
    model: str | None = None,
    fmt: dict[str, Any] | str | None = None,
    think: bool = False,
    temperature: float = 0.4,
    num_predict: int | None = None,
    on_stats: Callable[[dict[str, Any]], None] | None = None,
    timeout: float = 600,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model or settings.model_reason,
        "messages": messages,
        "stream": False,
        "think": think,
        "keep_alive": settings.llm_keep_alive,
        "options": {
            "temperature": temperature,
            "num_ctx": settings.llm_ctx,
            "top_p": 0.9,
            "presence_penalty": 0.3,
        },
    }
    if fmt is not None:
        payload["format"] = fmt
    if num_predict:
        payload["options"]["num_predict"] = num_predict
    async with _semaphore():
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(f"{settings.ollama_host}/api/chat", json=payload)
        except httpx.TimeoutException as e:
            # Closing the connection makes Ollama abort the generation, freeing the GPU.
            raise LLMTimeout(f"no answer within {timeout:.0f}s") from e
        if r.status_code != 200:
            raise LLMError(f"Ollama {r.status_code}: {r.text[:400]}")
        data = r.json()
        dt = time.perf_counter() - t0
    LLMStats.calls += 1
    LLMStats.tokens_out += data.get("eval_count", 0) or 0
    LLMStats.seconds += dt
    if on_stats:
        ev = data.get("eval_count", 0) or 0
        ed = (data.get("eval_duration", 0) or 0) / 1e9
        on_stats({"model": payload["model"], "tokens": ev, "seconds": round(dt, 1), "tps": round(ev / ed, 1) if ed else None})
    return data


async def structured(
    model_cls: type[T],
    system: str,
    user: str,
    *,
    images: list[str | Path] | None = None,
    model: str | None = None,
    think: bool = False,
    temperature: float = 0.4,
    attempts: int = 3,
    validate: Callable[[T], str | None] | None = None,
    on_stats: Callable[[dict[str, Any]], None] | None = None,
    on_repair: Callable[[str], None] | None = None,
) -> T:
    """Schema-constrained call with validate-and-repair loop.

    `validate` may return a human-readable problem string for semantic checks
    (e.g. "narration missing for item 3") which is fed back like a schema error.
    """
    fmt = schema_for(model_cls)
    user_msg: dict[str, Any] = {"role": "user", "content": user}
    if images:
        user_msg["images"] = [_encode_image(p) for p in images]
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}, user_msg]
    last_err = ""
    for i in range(attempts):
        temp = temperature if i == 0 else max(0.15, temperature - 0.2)
        # Grammar-constrained decoding can loop (e.g. repeating array items forever, since maxItems is
        # not enforced). Every call is capped in tokens and time; a runaway counts as a failed attempt.
        try:
            if think:
                try:
                    data = await chat(messages, model=model, fmt=fmt, think=True, temperature=temp, on_stats=on_stats, timeout=240, num_predict=9000)
                except LLMTimeout:
                    if on_repair:
                        on_repair("thinking ran too long — answering directly instead")
                    think = False
                    data = await chat(messages, model=model, fmt=fmt, think=False, temperature=temp, on_stats=on_stats, timeout=180, num_predict=4096)
            else:
                data = await chat(messages, model=model, fmt=fmt, think=False, temperature=temp, on_stats=on_stats, timeout=180, num_predict=4096)
        except LLMTimeout as e:
            last_err = f"generation ran away ({e}); answer concisely and close every list"
            LLMStats.repairs += 1
            if on_repair:
                on_repair(last_err)
            temperature = max(0.1, temperature - 0.2)
            messages = messages[:2] + [{"role": "user", "content": BRIEF_NUDGE}]
            continue
        if data.get("done_reason") == "length":
            last_err = "output was cut off at the length limit — be more concise, keep lists short"
            LLMStats.repairs += 1
            if on_repair:
                on_repair(last_err)
            messages = messages[:2] + [{"role": "user", "content": BRIEF_NUDGE}]
            continue
        content = data.get("message", {}).get("content", "")
        try:
            obj = model_cls.model_validate(_extract_json(content))
            problem = validate(obj) if validate else None
            if not problem:
                return obj
            last_err = problem
        except (ValidationError, json.JSONDecodeError, ValueError) as e:
            last_err = str(e)[:1500]
        LLMStats.repairs += 1
        if on_repair:
            on_repair(last_err[:300])
        messages = messages[:2] + [
            {"role": "assistant", "content": content[:6000]},
            {
                "role": "user",
                "content": f"Your JSON had problems:\n{last_err}\n\nReturn the COMPLETE corrected JSON object only. Keep everything that was fine.",
            },
        ]
    raise LLMError(f"{model_cls.__name__}: could not produce valid output after {attempts} attempts: {last_err[:400]}")


async def text(system: str, user: str, *, model: str | None = None, think: bool = False, temperature: float = 0.3, on_stats=None) -> str:
    data = await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=model,
        think=think,
        temperature=temperature,
        on_stats=on_stats,
    )
    return data.get("message", {}).get("content", "")


async def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{settings.ollama_host}/api/embed", json={"model": settings.model_embed, "input": texts})
    if r.status_code != 200:
        raise LLMError(f"embed failed: {r.text[:200]}")
    return r.json()["embeddings"]


def cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    return num / (da * db) if da and db else 0.0


async def list_models() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{settings.ollama_host}/api/tags")
        return r.json().get("models", [])
    except Exception:
        return []
