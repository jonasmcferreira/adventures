from __future__ import annotations

from pathlib import Path

from .io_utils import ensure_dir, write_json, write_text


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Expected artifact missing: {path}")
    return path


def _rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def run(out_dir: str = "./output") -> str:
    base = ensure_dir(out_dir)

    premise = _require(base / "01_foundation" / "premise.md")
    seed = _require(base / "01_foundation" / "seed_ideas.md")
    characters = _require(base / "01_foundation" / "characters.md")
    arcs = _require(base / "02_outline" / "character_arcs.md")
    chapter_plan = _require(base / "02_outline" / "chapter_plan.md")
    scenes_dir = _require(base / "03_scenes")
    world = _require(base / "04_story_bible" / "world.md")
    locations_md = _require(base / "04_story_bible" / "locations.md")
    locations_jsonl = _require(base / "04_story_bible" / "locations.jsonl")
    bible_changelog = _require(base / "04_story_bible" / "bible_changelog.md")

    manifest = {
        "premise": _rel(premise, base),
        "seed": _rel(seed, base),
        "characters": _rel(characters, base),
        "arcs": _rel(arcs, base),
        "world": _rel(world, base),
        "locations_md": _rel(locations_md, base),
        "locations_jsonl": _rel(locations_jsonl, base),
        "chapter_plan": _rel(chapter_plan, base),
        "scenes_dir": _rel(scenes_dir, base),
        "bible_changelog": _rel(bible_changelog, base),
    }

    index_path = write_json(base / "index.json", manifest)

    lines = [
        "# Story Index",
        "",
        f"- [Premise]({_rel(premise, base)})",
        f"- [Seed ideas]({_rel(seed, base)})",
        f"- [Characters]({_rel(characters, base)})",
        f"- [Character arcs]({_rel(arcs, base)})",
        f"- [World bible]({_rel(world, base)})",
        f"- [Locations]({_rel(locations_md, base)})",
        f"- [Locations JSONL]({_rel(locations_jsonl, base)})",
        f"- [Chapter plan]({_rel(chapter_plan, base)})",
        f"- [Scenes directory]({_rel(scenes_dir, base)})",
        f"- [Bible changelog]({_rel(bible_changelog, base)})",
    ]
    write_text(base / "INDEX.md", "\n".join(lines) + "\n")

    return str(index_path)
