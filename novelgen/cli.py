from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import typer

from . import arcs, bible, chapters, characters, indexer, locations, orchestrator, premise, scenes, seed, world
from .config import load_config

app = typer.Typer(help="novelgen CLI for running the AWS Bedrock fiction pipeline.")

_EXTRA_SETTINGS = {"allow_extra_args": True, "ignore_unknown_options": True}


def _parse_constraints(args: list[str]) -> dict[str, str]:
    constraints: Dict[str, str] = {}
    pending_key: str | None = None

    for arg in args:
        if arg.startswith("--"):
            option = arg[2:]
            if "=" in option:
                key, value = option.split("=", 1)
                key = key.replace("-", "_")
                constraints[key] = value
                pending_key = None
            else:
                pending_key = option.replace("-", "_")
                if pending_key not in constraints:
                    constraints[pending_key] = ""
        else:
            if pending_key is None:
                raise typer.BadParameter(f"Unexpected argument '{arg}'.")
            current = constraints.get(pending_key, "")
            constraints[pending_key] = f"{current} {arg}".strip()

    if pending_key is not None and not constraints.get(pending_key):
        constraints[pending_key] = "true"

    return {key: value.strip() for key, value in constraints.items() if value.strip()}


def _resolve_out_dir(custom: str | None) -> str:
    if custom is not None:
        return custom
    return load_config().out_dir


@app.command(context_settings=_EXTRA_SETTINGS)
def premise_cmd(
    ctx: typer.Context,
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Generate a story premise from constraint flags."""

    constraints = _parse_constraints(list(ctx.args))
    if not constraints:
        raise typer.BadParameter("Provide at least one constraint option like --genre.")

    result_path = premise.run(constraints, out_dir=_resolve_out_dir(out_dir))
    typer.echo(result_path)


@app.command()
def seed_cmd(
    premise_path: str = typer.Option(
        None,
        help="Path to premise markdown.",
    ),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Expand the premise into seed ideas."""

    if premise_path is None:
        cfg = load_config()
        premise_path = str(Path(cfg.out_dir) / "01_foundation" / "premise.md")

    result_path = seed.run(premise_path, out_dir=_resolve_out_dir(out_dir))
    typer.echo(result_path)


@app.command()
def characters_cmd(
    seed_path: str = typer.Option(
        None,
        help="Path to seed ideas markdown.",
    ),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Create the character roster."""

    if seed_path is None:
        cfg = load_config()
        seed_path = str(Path(cfg.out_dir) / "01_foundation" / "seed_ideas.md")

    result_path = characters.run(seed_path, out_dir=_resolve_out_dir(out_dir))
    typer.echo(result_path)


@app.command()
def arcs_cmd(
    roster_path: str = typer.Option(
        None,
        help="Path to character roster markdown.",
    ),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Generate character arcs."""

    if roster_path is None:
        cfg = load_config()
        roster_path = str(Path(cfg.out_dir) / "01_foundation" / "characters.md")

    result_path = arcs.run(roster_path, out_dir=_resolve_out_dir(out_dir))
    typer.echo(result_path)


@app.command()
def world_cmd(
    seed_path: str = typer.Option(
        None,
        help="Path to seed ideas markdown.",
    ),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Build the world bible summary."""

    if seed_path is None:
        cfg = load_config()
        seed_path = str(Path(cfg.out_dir) / "01_foundation" / "seed_ideas.md")

    result_path = world.run(seed_path, out_dir=_resolve_out_dir(out_dir))
    typer.echo(result_path)


@app.command()
def locations_cmd(
    seed_path: str = typer.Option(None, help="Path to seed ideas markdown."),
    world_path: str = typer.Option(None, help="Path to world markdown."),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Create location compendium outputs."""

    cfg = load_config()
    if seed_path is None:
        seed_path = str(Path(cfg.out_dir) / "01_foundation" / "seed_ideas.md")
    if world_path is None:
        world_path = str(Path(cfg.out_dir) / "04_story_bible" / "world.md")

    md_path, jsonl_path = locations.run(
        seed_path,
        world_path,
        out_dir=_resolve_out_dir(out_dir),
    )
    typer.echo(json.dumps({"locations_md": md_path, "locations_jsonl": jsonl_path}, indent=2))


@app.command()
def plan_cmd(
    seed_path: str = typer.Option(None, help="Path to seed ideas markdown."),
    arcs_path: str = typer.Option(None, help="Path to character arcs markdown."),
    world_path: str = typer.Option(None, help="Path to world markdown."),
    locations_jsonl_path: str = typer.Option(None, help="Path to locations JSONL."),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Generate the 50 chapter outline."""

    cfg = load_config()
    if seed_path is None:
        seed_path = str(Path(cfg.out_dir) / "01_foundation" / "seed_ideas.md")
    if arcs_path is None:
        arcs_path = str(Path(cfg.out_dir) / "02_outline" / "character_arcs.md")
    if world_path is None:
        world_path = str(Path(cfg.out_dir) / "04_story_bible" / "world.md")
    if locations_jsonl_path is None:
        locations_jsonl_path = str(Path(cfg.out_dir) / "04_story_bible" / "locations.jsonl")

    plan_path = chapters.run(
        seed_path,
        arcs_path,
        world_path,
        locations_jsonl_path,
        out_dir=_resolve_out_dir(out_dir),
    )
    typer.echo(plan_path)


@app.command()
def scenes_cmd(
    chapter_plan_path: str = typer.Option(None, help="Path to chapter plan markdown."),
    limit: int = typer.Option(3, help="Number of scenes to draft."),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Draft scene cards and prose for the first N chapters."""

    cfg = load_config()
    if chapter_plan_path is None:
        chapter_plan_path = str(Path(cfg.out_dir) / "02_outline" / "chapter_plan.md")

    scenes_written = scenes.run(
        chapter_plan_path,
        out_dir=_resolve_out_dir(out_dir),
        limit=limit,
    )
    typer.echo(json.dumps(scenes_written, indent=2))


@app.command()
def bible_cmd(
    scene_path: str = typer.Option(..., help="Path to a scene draft."),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Append a bible changelog entry from a scene draft."""

    changelog_path = bible.run(scene_path, out_dir=_resolve_out_dir(out_dir))
    typer.echo(changelog_path)


@app.command()
def index_cmd(
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Create the index manifest."""

    index_path = indexer.run(out_dir=_resolve_out_dir(out_dir))
    typer.echo(index_path)


@app.command(context_settings=_EXTRA_SETTINGS)
def run_all_cmd(
    ctx: typer.Context,
    cards: int = typer.Option(3, help="Number of scene cards/drafts to generate."),
    out_dir: str | None = typer.Option(None, help="Override output directory."),
) -> None:
    """Run the entire pipeline end-to-end."""

    constraints = _parse_constraints(list(ctx.args))
    if not constraints:
        raise typer.BadParameter("Provide at least one constraint option like --genre.")

    target_out_dir = _resolve_out_dir(out_dir)
    results = orchestrator.run_all(constraints, cards=cards, out_dir=target_out_dir)

    typer.echo(json.dumps(results, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
