from __future__ import annotations

from pathlib import Path

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import ARCS_PROMPT


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


def run(roster_path: str, out_dir: str | None = None) -> str:
    path = Path(roster_path)
    if not path.exists():
        raise FileNotFoundError(f"Character roster not found: {path}")

    roster_text = read_text(path)

    cfg, base_dir = _prepare(out_dir)
    outline_dir = ensure_dir(base_dir / "02_outline")

    prompt = ARCS_PROMPT.format(roster=roster_text)
    arcs_text = _generate(prompt, cfg)

    arcs_path = write_text(outline_dir / "character_arcs.md", arcs_text)
    return str(arcs_path)
