#!/usr/bin/env python3
"""Convert a systems CSV file to nested JSON next to the input (same name, .json).

Also writes one folder per system next to that JSON: <id>/input.json (same parent directory).

CLI: python convert_csv.py [csv_path]
IDE: set INPUT_CSV below and run without arguments.
"""

import argparse
import csv
import json
from pathlib import Path

# Used when you run this file from the IDE with no CLI arguments. Override with any path.
INPUT_CSV = Path(__file__).resolve().parent / "improve_entry_model_comparison/handpicked_data.csv"

BRACKET_KEYS = (
    "operatingSystem",
    "operatingSystemVersion",
    "product",
    "description",
    "isSoftware",
    "manufacturer",
    "class",
)


def _unique_fieldnames(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out: list[str] = []
    for name in names:
        n = seen.get(name, 0)
        out.append(name if n == 0 else f"{name}_{n}")
        seen[name] = n + 1
    return out


def _split_bracket_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        return [raw]
    inner = raw[1:-1]
    if not inner:
        # CSV uses [] for "no list" on single-component rows; other columns still have [value].
        return [""]
    return inner.split(",")


def _fit_bracket_parts(parts: list[str], n: int) -> list[str]:
    """Make a comma-split bracket list exactly n segments (pad or merge; handles commas inside values)."""
    if n <= 0:
        return parts
    if len(parts) == n:
        return parts
    if len(parts) < n:
        return parts + [""] * (n - len(parts))
    if n == 1:
        return [",".join(parts)]
    return parts[: n - 1] + [",".join(parts[n - 1 :])]


def _cell_str(raw: str) -> str | None:
    s = raw.strip()
    return None if s == "" else s


def _cell_bool(raw: str) -> bool | None:
    s = raw.strip().lower()
    if s == "true":
        return True
    if s == "false":
        return False
    return None


def _row_to_record(row: dict[str, str]) -> dict:
    lists = {k: _split_bracket_list(row[k]) for k in BRACKET_KEYS}
    n = len(lists["operatingSystem"])
    for k in BRACKET_KEYS:
        lists[k] = _fit_bracket_parts(lists[k], n)

    sys_id = row["id_1"].strip() if "id_1" in row else row["id"].strip()

    components: list[dict] = []
    for i in range(n):
        comp: dict = {
            "description": _cell_str(lists["description"][i]),
            "isSoftware": _cell_bool(lists["isSoftware"][i]),
            "operatingSystem": _cell_str(lists["operatingSystem"][i]),
            "manufacturer": _cell_str(lists["manufacturer"][i]),
            "operatingSystemVersion": _cell_str(lists["operatingSystemVersion"][i]),
            "class": _cell_str(lists["class"][i]),
            "id": sys_id,
            "product": _cell_str(lists["product"][i]),
        }
        components.append(comp)

    return {
        "components": components,
        "id": row["id"].strip(),
        "type": row["type"].strip(),
    }


def _write_per_system_folders(systems: list[dict], json_parent: Path) -> None:
    """Create <id>/input.json under json_parent for each system (id from the system record)."""
    for system in systems:
        sid = str(system["id"])
        folder = json_parent / sid
        folder.mkdir(parents=True, exist_ok=True)
        input_path = folder / "input.json"
        with input_path.open("w", encoding="utf-8") as f:
            json.dump(system, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert systems CSV to nested JSON in the same folder as the CSV.",
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the input .csv file (optional if INPUT_CSV is set in this file)",
    )
    args = parser.parse_args()
    csv_path = args.csv_path if args.csv_path is not None else INPUT_CSV
    csv_path = Path(csv_path).expanduser().resolve()
    if not csv_path.is_file():
        raise SystemExit(f"Not a file: {csv_path}")
    if csv_path.suffix.lower() != ".csv":
        raise SystemExit(f"Expected a .csv file, got: {csv_path}")
    json_path = csv_path.with_suffix(".json")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        fields = _unique_fieldnames(header)
        out = [_row_to_record(dict(zip(fields, row))) for row in reader]

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    _write_per_system_folders(out, json_path.parent)


if __name__ == "__main__":
    main()
