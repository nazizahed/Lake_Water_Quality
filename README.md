# Lake Water Quality Catchments Analysis

This project is focused on analyzing lake catchments using Level 8 HydroBASINS data for the Arctic, North America, and South America regions. The goal is to support lake water quality studies by identifying contributing upstream basins and characterizing their spatial extent.

## Project Structure

- `catchment.ipynb` – Main Jupyter Notebook for processing and analysis
- `ar/`, `na/`, `sa/` – Regional HydroBASINS shapefiles (ignored in Git)
- `lakes/` – Selected subset of 2024 CCI Lakes (shapefiles, ignored in Git)
- `.gitignore` – Ensures large data files are excluded from Git tracking

## 📁 Data Files

Large shapefiles (e.g., `.shp`, `.dbf`) are **not included in this repository** due to [GitHub's file size limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

You can access all necessary geospatial data via Google Drive:

👉 [Download data from Google Drive](https://drive.google.com/drive/folders/1enGwJa4e8tolnopZdu0Y0Gw7AAeF3U2s?usp=drive_link)

Please download and place the data in the appropriate subfolders (`ar/`, `na/`, `sa/`, `lakes/`) as expected by the code.

## Why use Google Drive?

- Some shapefiles exceed **100 MB**, which is GitHub’s hard file limit.
- Even Git Large File Storage (LFS) does not support files above this size.
- Google Drive allows for easy, public access without login.

## Getting Started

To run the project:

1. Clone this repository:
   ```bash
   git clone https://github.com/nazizahed/Lake_Water_Quality.git
   cd Lake_Water_Quality
