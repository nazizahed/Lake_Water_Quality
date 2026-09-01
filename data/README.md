# Data layout

The complete source and derived datasets are too large to distribute in this
repository. Download the public inputs from their official providers and obtain
collaborative inputs through an appropriately authorized project-data channel,
then create the untracked `Datasets/` directory at the repository root.

The historical notebooks expect a layout similar to:

```text
Datasets/
|-- lakes/                         # ESA CCI lake polygons
|-- na/                            # HydroBASINS North America Level 8
|-- CNR/
|   |-- CHLA/                      # Chlorophyll-a per-lake files
|   |-- turbidity/                 # Turbidity per-lake files
|   `-- LSWT/                      # Lake surface-water temperature files
|-- ECMWF_raw/                     # Annual Earth Engine ERA5-Land exports
|-- GEE/                           # FireCCI catchment summaries
|-- final/                         # Lake/catchment vector outputs
|-- Interpolated_Lake_CSVs/        # Harmonised per-lake weekly tables
|-- LSTM2_Fire/                    # Generated fire-scenario arrays
|-- LSTM2_NoFire/                  # Generated comparison arrays
`-- LSTM_Combined/                 # Generated checkpoints and scalers
```

Folder names reflect the historical workflow and are retained to avoid silently
changing notebook behaviour.

## Included example

`example/era5_land_weekly_catchments_2019.csv` is a representative derived
ERA5-Land export with 24,698 weekly catchment records. It is included for schema
inspection and repository validation, not as a complete analysis dataset.

Expected columns:

- `Lake_ID`, `year`, `week`, `week_start`, `week_end`
- `lake_layer_temperature`, `air_temperature_2m`
- `runoff_sum`, `surface_runoff_sum`, `total_precipitation_sum`

## Data governance

Respect the licences, citation requirements, and redistribution terms of each
upstream source. Generated model files (`.pth`, `.npy`, `.pkl`, `.joblib`) and
large geospatial files are ignored by Git to avoid accidental publication.
