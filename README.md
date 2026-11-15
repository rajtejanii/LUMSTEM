# LUMSTEM // Multi-Modal Planetary Analog Engine

**NASA Space Apps Challenge 2026 — Permanent Moon Base Locations & Mars Landing Sites**

**LUMSTEM** (*Lunar & Martian Surface To Earth Mapping*) is a physics-informed, multi-modal planetary analog discovery engine. Rather than matching sites purely by visual appearance, LUMSTEM evaluates **320 terrestrial micro-tiles (7.68 × 7.68 km, 58.98 km² each)** across **15 global geological regions** against **6 official NASA Moon and Mars reference sites** across **5 orthogonal physical dimensions**, while explicitly diagnosing where each terrestrial analogy succeeds and where it breaks down due to gravity, atmospheric buffering, and hydrology.

---

## Instant Start for Judges (Zero External Downloads Required)

All pre-computed NASA/ESA similarity scores and metadata (`data/tiles/metadata.csv`, `data/scores/vision.csv`, `data/scores/scalar.csv`, and the compiled frontend bundle `web/data.js`) are included directly in this repository so the application runs immediately.

### Option A: One-Click Windows Launcher (`run_lumstem.bat`)
1. Double-click **`run_lumstem.bat`** in the project root directory.
2. The script automatically verifies `web/data.js` (or creates a `.venv` and compiles the CSVs via `build_web_data.py` if needed), launches a local web server on port `8080`, and opens **`http://localhost:8080`** in your browser.

### Option B: Cross-Platform Terminal Launch (Windows / macOS / Linux)
```bash
python -m http.server 8080 --directory web
```
Then open **`http://localhost:8080`** in your browser (or open `web/index.html` directly).

---

## Official NASA & Partner Space Agency Data Sources

Every parameter in LUMSTEM is derived from official NASA Planetary Data System (PDS), NASA Earthdata (`earthaccess`), and ESA Copernicus datasets:

| Physical Parameter | Moon & Mars Target Source | Earth Analog Source (30 m Resolution) |
| :--- | :--- | :--- |
| **1. 2D Geomorphology (`vision_score`)** | **NASA LRO LOLA** (59.2 m & 118 m) and **NASA MGS MOLA / ESA HRSC** (200 m) 3D elevation tensors embedded via **Meta DINOv2 ViT** (`dinov2_vits14`). | **ESA Copernicus GLO-30 DEM** (`cop-dem-glo-30`) 256 × 256 elevation tensors embedded via **DINOv2** cosine similarity. |
| **2. Steepness / 3D Slope (`slope_score`)** | True physical surface gradient ($\arctan\|\nabla z\|$) computed at exact orbital pixel spacing (`res_m`). | True physical mean slope (degrees) at 30.0 m pixel spacing. |
| **3. Terrain Ruggedness (`roughness_score`)** | Scale-normalized standard deviation of local slope gradient ($\text{std}(\|\nabla z\|) \times 100$), capturing second-order surface curvature without false positives on smooth ramps. | Scale-normalized local slope gradient variation across each 58.98 km² tile. |
| **4. Thermal & 3D Illumination (`temp_swing_score`)** | **NASA LRO Diviner** & **Mars Odyssey THEMIS / Mars 2020 MEDA** diurnal/shadow temperature swings ($\Delta T$) paired with 3D Lambertian solar incidence ($\cos i$). | **NASA MODIS (`MOD11A1`)** diurnal land-surface temperature baseline modulated by 3D topographic shadow contrast and elevation lapse rate (-6.5 K/km). |
| **5. Surface Material (`lithology_score`)** | **NASA LRO Diviner / M3 & Mars TES / CRISM** published mafic-silicate geochemical indices (`0.65` to `0.95`). | **NASA ASTER TIR / USGS** mafic-silicate bedrock indices (`0.15` evaporite to `0.96` basalt) modulated by 30 m slope bedrock exposure. |

---

## Planetary Reference Targets (3 Moon + 3 Mars)

