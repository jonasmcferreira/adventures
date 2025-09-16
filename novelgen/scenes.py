from __future__ import annotations

import re
from pathlib import Path

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text, write_text
from .prompts import SCENE_CARD_PROMPT, SCENE_DRAFT_PROMPT

_ROW_PATTERN = re.compile(r"^\|\s*\d+\s*\|.*$", re.MULTILINE)


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


def _extract_rows(chapter_plan: str, limit: int) -> list[str]:
    rows = _ROW_PATTERN.findall(chapter_plan)
    if not rows:
        raise ValueError("No chapter rows found in chapter plan")
    return rows[:limit]


def run(
    chapter_plan_path: str,
    out_dir: str | None = None,
    limit: int = 3,
) -> list[tuple[str, str]]:
    if limit <= 0:
        raise ValueError("limit must be positive")

    plan_text = read_text(Path(chapter_plan_path))
    rows = _extract_rows(plan_text, limit)

    cfg, base_dir = _prepare(out_dir)
    scenes_dir = ensure_dir(base_dir / "03_scenes")

    outputs: list[tuple[str, str]] = []
    for index, row in enumerate(rows, start=1):
        card_prompt = SCENE_CARD_PROMPT.format(row=row)
        card_text = _generate(card_prompt, cfg)

        draft_prompt = SCENE_DRAFT_PROMPT.format(row=row, card=card_text)
        draft_text = _generate(draft_prompt, cfg)

        card_path = write_text(scenes_dir / f"S{index:03d}_card.md", card_text)
        draft_path = write_text(scenes_dir / f"S{index:03d}_draft.md", draft_text)
        outputs.append((str(card_path), str(draft_path)))

    return outputs
