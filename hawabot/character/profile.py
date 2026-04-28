"""Load and validate character profiles (character.yaml)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_DEFAULT_PROFILE = Path(__file__).parent / "profiles" / "default.yaml"


@dataclass
class Keyframe:
    """A single animation keyframe: target joint angles + duration."""

    joints: dict[str, float]
    duration_ms: int


@dataclass
class CharacterProfile:
    name: str
    skeleton: str
    tier: str
    appearance: dict[str, Any]
    joint_overrides: dict[str, Any]
    animations: dict[str, list[Keyframe]]

    @classmethod
    def load(cls, path: str | Path | None = None) -> CharacterProfile:
        """Load a character profile from YAML.

        Resolution order:
        1. Explicit *path* argument
        2. ``HAWABOT_CHARACTER`` environment variable
        3. ``character.yaml`` in the current working directory
        4. Built-in default profile
        """
        if path is None:
            path = os.environ.get("HAWABOT_CHARACTER")
        if path is None:
            cwd_file = Path.cwd() / "character.yaml"
            if cwd_file.exists():
                path = cwd_file
        if path is None:
            path = _DEFAULT_PROFILE

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Character profile not found: {path}")

        with open(path) as f:
            raw: dict[str, Any] = yaml.safe_load(f)

        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> CharacterProfile:
        animations: dict[str, list[Keyframe]] = {}
        for anim_name, frames in (data.get("animations") or {}).items():
            keyframes = []
            for frame in frames:
                keyframes.append(
                    Keyframe(
                        joints=frame.get("joints", {}),
                        duration_ms=frame.get("duration_ms", 300),
                    )
                )
            animations[anim_name] = keyframes

        return cls(
            name=data.get("name", "Unnamed"),
            skeleton=data.get("skeleton", "humanoid"),
            tier=data.get("tier", "spark"),
            appearance=data.get("appearance", {}),
            joint_overrides=data.get("joints") or {},
            animations=animations,
        )
