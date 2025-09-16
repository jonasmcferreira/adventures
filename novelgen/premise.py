from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, write_text, write_yaml
from .prompts import PREMISE_PROMPT


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


def run(constraints: dict[str, Any], out_dir: str | None = None) -> str:
    if not constraints:
        raise ValueError("constraints must not be empty")

    cfg, base_dir = _prepare(out_dir)
    foundation_dir = ensure_dir(base_dir / "01_foundation")

    constraints_yaml = yaml.safe_dump(constraints, sort_keys=False)
    prompt = PREMISE_PROMPT.format(constraints=constraints_yaml)
    premise_text = _generate(prompt, cfg)

    premise_path = write_text(foundation_dir / "premise.md", premise_text)
    write_yaml(foundation_dir / "premise.yaml", constraints)

    return str(premise_path)
