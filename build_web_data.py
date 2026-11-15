# build_web_data.py
import os
import json
import numpy as np
import pandas as pd
from config import TARGETS, EARTH_REGIONS

os.makedirs("web", exist_ok=True)

REGION_META = {r["region_id"]: r for r in EARTH_REGIONS}

REGION_NOTES = {
    "atacama_01": {
        "why_chosen": "Hyper-arid core (<15 mm/yr rain) with perchlorate/sulfate soil chemistry and active aeolian dust transport matching Martian basins.",
        "ice_water": "Anhydrous surface crust; trace hygroscopic deliquescence in halite nodules.",
        "process": "Aeolian saltation, thermal stress fracturing, and UV photochemical oxidation."
    },
    "askja_01": {
        "why_chosen": "Historic 1965–1967 NASA Apollo astronaut geological training ground; bimodal basaltic lava flows, tephra craters, and volcanic rilles.",
        "ice_water": "Seasonal snowpack and sub-arctic glaciovolcanic permafrost interaction (~1200 mm/yr precip).",
        "process": "Explosive maar volcanism, fissure effusive lava channels, and periglacial frost heave."
    },
    "devon_01": {
        "why_chosen": "23-km Haughton impact structure at 75.4°N; only terrestrial impact crater set in a high-arctic polar desert with continuous permafrost.",
        "ice_water": "Continuous subsurface water-ice permafrost (>500m depth) and seasonal meltwater channels.",
        "process": "Hypervelocity shock brecciation, cryo-hydrological freeze-thaw, and low-sun polar illumination."
    },
    "pinacate_01": {
        "why_chosen": "Apollo 14 & 15 rover/geology training site; steep phreatomagmatic maar craters (Elegante, Cerro Colorado) and fresh vesicular alkali basalt.",
        "ice_water": "Arid Sonoran regime (~120 mm/yr); dry unconsolidated volcanic ash and lapilli.",
        "process": "Maar crater collapse, pyroclastic base-surge deposition, and desert pavement deflation."
    },
    "kilauea_01": {
        "why_chosen": "Kaʻū Desert leeward volcanic zone; unweathered tholeiitic picrite-basalt, collapse pit craters, and pyroclastic glass beads.",
        "ice_water": "Orographic rain-shadow acid rainfall (~1000 mm/yr) stripping soluble cations.",
        "process": "Effusive shield volcanism, lava tube skylight collapse, and volcanic gas acid-sulfate weathering."
    },
    "mcmurdo_01": {
        "why_chosen": "Coldest, driest hyper-arid polar desert on Earth (-20°C mean, <10 mm snow-water equivalent); premier analog for Lunar PSRs and high-latitude Mars.",
        "ice_water": "Shallow ice-cemented permafrost table under dry sublimation till; zero liquid rainfall.",
        "process": "Cryogenic sublimation, thermal contraction polygon cracking, and katabatic wind scouring."
    },
    "wadi_rum_01": {
        "why_chosen": "Steep ferric-iron sandstone mesas and wide aeolian sand corridors mimicking Martian fretted terrain and outflow valleys.",
        "ice_water": "Arid desert (~50 mm/yr); bone-dry hematitic quartz-feldspar regolith.",
        "process": "Aeolian abrasion, cliff sapping, and iron-oxide grain coating."
    },
    "qaidam_01": {
        "why_chosen": "High-altitude (2800m) Tibetan Plateau basin containing Earth's largest hyper-arid fluvio-lacustrine yardang fleet and Mg-sulfate evaporites.",
        "ice_water": "Hyper-arid cold desert (~25 mm/yr) with high UV flux and hydrated sulfate/clay minerals.",
        "process": "Unidirectional wind carving (yardangs) of ancient paleolake delta beds (Jezero analog)."
    },
    "arizaro_01": {
        "why_chosen": "Extreme high-altitude (3470m) Andean Puna salar with thin atmosphere, intense solar insolation, and low-slope basin geometry.",
        "ice_water": "Hyper-arid halite/gypsum evaporite crust (~40 mm/yr) over hypersaline brine table.",
        "process": "Evaporitic polygon crystallization and high-altitude radiative diurnal cycling."
    },
    "khaybar_01": {
        "why_chosen": "Vast Arabian shield alkali-olivine basalt field ('Harrat') featuring pristine lava tubes, collapse skylights, and aligned scoria cones.",
        "ice_water": "Hot arid desert (~60 mm/yr); anhydrous basaltic boulder fields and thin windblown silt.",
        "process": "Intraplate basaltic volcanism, lava tube roof collapse, and minimal hydrological erosion."
    },
    "tibesti_01": {
        "why_chosen": "Remote Saharan volcanic massif with nested calderas (Trou au Natron, Era Kohor), steep crater walls, and dark ignimbrite/basalt sheets.",
        "ice_water": "Hyper-arid central Sahara (<30 mm/yr); dry caldera floor carbonate/sulfate crusts.",
        "process": "Caldera collapse, steep crater-wall mass wasting, and Saharan aeolian dust mantle."
    },
    "lut_01": {
        "why_chosen": "Hottest land surface on Earth (MODIS >70°C); massive parallel 'Kalut' yardang ridges and dark mafic desert pavement.",
        "ice_water": "Virtually rainless core (<30 mm/yr); extreme thermal desiccation.",
        "process": "High-velocity shamal wind corridor erosion and extreme diurnal thermal shock."
    },
    "makgadikgadi_01": {
        "why_chosen": "Relict mega-paleolake basin with ultra-flat, obstacle-free horizons ideal for landing radar and long-range rover traverse validation.",
        "ice_water": "Seasonal semi-arid pan (~400 mm/yr); dry alkaline carbonate-clay crust in winter.",
        "process": "Lacustrine desiccation, wind-deflated pan leveling, and salt-crust blistering."
    },
    "danakil_01": {
        "why_chosen": "Active continental rift 125m below sea level with flood basalts and acidic iron-sulfur hydrothermal systems mimicking early Hesperian Mars.",
        "ice_water": "Hyper-arid rift (~100 mm/yr) with boiling hyper-acidic brines and ferric sulfate sinters.",
        "process": "Crustal extension faulting, flood basalt effusion, and hydrothermal mineral precipitation."
    },
    "namib_01": {
        "why_chosen": "Ancient hyper-arid coastal sand sea with 300m linear and star dunes coated in ferric iron oxide, matching Martian Bagnold Dunes.",
        "ice_water": "Hyper-arid (<20 mm/yr rain; coastal fog moisture); dry cohesionless quartz-hematite grains.",
        "process": "Aeolian dune migration, grain-flow avalanching on 32° slip faces, and triboelectric dust charging."
    },
}

