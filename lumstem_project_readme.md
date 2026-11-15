# 🪐 LUMSTEM // Multi-Modal Planetary Analog Engine

**2026 NASA Space Apps Challenge — Permanent Moon Base Locations & Mars Landing Sites**

**LUMSTEM** (*Lunar & Martian Surface To Earth Mapping*) is a physics-informed, multi-modal planetary analog discovery engine and interactive 3D Mission Control application. Rather than matching terrestrial testbeds purely by subjective visual appearance, LUMSTEM quantitatively evaluates **320 terrestrial micro-tiles ($7.68 \times 7.68\text{ km}$, $58.98\text{ km}^2$ each)** across **15 global geological regions** against **6 official NASA Moon and Mars reference landing sites** across **5 orthogonal physical dimensions**, while explicitly diagnosing where each terrestrial analogy breaks down due to gravity, atmospheric thermal buffering, and hydrology.

---

## 🎬 Project Demonstration (In-Repository)

Our official 30-second project demonstration and interface preview are included directly in this repository:

* **📹 Video Demonstration ($\le 30\text{s}$):** [Watch / Download Project Demo Video (`demo.mp4`)](./demo.mp4) *(or view our presentation slides if included in the root folder)*
* **🖥️ Mission Control Interface Preview:**
  ![LUMSTEM Mission Control Interface](./web/preview.png)
  *(Note: If your demo video or screenshot has a different filename in the root directory, update the relative link above before committing.)*

---

## ⚡ Quick Start (Clone & Launch in 10 Seconds)

All **1,920 pre-computed tile-target evaluations** (`320` Earth tiles $\times$ `6` planetary targets) are bundled directly in this repository (`data/tiles/metadata.csv`, `data/scores/vision.csv`, `data/scores/scalar.csv`, and `web/data.js`). **Zero external gigabyte downloads or API keys are required to run the Mission Control web app.**

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR-GITHUB-USERNAME>/<YOUR-REPO-NAME>.git
cd <YOUR-REPO-NAME>
```

### 2. Launch the Mission Control Web Application

#### **Option A: Cross-Platform Terminal Launch (Windows / macOS / Linux — Recommended)**
Using standard Python 3 (zero package installations required):
```bash
python -m http.server 8080 --directory web
```
Then open **[`http://localhost:8080`](http://localhost:8080)** in your browser (or open `web/index.html` directly in any modern browser).

#### **Option B: One-Click Windows Launcher (`run_lumstem.bat`)**
Double-click **`run_lumstem.bat`** in the root folder. It automatically detects `web/data.js`, starts the local server on port `8080`, and opens `http://localhost:8080` in your browser (or press `R` during the 2-second startup window to rebuild `web/data.js` from the CSVs).

#### **Option C: Streamlit Scientific Telemetry Dashboard (`app.py`)**
If you also want to explore our secondary Python/Plotly analytical dashboard:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📂 Repository Folder Structure

```text
LUMSTEM/
├── README.md                        # Project documentation, physics formulas & citations
├── requirements.txt                 # Python dependencies for backend pipeline & Streamlit app
├── config.py                        # Definitions for 6 NASA targets & 15 Earth analog regions
├── build_web_data.py                # Compiler that merges CSVs & DEM grids into web/data.js
├── run_lumstem.bat                  # One-click Windows launcher (Quick Launch + Dev Rebuild)
├── app.py                           # Secondary Streamlit / Plotly scientific telemetry app
├── web/                             # Primary Standalone Mission Control Web Application
│   ├── index.html                   # 3D Three.js Globe, Leaflet Map, Dossier & Radar UI
│   └── data.js                      # Pre-compiled offline JSON bundle (1,920 tile-target records)
├── src/                             # Reproducible 5-Step Backend Ingestion & AI Pipeline
│   ├── step0_fetch_nasa_targets.py  # Streams NASA LRO LOLA & MGS MOLA/HRSC GeoTIFF windows
│   ├── step1_ingest_tile.py         # Streams ESA Copernicus 30m DEMs & computes 3D illumination
│   ├── step2_vision.py              # Extracts 384-d Meta DINOv2 ViT geomorphology embeddings
│   ├── step3_scalar.py              # Computes physical 3D slope, ruggedness, ΔT & lithology
│   └── step4_fusion.py              # Dynamic multi-modal weight fusion & Discovery Mode filter
└── data/
    ├── raw/                         # Raw 512×512 NASA planetary orbital GeoTIFFs (step0)
    ├── tiles/
    │   ├── metadata.csv             # Geographic bounds, lat/lon centers & precip for 320 tiles
    │   └── *.npz                    # Compressed 256×256 float32 DEM, thermal & illumination arrays
    └── scores/
        ├── vision.csv               # DINOv2 cosine similarity scores (0–100%) per target
        └── scalar.csv               # Raw physical metrics & normalized scores per target
```

