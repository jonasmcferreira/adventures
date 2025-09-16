from __future__ import annotations

from pathlib import Path
from typing import Any

from . import arcs, bible, chapters, characters, indexer, locations, premise, scenes, seed, world
from .config import load_config


def run_all(constraints: dict[str, Any], cards: int = 3, out_dir: str | None = None) -> dict[str, Any]:
    if not constraints:
        raise ValueError("constraints must not be empty")
    if cards <= 0:
        raise ValueError("cards must be positive")

    cfg = load_config()
    target_out_dir = out_dir or cfg.out_dir

    premise_path = premise.run(constraints, out_dir=target_out_dir)
    seed_path = seed.run(premise_path, out_dir=target_out_dir)
    characters_path = characters.run(seed_path, out_dir=target_out_dir)
    arcs_path = arcs.run(characters_path, out_dir=target_out_dir)
    world_path = world.run(seed_path, out_dir=target_out_dir)
    locations_md_path, locations_jsonl_path = locations.run(
        seed_path, world_path, out_dir=target_out_dir
    )
    chapter_plan_path = chapters.run(
        seed_path,
        arcs_path,
        world_path,
        locations_jsonl_path,
        out_dir=target_out_dir,
    )
    scene_outputs = scenes.run(chapter_plan_path, out_dir=target_out_dir, limit=cards)

    bible_updates: list[str] = []
    for _, draft_path in scene_outputs:
        bible_updates.append(bible.run(draft_path, out_dir=target_out_dir))

    index_json_path = indexer.run(out_dir=target_out_dir)
    index_md_path = str(Path(index_json_path).with_name("INDEX.md"))

    return {
        "premise": premise_path,
        "seed": seed_path,
        "characters": characters_path,
        "arcs": arcs_path,
        "world": world_path,
        "locations_md": locations_md_path,
        "locations_jsonl": locations_jsonl_path,
        "chapter_plan": chapter_plan_path,
        "scenes": scene_outputs,
        "bible_updates": bible_updates,
        "index_json": index_json_path,
        "index_markdown": index_md_path,
        "out_dir": target_out_dir,
    }
