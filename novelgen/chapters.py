from __future__ import annotations

from pathlib import Path

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import CHAPTER_PLAN_PROMPT


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


def run(
    seed_path: str,
    arcs_path: str,
    world_path: str,
    locations_jsonl_path: str,
    out_dir: str | None = None,
) -> str:
    seed_text = read_text(Path(seed_path))
    arcs_text = read_text(Path(arcs_path))
    world_text = read_text(Path(world_path))
    locations_text = read_text(Path(locations_jsonl_path))

    cfg, base_dir = _prepare(out_dir)
    outline_dir = ensure_dir(base_dir / "02_outline")

    prompt = CHAPTER_PLAN_PROMPT.format(
        seed=seed_text,
        arcs=arcs_text,
        world=world_text,
        locations=locations_text,
    )
    chapter_plan = _generate(prompt, cfg)

    plan_path = write_text(outline_dir / "chapter_plan.md", chapter_plan)
    return str(plan_path)