TARGET_DESCRIPTIONS = {
    "shackleton_rim": "Artemis III candidate landing ridge at 89.9°S. Near-continuous grazing sunlight (1.5° horizon angle) overlooking cryogenic shadows.",
    "shackleton_floor": "Permanently Shadowed Region (PSR) interior floor (~40–75 K). Traps ancient cometary/solar-wind water ice in anorthositic regolith.",
    "hadley_rille": "Apollo 15 landing site at Mare Imbrium edge (26.1°N). Features a 1.5-km-wide sinuous volcanic lava channel cut into high-Fe/Ti mare basalt.",
    "jezero_delta": "Mars 2020 Perseverance landing site (18.4°N). Ancient river delta fan rich in Fe/Mg-smectite clays and carbonates inside a 45-km basin.",
    "valles_marineris": "Coprates Chasma tectonic canyon wall (-13.5°S). Exposes kilometers of layered flood basalt and sulfate bedrock along steep fault escarpments.",
    "arsia_mons": "Southernmost Tharsis shield volcano flank (-9.2°S). Hosts high-altitude basaltic lava tubes and collapse skylights for radiation-shielded habitats.",
}

def export_bundle():
    meta = pd.read_csv("data/tiles/metadata.csv")
    vis = pd.read_csv("data/scores/vision.csv")
    scal = pd.read_csv("data/scores/scalar.csv")
    merged = meta.merge(vis, on="tile_id").merge(scal, on=["tile_id", "target_id"])

    targets_out = {}
    for tid, t_info in TARGETS.items():
        npz_path = f"data/tiles/target_{tid}.npz"
        dem_grid = []
        elev_min, elev_max = 0.0, 100.0
        if os.path.exists(npz_path):
            dem = np.load(npz_path)["dem"]
            elev_min, elev_max = float(np.min(dem)), float(np.max(dem))
            # Downsample 256x256 -> 64x64 uint8 [0..255] for instant HTML5 Canvas hillshade rendering
            small = dem[::4, ::4]
            norm = ((small - elev_min) / (elev_max - elev_min + 1e-6) * 255.0).astype(int)
            dem_grid = norm.tolist()

        targets_out[tid] = {
            **t_info,
            "description": TARGET_DESCRIPTIONS.get(tid, ""),
            "elev_min": round(elev_min, 1),
            "elev_max": round(elev_max, 1),
            "dem_grid": dem_grid,
        }

    regions_out = {}
    for rid, r_info in REGION_META.items():
        regions_out[rid] = {
            **r_info,
            **REGION_NOTES.get(rid, {})
        }

    records = merged.to_dict(orient="records")
    payload = {
        "targets": targets_out,
        "regions": regions_out,
        "tiles": records
    }

    with open("web/data.js", "w", encoding="utf-8") as f:
        f.write("window.LUMSTEM_DATA = " + json.dumps(payload) + ";\n")
    print(f"✅ Exported {len(records)} tile-target records and {len(targets_out)} planetary DEM grids to web/data.js!")

if __name__ == "__main__":
    export_bundle()