---

## 🏗️ System Architecture & 5-Step Pipeline

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                     1. ORBITAL DATA INGESTION (step0 & step1)                │
│  • Moon/Mars: NASA PDS LRO LOLA (59.2m/118m) & MGS MOLA / ESA HRSC (200m)    │
│  • Earth: ESA Copernicus GLO-30 (30m STAC) + NASA MODIS MOD11A1 (earthaccess)│
│  • Slicing: 15 Regions (0.4°×0.4° bboxes) -> 320 Non-Overlapping 256×256 Tiles│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│            2. MULTI-MODAL FEATURE EXTRACTION (step2 & step3)                 │
│  ┌───────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │ AI Vision Pipeline (step2_vision) │  │ Physical Pipeline (step3_scalar) │ │
│  │ • Meta DINOv2 ViT (dinov2_vits14) │  │ • True 3D Slope (arctan ||∇z||)  │ │
│  │ • 384-D Structural Embeddings     │  │ • Ruggedness (std(||∇z||) × 100) │ │
│  │ • Cosine Similarity -> P5/P95 Norm│  │ • 3D Lambertian Illum & ΔT Swing │ │
│  └─────────────────┬─────────────────┘  │ • Mafic-Silicate Lithology Index │ │
│                    │                    └─────────────────┬────────────────┘ │
└────────────────────┼──────────────────────────────────────┼──────────────────┘
                     ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               3. PRE-COMPUTED DATA BUNDLE (build_web_data.py)                │
│  • Merges metadata.csv + vision.csv + scalar.csv -> web/data.js (1,920 rows) │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               4. MISSION CONTROL FRONTEND (web/index.html)                   │
│  • Interactive 3D Moon/Mars Globe (Three.js) + Global Satellite Map (Leaflet)│
│  • Real-Time Weight Fusion + Discovery Mode + Explainable Similarity Radar   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Why Exactly 320 Terrestrial Micro-Tiles?
Each of the **15 Earth analog regions** in `config.py` spans a **$0.4^\circ \times 0.4^\circ$ latitude/longitude bounding box** sliced into non-overlapping **$256 \times 256\text{ pixel}$ tiles** ($7.68 \times 7.68\text{ km} = 58.98\text{ km}^2$ at $30\text{ m}$ spacing):
* **12 Low/Mid-Latitude Regions ($1^\prime\prime \times 1^\prime\prime$ native DEM grid):** $0.4^\circ \times 3600\text{ px/deg} = 1440 \times 1440\text{ px} \rightarrow \lfloor 1440/256 \rfloor = 5 \times 5 = \mathbf{25\text{ tiles/region}}$ ($12 \times 25 = 300\text{ tiles}$).
* **1 Sub-Arctic Region (`Askja, Iceland` at $65.2^\circ\text{N}$, $1^\prime\prime \times 2^\prime\prime$ grid due to meridian convergence):** $1440 \times 720\text{ px} \rightarrow 5 \times 2 = \mathbf{10\text{ tiles}}$.
* **2 High-Polar Regions (`Devon Island` at $75.4^\circ\text{N}$ & `McMurdo, Antarctica` at $77.4^\circ\text{S}$, $1^\prime\prime \times 3^\prime\prime$ grid):** $1440 \times 480\text{ px} \rightarrow 5 \times 1 = \mathbf{5\text{ tiles/region}}$ ($2 \times 5 = 10\text{ tiles}$).
* **Total:** $300 + 10 + 10 = \mathbf{320\text{ unique Earth micro-tiles}} \times 6\text{ planetary targets} = \mathbf{1,920\text{ evaluations}}$.

---

## 🔬 Scientific Methodology & 5 Physical Parameters

