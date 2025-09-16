from __future__ import annotations

from pathlib import Path

import yaml

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import SEED_PROMPT


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


def run(premise_path: str, out_dir: str | None = None) -> str:
    path = Path(premise_path)
    if not path.exists():
        raise FileNotFoundError(f"Premise file not found: {path}")

    constraints_path = path.with_suffix(".yaml")
    if not constraints_path.exists():
        raise FileNotFoundError("premise.yaml not found beside premise markdown")

    premise_text = read_text(path)
    with constraints_path.open("r", encoding="utf-8") as handle:
        constraints = yaml.safe_load(handle) or {}

    cfg, base_dir = _prepare(out_dir)
    foundation_dir = ensure_dir(base_dir / "01_foundation")

    prompt = SEED_PROMPT.format(
        premise=premise_text,
        constraints=yaml.safe_dump(constraints, sort_keys=False),
    )
    seeds = _generate(prompt, cfg)

    seed_path = write_text(foundation_dir / "seed_ideas.md", seeds)
    return str(seed_path)
