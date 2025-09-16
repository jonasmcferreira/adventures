from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class Config:
    region: str
    profile: str
    model_id: str
    temperature: float
    max_tokens: int
    out_dir: str


_REQUIRED_KEYS = {
    "region",
    "profile",
    "model_id",
    "temperature",
    "max_tokens",
    "out_dir",
}


def _coerce_config(data: dict[str, Any]) -> Config:
    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Missing configuration keys: {missing_str}")

    return Config(
        region=str(data["region"]),
        profile=str(data["profile"]),
        model_id=str(data["model_id"]),
        temperature=float(data["temperature"]),
        max_tokens=int(data["max_tokens"]),
        out_dir=str(data["out_dir"]),
    )


def load_config(path: str | Path = "config.yaml") -> Config:
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a YAML mapping")

    return _coerce_config(data)