### Moon (Artemis & Apollo Reference Sites)
1. **Shackleton Crater Rim (`89.9°S`, NASA LRO LOLA 118 m/px):** Illuminated polar ridge receiving near-continuous grazing sunlight (1.5° solar elevation) adjacent to cryogenic shadows ($\Delta T = 185\text{ K}$).
2. **Shackleton PSR Floor (`89.9°S`, NASA LRO LOLA 118 m/px):** Permanently Shadowed Region interior floor (~40–75 K, $\Delta T = 35\text{ K}$) trapping water-ice volatiles in anorthositic regolith.
3. **Apollo 15 Hadley Rille (`26.13°N, 3.63°E`, LRO LOLA + Kaguya 59.2 m/px):** Sinuous volcanic lava channel cut into high-$\text{FeO}/\text{TiO}_2$ tholeiitic mare basalt ($\Delta T = 140\text{ K}$).

### Mars (Rover & Human Exploration Reference Sites)
4. **Jezero Crater Delta (`18.44°N, 77.45°E`, MGS MOLA / HRSC 200 m/px):** Mars 2020 Perseverance landing site; ancient fluvio-lacustrine delta rich in Fe/Mg-smectite clays and carbonates ($\Delta T = 65\text{ K}$).
5. **Valles Marineris — Coprates Chasma (`13.50°S, 61.00°W`, MGS MOLA / HRSC 200 m/px):** Steep tectonic canyon escarpment exposing layered flood basalt and sulfate bedrock ($\Delta T = 75\text{ K}$).
6. **Arsia Mons (`9.20°S, 120.50°W`, MGS MOLA / HRSC 200 m/px):** Tharsis shield volcano flank featuring basaltic lava flows and collapse skylight pits for radiation-shielded habitats ($\Delta T = 85\text{ K}$).

---

## Mission Control Interface Features (`web/index.html`)

* **Celestial Body & Target Switcher:** Toggle between **Moon** and **Mars** and select any of the 6 reference landing sites with adaptive frosted-glass telemetry styling.
* **Mission Presets & Real-Time Similarity Sliders:**
  * **Rover Nav (`0.40, 0.30, 0.20, 0.05, 0.05`):** Prioritizes 2D landform geometry, slope, and ruggedness for autonomous path-planning and wheel traction.
  * **ISRU Drill (`0.10, 0.25, 0.10, 0.20, 0.35`):** Prioritizes mafic-silicate lithology, rig-leveling slope, and thermal regime for volatile extraction and rock drilling.
  * **Habitat Landing (`0.20, 0.30, 0.30, 0.10, 0.10`):** Prioritizes low slope and low surface roughness for lander touchdown stability.
* **Discovery Mode (Unrecognized Sites):** Filters out well-known NASA benchmarks (*Atacama, Askja, Devon Island, El Pinacate, Kilauea, McMurdo, Wadi Rum*) to surface under-utilized planetary analogs (*Tibesti Calderas, Harrat Khaybar, Qaidam Basin, Dasht-e Lut, Danakil Depression, Salar de Arizaro, Makgadikgadi, Namib*).
* **Synchronized Satellite Map, Analog Dossier & Leaderboard:** Clicking any marker on the Esri World Imagery satellite map or any row in the Top 10 Regional Leaderboard smoothly flies to the site and updates the right-hand **Analog Dossier** (displaying parameter breakdown bars, geological rationale, lithology, ice/water state, and physical breakdown constraints).

---

## Full Backend Pipeline Architecture (Reproducibility)

If you wish to re-run the entire data ingestion, AI vision embedding, and physical scoring pipeline from scratch:

```bash
pip install -r requirements.txt
python -m src.step0_fetch_nasa_targets   # Streams NASA PDS LRO LOLA & Mars MOLA/HRSC GeoTIFFs -> data/raw/
python -m src.step1_ingest_tile          # Streams ESA Copernicus 30m DEM & NASA MODIS thermal -> data/tiles/
python -m src.step2_vision               # Extracts DINOv2 ViT embeddings -> data/scores/vision.csv
python -m src.step3_scalar               # Computes 3D slope, roughness, dT & lithology -> data/scores/scalar.csv
python build_web_data.py                 # Compiles CSVs into web/data.js for the Mission Control frontend
```