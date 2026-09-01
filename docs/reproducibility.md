# Reproducibility guide

## What is reproducible from this repository

- The complete notebook code and its intended execution order are visible.
- Relative paths and required input folders are documented.
- A representative ERA5-Land table supports schema and integration checks.
- Repository CI verifies notebook JSON integrity, cleared outputs, Python syntax,
  documentation links, and the example-table schema.
- Curated historical figures and reports make the recorded outputs inspectable.

## What requires external state

- ESA CCI Lakes files, HydroBASINS vectors, and the full CNR lake-variable
  collection are not committed.
- Earth Engine extraction requires an authenticated account, a Google Cloud
  project, and a catchment FeatureCollection supplied through
  `EE_CATCHMENTS_ASSET`.
- Several stages submit asynchronous Earth Engine export tasks to Google Drive.
- LSTM training requires generated NumPy arrays and produces checkpoints that
  are intentionally ignored by Git.

## Known historical limitations

- The model experiments did not preserve a fully locked software environment.
- Random seeds were not consistently recorded in the original modelling cells.
- Some reports and figures were generated during iterative development, so
  naming from the original scenarios is retained in figure titles.
- No complete end-to-end rerun was performed during the 2026 repository cleanup.

## Validation

Run the lightweight repository checks without installing geospatial or ML
dependencies:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

To execute the research workflow itself, install `requirements.txt`, prepare
the external data tree, configure Earth Engine, and run the notebooks in order.