| Parameter | Mathematical Formulation | Planetary Target Source | Terrestrial Analog Source |
| :--- | :--- | :--- | :--- |
| **1. Geomorphology (`vision_score`)** | Cosine similarity $\frac{\mathbf{e}_{\text{Earth}} \cdot \mathbf{e}_{\text{Target}}}{\|\mathbf{e}_{\text{Earth}}\| \|\mathbf{e}_{\text{Target}}\|}$ of 384-D **DINOv2 ViT** (`dinov2_vits14`) embeddings extracted from min-max normalized elevation rasters, scaled via 5th–95th percentile clamping. | **NASA LRO LOLA** ($59.2\text{ m}$ & $118\text{ m}$) and **NASA MGS MOLA / ESA HRSC** ($200\text{ m}$) DEMs. | **ESA Copernicus GLO-30** ($30\text{ m}$) DEMs. |
| **2. 3D Slope (`slope_score`)** | True physical mean inclination: $$\bar{\theta} = \frac{1}{N}\sum \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \cdot \frac{180}{\pi}$$ where derivatives are divided by exact pixel spacing `res_m`. | Computed at exact orbital resolution ($59.2\text{ m}$, $118\text{ m}$, or $200\text{ m}$). | Computed at $30.0\text{ m}$ pixel spacing. |
| **3. Roughness (`roughness_score`)** | Scale-normalized standard deviation of local gradient magnitude: $$R = \text{std}\left(\sqrt{(\partial_x z)^2 + (\partial_y z)^2}\right) \times 100$$ Avoids false roughness spikes on smooth tilted ramps. | Second-order surface curvature across target DEM. | Second-order surface curvature across $58.98\text{ km}^2$ tile. |
| **4. Thermal & Illumination (`temp_swing_score`)** | 3D Lambertian solar incidence: $$\cos i = \cos\theta_z \cos\theta_s + \sin\theta_z \sin\theta_s \cos(\phi_s - \alpha)$$ Modulates diurnal $\Delta T$ with topographic shadow depth and elevation lapse rate ($-6.5\text{ K/km}$). | **NASA LRO Diviner** & **Mars THEMIS / MEDA** $\Delta T$ ($35\text{ K}$ to $185\text{ K}$) at site solar grazing angle. | **NASA MODIS (`MOD11A1`)** diurnal baseline modulated by 3D shadow contrast. |
| **5. Lithology (`lithology_score`)** | Mafic-silicate geochemical index $M \in [0, 1]$ modulated by steep-slope bedrock exposure: $$M_{\text{tile}} = \text{clip}\left(M_{\text{base}} + 0.03 \cdot \frac{\bar{\theta}}{15^\circ},\, 0,\, 1\right)$$ | **LRO Diviner / M3 & Mars TES / CRISM** mafic indices ($0.65$ smectite to $0.95$ mare basalt). | **NASA ASTER TIR / USGS** bedrock indices ($0.15$ evaporite to $0.96$ picrite-basalt). |

---

## 🎯 Official NASA Reference Landing Sites (3 Moon + 3 Mars)

1. **🌕 Moon — Shackleton Crater Rim (`89.9°S, 0.0°E`, LRO LOLA 118 m/px):** Artemis III candidate polar ridge receiving near-continuous grazing sunlight ($1.5^\circ$ horizon angle) adjacent to cryogenic shadows ($\Delta T = 185\text{ K}$, Anorthositic Highland Breccia, $0.165g$).
2. **🌕 Moon — Shackleton PSR Floor (`89.9°S`, LRO LOLA 118 m/px, 15.1 km offset):** Permanently Shadowed Region interior floor ($\sim 40\text{–}75\text{ K}$, $\Delta T = 35\text{ K}$) cold-trapping water-ice volatiles in anorthositic regolith ($0.165g$).
3. **🌕 Moon — Apollo 15 Hadley Rille (`26.13°N, 3.63°E`, LRO LOLA + Kaguya 59.2 m/px):** Sinuous volcanic lava channel cut into high-$\text{FeO}/\text{TiO}_2$ tholeiitic mare basalt ($\Delta T = 140\text{ K}$, Mafic Index $0.95$, $0.165g$).
4. **🔴 Mars — Jezero Crater Delta (`18.44°N, 77.45°E`, MGS MOLA / HRSC 200 m/px):** Mars 2020 Perseverance landing site; ancient fluvio-lacustrine delta fan rich in $\text{Fe/Mg}$-smectite clays and carbonates ($\Delta T = 65\text{ K}$, Mafic Index $0.65$, $0.38g$).
5. **🔴 Mars — Valles Marineris, Coprates Chasma (`13.50°S, 61.00°W`, MGS MOLA / HRSC 200 m/px):** Steep tectonic canyon fault escarpment exposing kilometers of layered flood basalt and sulfate bedrock ($\Delta T = 75\text{ K}$, Mafic Index $0.84$, $0.38g$).
6. **🔴 Mars — Arsia Mons (`9.20°S, 120.50°W`, MGS MOLA / HRSC 200 m/px):** Southernmost Tharsis shield volcano flank hosting high-altitude basaltic lava tubes and collapse skylights for radiation-shielded habitats ($\Delta T = 85\text{ K}$, Mafic Index $0.92$, $0.38g$).

---

## 🖥️ Mission Control Interface Features (`web/index.html`)

