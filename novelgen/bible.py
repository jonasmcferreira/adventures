from __future__ import annotations

from pathlib import Path

from .bedrock_client import get_client, invoke_text_model
from .config import Config, load_config
from .io_utils import ensure_dir, read_text
from .prompts import BIBLE_UPDATE_PROMPT


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


def run(scene_path: str, out_dir: str | None = None) -> str:
    scene_file = Path(scene_path)
    if not scene_file.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_file}")

    scene_text = read_text(scene_file)

    cfg, base_dir = _prepare(out_dir)
    bible_dir = ensure_dir(base_dir / "04_story_bible")

    prompt = BIBLE_UPDATE_PROMPT.format(scene=scene_text)
    update_text = _generate(prompt, cfg).strip()

    changelog_path = bible_dir / "bible_changelog.md"
    header = f"## Update from {scene_file.name}\n\n"
    entry = header + update_text + "\n\n"

    mode = "a" if changelog_path.exists() else "w"
    with changelog_path.open(mode, encoding="utf-8") as handle:
        handle.write(entry)

    return str(changelog_path)
