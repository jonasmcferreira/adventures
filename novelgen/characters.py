from __future__ import annotations

from pathlib import Path

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import CHARACTERS_PROMPT


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


def run(seed_path: str, out_dir: str | None = None) -> str:
    path = Path(seed_path)
    if not path.exists():
        raise FileNotFoundError(f"Seed ideas file not found: {path}")

    seed_text = read_text(path)

    cfg, base_dir = _prepare(out_dir)
    foundation_dir = ensure_dir(base_dir / "01_foundation")

    prompt = CHARACTERS_PROMPT.format(seed=seed_text)
    characters_text = _generate(prompt, cfg)

    roster_path = write_text(foundation_dir / "characters.md", characters_text)
    return str(roster_path)
