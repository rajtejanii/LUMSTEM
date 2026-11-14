# LUMSTEM: Multi-Modal Planetary Twin Engine
**NASA Space Apps Challenge**

LUMSTEM is a high-performance, Late-Fusion search engine designed to discover Earth-based geological analogs for lunar and Martian exploration sites.

Instead of merely searching for terrain that visually resembles the Moon or Mars, this pipeline structurally and physically evaluates candidate sites using **Meta AI's DINOv2 Vision Transformers** for 2D geomorphology and **NumPy-based Scalar Physics** for 3D terrain constraints (slope, surface roughness, and extensible thermal/mineral metrics).

## Key Features
* **100% Real Space Agency Data:** Streams ESA Copernicus GLO-30 (Earth) and NASA PDS LRO LOLA / MGS MOLA (Moon and Mars) orbital altimeter data directly via HTTP range requests.
* **AI Geomorphology Vision:** Uses `dinov2_vits14` to extract high-dimensional semantic embeddings of terrain structures (crater rims, rilles, basins, and yardangs).
* **Scalar Physics Engine:** Computes true physical slope (in degrees) and elevation roughness directly from Digital Elevation Model (DEM) matrices to enforce engineering constraints.
* **Discovery Mode:** Includes a dashboard filter that hides well-known NASA test sites (such as the Atacama Desert or Devon Island) to uncover novel, unrecognized planetary analogs across remote global regions.
* **Mission Presets:** Interactive Streamlit dashboard allowing mission planners to snap scoring weights to specific operational profiles (Rover Navigation, ISRU Drilling, and Habitat Landing).

---

## Prerequisites
* **OS:** Linux (Ubuntu recommended) or Windows (WSL2)
* **Hardware:** NVIDIA GPU with CUDA support recommended for batched DINOv2 inference
* **Python:** 3.10+
* **Environment Manager:** Miniconda or Anaconda

---

## Installation and Setup

**1. Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/lumstem_analog_search.git
cd lumstem_analog_search
```

**2. Create a clean Conda environment**
```bash
conda create -n lumstem python=3.10 -y
conda activate lumstem
```

**3. Install PyTorch with CUDA 12.1**
We install the official pip wheels to prevent Intel MKL symbol conflicts common in Conda PyTorch builds on Ubuntu:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install sympy mpmath
```

**4. Install geospatial and dashboard dependencies**
```bash
pip install -r requirements.txt
```

---

## Pipeline Usage

The backend runs as an offline 4-step pipeline so satellite datasets are cached locally as compressed NumPy arrays (`.npz`) and lightweight score tables (`.csv`). Run the modules sequentially from the project root:

### Step 0: Fetch NASA Planetary Target Baselines
Streams real 512x512 pixel elevation crops for Shackleton Crater (Moon), Apollo 15 Hadley Rille (Moon), and Jezero Crater (Mars) from the NASA PDS / USGS Astrogeology archive into `data/raw/`:
```bash
python -m src.step0_fetch_nasa_targets
```

### Step 1: Ingest and Slice Earth Regions
Queries the Element 84 STAC API for ESA Copernicus GLO-30 DEM tiles across all 15 global macro-regions, slicing them into 256x256 pixel tiles (7.68 km x 7.68 km):
```bash
python -m src.step1_ingest_tile
```

### Step 2: Run DINOv2 Vision Inference
Loads the DINOv2 Vision Transformer on your GPU, computes cosine similarity between Earth tiles and planetary targets, and writes `data/scores/vision.csv`:
```bash
python -m src.step2_vision
```

### Step 3: Run Scalar Physics Extraction
Calculates physical slope and roughness metrics across all tiles, normalizes them against the planetary targets, and writes `data/scores/scalar.csv`:
```bash
python -m src.step3_scalar
```

---

## Launching the Dashboard

Once `metadata.csv`, `vision.csv`, and `scalar.csv` are generated, start the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## Project Structure

```text
lumstem_analog_search/
├── app.py                         # Interactive Streamlit dashboard UI
├── config.py                      # Planetary target coordinates, Earth bounding boxes, and parameters
├── requirements.txt               # Python package dependencies
├── README.md                      # Project documentation
├── data/
│   ├── raw/                       # Downloaded NASA GeoTIFF target files (Git-ignored)
│   ├── tiles/                     # Sliced .npz terrain arrays (Git-ignored) and metadata.csv
│   └── scores/                    # Generated vision.csv and scalar.csv
└── src/
    ├── __init__.py
    ├── step0_fetch_nasa_targets.py # NASA PDS / USGS planetary DEM downloader
    ├── step1_ingest_tile.py        # ESA Copernicus STAC streamer and tiler
    ├── step2_vision.py             # Batched PyTorch DINOv2 similarity pipeline
    ├── step3_scalar.py             # NumPy terrain physics and normalization
    └── step4_fusion.py             # Late-fusion Pandas merge and weighted ranking
```

---

## Acknowledgements
* NASA Planetary Data System (PDS) & USGS Astrogeology Science Center
* ESA Copernicus GLO-30 Digital Elevation Model
* Meta AI Research (DINOv2)
* NASA Space Apps Challenge