* **Interactive 3D Planetary Globe (Three.js):** Orbit and zoom 3D Moon and Mars globes with surface-locked landing site pins, automatic camera fly-to animations, and collision-free callout labels.
* **Real-Time Similarity Weight Sliders & Info Popovers (`ⓘ`):** Adjust priority weights (`0.00` to `1.00`) across all 5 physical parameters, with hover/click popovers explaining the physical meaning and operational impact of each metric.
* **Discovery Mode (Novel Testbeds):** Filters out 7 well-known NASA training benchmarks (*Atacama, Askja, Devon Island, El Pinacate, Kilauea, McMurdo, Wadi Rum*) to surface 8 under-utilized planetary analog regions (*Tibesti Calderas, Harrat Khaybar, Qaidam Basin, Dasht-e Lut, Danakil Depression, Salar de Arizaro, Makgadikgadi, Namib*).
* **Synchronized Satellite Map, Analog Dossier & Leaderboard:** Clicking any marker on the bounded Esri World Imagery map or any row in the Top 10 Regional Leaderboard flies to the site and updates the **Analog Dossier** (geological rationale, lithology, ice/water regime, and physical breakdown warnings).
* **Explainable Similarity Analysis Radar Graph:** Overlays the user's **Target Mission Profile** (solid polygon) against the **Candidate Earth Site's** real similarity scores (diagonal hatched polygon) and highlights the **Verified Overlap Core** (bright white intersection where the candidate site satisfies mission weights).

---

## 🛠️ Re-Running the Full Backend Pipeline from Scratch (Optional)

If you want to re-stream the raw orbital GeoTIFFs from NASA PDS and ESA Copernicus and recompute all embeddings and scores:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Execute the 5-step ingestion, AI vision & physical scoring pipeline
python -m src.step0_fetch_nasa_targets   # Streams 512×512 NASA LOLA & MOLA/HRSC GeoTIFFs -> data/raw/
python -m src.step1_ingest_tile          # Streams ESA Copernicus 30m DEMs & MODIS thermal -> data/tiles/
python -m src.step2_vision               # Extracts DINOv2 ViT embeddings -> data/scores/vision.csv
python -m src.step3_scalar               # Computes 3D slope, roughness, ΔT & lithology -> data/scores/scalar.csv
python build_web_data.py                 # Compiles CSVs & DEM grids into web/data.js
```

---

## 🤖 Super Intelligence (SI) & AI Tool Disclosure

In full compliance with the **2026 NASA Space Apps Challenge** rules regarding Super Intelligence (SI) tools:
1. **Vision Transformer Embeddings (`src/step2_vision.py`):** Uses the open-source pre-trained **Meta DINOv2 Vision Transformer (`dinov2_vits14`)** via PyTorch Hub to compute 2D geomorphological similarity embeddings from normalized DEM tensors.
2. **Code & Documentation Assistance:** Large Language Model (LLM) assistance (**Google Gemini**) was used to accelerate frontend HTML/CSS/JavaScript layout structuring, SVG radar chart rendering, and documentation formatting. All physical equations, dataset coordinates, and geological rationales were authored and verified by the team.
3. **Demo Video Audio:** The 30-second demonstration video narration was generated via AI text-to-speech synthesis (**ElevenLabs**) and includes a visible SI watermark on the video.
4. **Zero NASA Branding:** No NASA logos, flags, or mission insignias are used in any SI-assisted code, UI, or media assets.

---

## 📚 Data & Open-Source Resource Citations

* **NASA Planetary Data System (PDS) & USGS Astrogeology:**
  * Lunar Orbiter Laser Altimeter (`LRO LOLA` Global 118 m DEM & `LRO LOLA / JAXA SELENE Kaguya` Merged 59 m DEM).
  * Mars Global Surveyor (`MGS MOLA`) & ESA Mars Express (`HRSC`) Blended 200 m Global DEM.
  * Published thermal and geochemical baselines from `LRO Diviner`, `Mars Odyssey THEMIS`, and `Mars 2020 MEDA`.
* **NASA Earthdata (`earthaccess`):**
  * `MODIS MOD11A1` Land Surface Temperature/Emissivity & `ASTER` Global Emissivity Geochemical Baselines.
* **Space Agency Partner Data:**
  * **ESA Copernicus Global DEM (`cop-dem-glo-30`, 30 m)** accessed via Element84 Earth Search STAC API on AWS Registry of Open Data.
* **Open-Source Software & Visual Assets:**
  * **Meta AI DINOv2** (`facebookresearch/dinov2`, Apache-2.0 License), **PyTorch**, **Rasterio**, **NumPy**, **Pandas**, **SciPy**.
  * **Three.js** (`r128`, MIT License), **Leaflet.js** (`1.9.4`, BSD-2-Clause License), **Tailwind CSS** (MIT License), **Esri World Imagery** basemap tiles.
  * **Planetary Surface Textures:** SolarSystemScope 2K Moon & Mars Equirectangular Textures (CC BY 4.0) and Wikimedia Commons public-domain orbital mosaics (`FullMoon2010.jpg`, ESA Rosetta `OSIRIS_Mars_true_color.jpg`).