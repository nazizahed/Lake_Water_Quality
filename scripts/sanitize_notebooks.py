"""Apply deterministic, review-friendly cleanup to the research notebooks.

The script deliberately does not execute scientific code. It adds a short
repository overview, clears transient outputs, normalizes metadata, and fixes
the few machine-specific paths and Earth Engine identifiers found in the
historical notebooks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"

NOTEBOOKS = {
    "00_data_coverage_check.ipynb": {
        "title": "Data coverage check",
        "purpose": "Inspect lake identifiers and the availability of water-quality observations.",
        "inputs": "Local CCI Lakes tables under `Datasets/`.",
        "outputs": "Coverage summaries used to select lakes for subsequent processing.",
    },
    "01_lake_catchment_assignment.ipynb": {
        "title": "Lake–catchment assignment",
        "purpose": "Associate lake geometries with HydroBASINS Level 8 catchments.",
        "inputs": "CCI lake geometries and HydroBASINS Level 8 polygons.",
        "outputs": "Lake-to-catchment assignments and mapped geometries.",
    },
    "02_upstream_catchment_extraction.ipynb": {
        "title": "Upstream catchment extraction",
        "purpose": "Trace upstream HydroBASINS units for each selected lake catchment.",
        "inputs": "Lake-to-catchment assignments and HydroBASINS connectivity fields.",
        "outputs": "Aggregated upstream catchment geometries for environmental extraction.",
    },
    "03_era5_land_extraction.ipynb": {
        "title": "ERA5-Land extraction",
        "purpose": "Export weekly climate and hydrological predictors by lake catchment.",
        "inputs": "An Earth Engine catchment asset and ERA5-Land Daily Aggregated.",
        "outputs": "Yearly weekly catchment CSV exports and exploratory diagnostics.",
    },
    "04_firecci_extraction.ipynb": {
        "title": "FireCCI extraction",
        "purpose": "Summarize burned-area observations for lake catchments.",
        "inputs": "Catchment geometries and the FireCCI51 Earth Engine collection.",
        "outputs": "Catchment-level fire-exposure tables.",
    },
    "05_cnr_weekly_aggregation.ipynb": {
        "title": "CNR weekly aggregation",
        "purpose": "Aggregate source lake-quality observations to a weekly time step.",
        "inputs": "Local lake-variable tables supplied for the research analysis.",
        "outputs": "Weekly lake-quality tables.",
    },
    "06_fire_exposure_summary.ipynb": {
        "title": "Fire-exposure summary",
        "purpose": "Identify lakes and periods represented in the fire-exposure extracts.",
        "inputs": "Catchment-level FireCCI summaries.",
        "outputs": "Fire-exposure lookup and summary tables.",
    },
    "07_no_fire_aggregation.ipynb": {
        "title": "No-fire aggregation",
        "purpose": "Build the comparison-lake environmental dataset.",
        "inputs": "Weekly lake-quality, climate, and fire-exposure tables.",
        "outputs": "Merged weekly records for lakes without recorded fire exposure.",
    },
    "08_metadata_aggregation.ipynb": {
        "title": "Metadata aggregation",
        "purpose": "Combine lake metadata used by the downstream analysis.",
        "inputs": "Local lake metadata and intermediate lookup tables.",
        "outputs": "Consolidated metadata tables.",
    },
    "09_time_series_interpolation.ipynb": {
        "title": "Time-series interpolation",
        "purpose": "Merge predictors and interpolate gaps in weekly lake series.",
        "inputs": "Weekly water-quality, ERA5-Land, FireCCI, and metadata tables.",
        "outputs": "Per-lake interpolated weekly time series.",
    },
    "10_select_no_fire_lakes.ipynb": {
        "title": "Select no-fire lakes",
        "purpose": "Select comparison lakes that meet the analysis coverage criteria.",
        "inputs": "Interpolated lake series and fire-exposure summaries.",
        "outputs": "Filtered comparison-lake dataset.",
    },
    "11_select_fire_lakes.ipynb": {
        "title": "Select fire-exposed lakes",
        "purpose": "Select fire-exposed lakes that meet the analysis coverage criteria.",
        "inputs": "Interpolated lake series and fire-exposure summaries.",
        "outputs": "Filtered fire-exposed lake dataset.",
    },
    "12_prepare_no_fire_sequences.ipynb": {
        "title": "Prepare no-fire sequences",
        "purpose": "Transform comparison-lake observations into model-ready sequences.",
        "inputs": "Filtered comparison-lake weekly records.",
        "outputs": "Training, validation, and test arrays for comparison lakes.",
    },
    "13_prepare_fire_sequences.ipynb": {
        "title": "Prepare fire-exposed sequences",
        "purpose": "Transform fire-exposed observations into model-ready sequences.",
        "inputs": "Filtered fire-exposed weekly records.",
        "outputs": "Training, validation, and test arrays for fire-exposed lakes.",
    },
    "14_lstm_with_fire_predictors.ipynb": {
        "title": "LSTM with fire predictors",
        "purpose": "Train and evaluate the historical LSTM configuration containing fire variables.",
        "inputs": "Prepared lake sequences, including fire-related predictors.",
        "outputs": "Saved model artifacts and evaluation diagnostics (not committed in full).",
    },
    "15_lstm_without_fire_predictors.ipynb": {
        "title": "LSTM without fire predictors",
        "purpose": "Train and evaluate the historical baseline LSTM configuration.",
        "inputs": "Prepared lake sequences without fire-related predictors.",
        "outputs": "Saved model artifacts and evaluation diagnostics (not committed in full).",
    },
    "16_visualization.ipynb": {
        "title": "Visualization",
        "purpose": "Create the case-study map and inspect preserved model diagnostics.",
        "inputs": "Lake/catchment geometries and historical evaluation artifacts.",
        "outputs": "Curated figures under `docs/figures/`.",
    },
}


def source_lines(text: str) -> list[str]:
    """Convert text to the line-list representation used by notebook JSON."""
    return text.splitlines(keepends=True)


def overview_cell(details: dict[str, str]) -> dict[str, object]:
    text = (
        f"# {details['title']}\n\n"
        f"**Purpose.** {details['purpose']}\n\n"
        f"**Inputs.** {details['inputs']}\n\n"
        f"**Outputs.** {details['outputs']}\n\n"
        "> Historical research notebook. Paths assume the repository layout described "
        "in `data/README.md`; generated outputs are intentionally not stored in the notebook.\n"
    )
    return {
        "cell_type": "markdown",
        "metadata": {"tags": ["repository-overview"]},
        "source": source_lines(text),
    }


def path_setup_cell() -> dict[str, object]:
    text = (
        "from pathlib import Path\n"
        "import os\n\n"
        "start_dir = Path.cwd().resolve()\n"
        "for candidate in (start_dir, *start_dir.parents):\n"
        "    if (candidate / 'notebooks').is_dir() and (candidate / 'README.md').is_file():\n"
        "        os.chdir(candidate)\n"
        "        break\n"
        "else:\n"
        "    raise RuntimeError('Run this notebook from inside the cloned repository.')\n"
    )
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": ["repository-path-setup"]},
        "outputs": [],
        "source": source_lines(text),
    }


def replace_machine_specific_values(source: str, notebook_name: str) -> str:
    windows_separator = chr(92)
    source = source.replace(
        f"Datasets{windows_separator}ECMWF_raw", "Datasets/ECMWF_raw"
    )
    source = source.replace(
        f"Datasets{windows_separator}Interpolated_Lake_CSVs"
        f"{windows_separator}Lake_27.csv",
        "Datasets/Interpolated_Lake_CSVs/Lake_27.csv",
    )

    if notebook_name in {
        "03_era5_land_extraction.ipynb",
        "04_firecci_extraction.ipynb",
    }:
        if "ee.Authenticate" in source and "ee.Initialize" in source:
            source = (
                "import os\nimport ee\n\n"
                "EE_PROJECT = os.getenv('EE_PROJECT')\n"
                "if not EE_PROJECT:\n"
                "    raise RuntimeError('Set EE_PROJECT before running this notebook.')\n\n"
                "ee.Authenticate(auth_mode='notebook')\n"
                "ee.Initialize(project=EE_PROJECT)\n"
            )
        if re.search(r"^catchments\s*=\s*ee\.FeatureCollection\(", source):
            source = re.sub(
                r"^catchments\s*=\s*ee\.FeatureCollection\([^\n]+\)",
                "EE_CATCHMENTS_ASSET = os.getenv('EE_CATCHMENTS_ASSET')\n"
                "if not EE_CATCHMENTS_ASSET:\n"
                "    raise RuntimeError('Set EE_CATCHMENTS_ASSET before running this notebook.')\n\n"
                "catchments = ee.FeatureCollection(EE_CATCHMENTS_ASSET)",
                source,
                count=1,
                flags=re.MULTILINE,
            )

    if notebook_name == "16_visualization.ipynb":
        source = source.replace(
            'plt.savefig("burned_unburned_lakes_map_with_legend.png", dpi=300)',
            'plt.savefig("docs/figures/burned_unburned_lakes_map.png", dpi=300)',
        )
        source = source.replace(
            'plt.savefig("../docs/figures/burned_unburned_lakes_map.png", dpi=300)',
            'plt.savefig("docs/figures/burned_unburned_lakes_map.png", dpi=300)',
        )

    return source


def sanitize(path: Path, details: dict[str, str]) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = notebook.get("cells", [])

    if (
        cells
        and cells[0].get("cell_type") == "markdown"
        and "repository-overview" in cells[0].get("metadata", {}).get("tags", [])
    ):
        cells[0] = overview_cell(details)
    else:
        cells.insert(0, overview_cell(details))

    if (
        len(cells) > 1
        and cells[1].get("cell_type") == "code"
        and "repository-path-setup" in cells[1].get("metadata", {}).get("tags", [])
    ):
        cells[1] = path_setup_cell()
    else:
        cells.insert(1, path_setup_cell())

    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        cell["execution_count"] = None
        cell["outputs"] = []
        source = "".join(cell.get("source", []))
        source = replace_machine_specific_values(source, path.name)
        cell["source"] = source_lines(source)

    notebook["cells"] = cells
    metadata = notebook.setdefault("metadata", {})
    metadata.pop("widgets", None)
    metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    metadata["language_info"] = {"name": "python", "version": "3"}
    notebook["nbformat"] = 4
    notebook["nbformat_minor"] = 5
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    actual = {path.name for path in NOTEBOOK_DIR.glob("*.ipynb")}
    expected = set(NOTEBOOKS)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise SystemExit(f"Notebook set differs: missing={missing}, unexpected={unexpected}")

    for name, details in NOTEBOOKS.items():
        sanitize(NOTEBOOK_DIR / name, details)
    print(f"Sanitized {len(NOTEBOOKS)} notebooks")


if __name__ == "__main__":
    main()
