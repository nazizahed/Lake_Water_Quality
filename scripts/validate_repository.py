"""Lightweight structural validation for the public research repository."""

from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
README = ROOT / "README.md"
EXAMPLE_CSV = ROOT / "data" / "example" / "era5_land_weekly_catchments_2019.csv"
EXPECTED_NOTEBOOKS = [f"{index:02d}_" for index in range(17)]
EXPECTED_COLUMNS = [
    "Lake_ID",
    "year",
    "week",
    "week_start",
    "week_end",
    "lake_layer_temperature",
    "runoff_sum",
    "surface_runoff_sum",
    "air_temperature_2m",
    "total_precipitation_sum",
]


def python_source_for_ast(source: str) -> str:
    """Remove notebook-only line magics before parsing regular Python syntax."""
    return "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith(("%", "!"))
    )


def validate_notebooks() -> list[str]:
    errors: list[str] = []
    paths = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    prefixes = [path.name[:3] for path in paths]

    if len(paths) != 17:
        errors.append(f"Expected 17 notebooks, found {len(paths)}")
    if prefixes != EXPECTED_NOTEBOOKS:
        errors.append("Notebook names must form one ordered 00–16 sequence")

    for path in paths:
        if path.stat().st_size > 1_000_000:
            errors.append(f"{path.relative_to(ROOT)} exceeds 1 MB")
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
            continue

        cells = notebook.get("cells", [])
        if not cells or cells[0].get("cell_type") != "markdown":
            errors.append(f"{path.relative_to(ROOT)} must begin with documentation")
        elif "repository-overview" not in cells[0].get("metadata", {}).get("tags", []):
            errors.append(f"{path.relative_to(ROOT)} is missing its overview tag")
        if (
            len(cells) < 2
            or cells[1].get("cell_type") != "code"
            or "repository-path-setup"
            not in cells[1].get("metadata", {}).get("tags", [])
        ):
            errors.append(f"{path.relative_to(ROOT)} is missing its path setup cell")

        for number, cell in enumerate(cells):
            if cell.get("cell_type") != "code":
                continue
            if cell.get("outputs"):
                errors.append(f"{path.relative_to(ROOT)} cell {number} contains outputs")
            if cell.get("execution_count") is not None:
                errors.append(f"{path.relative_to(ROOT)} cell {number} has an execution count")

            source = python_source_for_ast("".join(cell.get("source", [])))
            if not source.strip():
                continue
            try:
                ast.parse(source)
            except SyntaxError as exc:
                errors.append(
                    f"{path.relative_to(ROOT)} cell {number} has invalid Python: "
                    f"line {exc.lineno}: {exc.msg}"
                )
    return errors


def validate_readme() -> list[str]:
    errors: list[str] = []
    text = README.read_text(encoding="utf-8")
    if text.count("```") % 2:
        errors.append("README.md has an unclosed fenced code block")

    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for target in link_pattern.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean_target = target.split("#", 1)[0]
        if clean_target and not (ROOT / clean_target).exists():
            errors.append(f"README.md links to missing path: {clean_target}")
    return errors


def validate_example_data() -> list[str]:
    errors: list[str] = []
    try:
        with EXAMPLE_CSV.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            first_row = next(reader, None)
    except OSError as exc:
        return [f"Could not read {EXAMPLE_CSV.relative_to(ROOT)}: {exc}"]

    if header != EXPECTED_COLUMNS:
        errors.append(f"Example CSV schema differs: {header}")
    if first_row is None:
        errors.append("Example CSV must contain at least one data row")
    return errors


def main() -> None:
    errors = validate_notebooks() + validate_readme() + validate_example_data()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Repository validation passed")


if __name__ == "__main__":
    main()
