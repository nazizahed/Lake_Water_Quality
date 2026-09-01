# Notebook workflow

The notebooks are ordered by pipeline stage. Stages 10–15 contain parallel
fire-exposed and comparison branches rather than one strictly linear sequence.
All paths are relative to the repository root and expect local inputs under
`Datasets/`.

| Order | Notebook | Purpose | Main output |
| --- | --- | --- | --- |
| 00 | `00_data_coverage_check.ipynb` | Compare lake IDs across polygons, chlorophyll-a, and turbidity files | Coverage diagnostics |
| 01 | `01_lake_catchment_assignment.ipynb` | Match CCI lake polygons to HydroBASINS units | Cleaned lake–catchment layer |
| 02 | `02_upstream_catchment_extraction.ipynb` | Trace and dissolve upstream HydroBASINS units | One upstream catchment per lake |
| 03 | `03_era5_land_extraction.ipynb` | Aggregate ERA5-Land variables by lake catchment and week | Annual climate CSV exports |
| 04 | `04_firecci_extraction.ipynb` | Aggregate FireCCI burned area by catchment | Fire-exposure tables |
| 05 | `05_cnr_weekly_aggregation.ipynb` | Convert CCI lake-variable files to weekly summaries | Weekly CHLA, TURB, and LSWT tables |
| 06 | `06_fire_exposure_summary.ipynb` | Summarise years with recorded fire in each catchment | Lake fire-status table |
| 07 | `07_no_fire_aggregation.ipynb` | Assemble comparison-lake weekly data | No-fire aggregate tables |
| 08 | `08_metadata_aggregation.ipynb` | Combine lake metadata used by later stages | Consolidated metadata |
| 09 | `09_time_series_interpolation.ipynb` | Merge predictors and interpolate weekly gaps | Per-lake modelling tables |
| 10 | `10_select_no_fire_lakes.ipynb` | Select comparison-lake files | No-fire modelling subset |
| 11 | `11_select_fire_lakes.ipynb` | Select fire-exposed lake files | Fire modelling subset |
| 12 | `12_prepare_no_fire_sequences.ipynb` | Construct LSTM windows for comparison lakes | NumPy training/test arrays |
| 13 | `13_prepare_fire_sequences.ipynb` | Construct LSTM windows for fire-exposed lakes | NumPy training/test arrays |
| 14 | `14_lstm_with_fire_predictors.ipynb` | Train the scenario including fire-related predictors | Model checkpoint and diagnostics |
| 15 | `15_lstm_without_fire_predictors.ipynb` | Train the scenario excluding fire-related predictors | Baseline checkpoint and diagnostics |
| 16 | `16_visualization.ipynb` | Produce the case-study map and model plots | Curated figures |

## Running the notebooks

Start Jupyter from the repository root so the relative `Datasets/` paths resolve:

```bash
jupyter lab
```

The Earth Engine notebooks require the `EE_PROJECT` and
`EE_CATCHMENTS_ASSET` environment variables described in the main README.
Large generated arrays, model checkpoints, and source geospatial files are
ignored by Git.

Notebook cell outputs are intentionally cleared before commit. This keeps code
reviewable and prevents machine-specific paths, widget state, and repeated plots
from inflating the repository. Curated historical results remain under
`docs/figures/` and `docs/reports/`.
