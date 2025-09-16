from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import LOCATIONS_PROMPT


_REQUIRED_LOCATION_KEYS = {
    "id",
    "name",
    "type",
    "summary",
    "sensory",
    "plot_functions",
    "hazards",
    "ties",
    "first_seen",
    "coords",
}


def _prepare(out_dir: str | None) -> tuple[Config, Path]:
    cfg = load_config()
    base = Path(out_dir) if out_dir is not None else Path(cfg.out_dir)
    return cfg, base


def _generate(prompt: str, cfg: Config) -> str:
    client = get_client(cfg.region, cfg.profile)
    return invoke_text_model(
        client=client,
        model_id=cfg.model_id,
        prompt=prompt,
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
    )


def _split_locations_output(text: str) -> tuple[str, list[str]]:
    md_lines: list[str] = []
    json_lines: list[str] = []
    collecting_json = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if collecting_json:
                collecting_json = False
            else:
                lowered = stripped.lower()
                if "json" in lowered:
                    collecting_json = True
            continue

        if collecting_json:
            if not stripped:
                continue
            obj = _parse_location_json(stripped)
            json_lines.append(json.dumps(obj, separators=(",", ":")))
            continue

        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            md_lines.append(line)
        else:
            if isinstance(obj, dict):
                _validate_location_object(obj)
                json_lines.append(json.dumps(obj, separators=(",", ":")))
                collecting_json = True
            else:
                md_lines.append(line)

    if not json_lines:
        raise RuntimeError("Locations prompt response did not contain JSONL data")

    return "\n".join(md_lines).strip() + "\n", json_lines


def _parse_location_json(line: str) -> dict[str, Any]:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid JSON in locations JSONL block") from exc
    if not isinstance(obj, dict):
        raise RuntimeError("Locations JSONL entry must be an object")
    _validate_location_object(obj)
    return obj


def _validate_location_object(obj: dict[str, Any]) -> None:
    missing = _REQUIRED_LOCATION_KEYS - obj.keys()
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise RuntimeError(f"Location JSON missing keys: {missing_str}")

    for key in ("sensory", "plot_functions", "hazards", "ties"):
        value = obj.get(key)
        if not isinstance(value, list):
            raise RuntimeError(f"Location field '{key}' must be a list")


def run(seed_path: str, world_path: str, out_dir: str | None = None) -> tuple[str, str]:
    seed_file = Path(seed_path)
    if not seed_file.exists():
        raise FileNotFoundError(f"Seed ideas file not found: {seed_file}")

    world_file = Path(world_path)
    if not world_file.exists():
        raise FileNotFoundError(f"World file not found: {world_file}")

    seed_text = read_text(seed_file)
    world_text = read_text(world_file)

    cfg, base_dir = _prepare(out_dir)
    bible_dir = ensure_dir(base_dir / "04_story_bible")

    prompt = LOCATIONS_PROMPT.format(seed=seed_text, world=world_text)
    locations_text = _generate(prompt, cfg)

    markdown, json_lines = _split_locations_output(locations_text)

    md_path = write_text(bible_dir / "locations.md", markdown)
    jsonl_path = write_text(bible_dir / "locations.jsonl", "\n".join(json_lines) + "\n")

    return str(md_path), str(jsonl_path)
