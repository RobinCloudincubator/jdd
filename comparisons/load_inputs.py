#!/usr/bin/env python3
"""Load each subfolder's input.json into a dict: folder name -> parsed JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_JSON_KW = {"ensure_ascii": False, "indent": 2}


def _comparisons_dir() -> Path:
    return Path(__file__).resolve().parent


def _resolve_experiment_root(root: Path | str | None) -> Path:
    """Relative paths are resolved under the ``comparisons/`` directory (this file's parent)."""
    if root is None:
        return _comparisons_dir()
    p = Path(root).expanduser()
    if not p.is_absolute():
        p = _comparisons_dir() / p
    return p.resolve()


def load_input_json_by_folder(root: Path | str | None = None) -> dict[str, Any]:
    """
    Scan immediate subdirectories of ``root`` for ``input.json`` and return
    ``{ subfolder_name: json.loads(...) }``.

    If ``root`` is a relative path or name, it is resolved under ``comparisons/``
    (the directory containing this module), not the process cwd.
    """
    root = _resolve_experiment_root(root)
    out: dict[str, Any] = {}
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        path = child / "input.json"
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as f:
            out[child.name] = json.load(f)
    return out


def write_left_right_json(
    path: Path | str,
    id: str,
    left: dict[str, Any],
    right: dict[str, Any],
) -> None:
    """
    Write ``left`` and ``right`` as JSON under ``path / id / left.json`` and
    ``right.json``. Creates the subfolder if needed.

    If ``path`` is relative, it is resolved under ``comparisons/`` (same as
    :func:`load_input_json_by_folder`).
    """
    base = _resolve_experiment_root(path)
    folder = base / str(id)
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "left.json").open("w", encoding="utf-8") as f:
        json.dump(left, f, **_JSON_KW)
    with (folder / "right.json").open("w", encoding="utf-8") as f:
        json.dump(right, f, **_JSON_KW)

