# src/step3_scalar.py
import os
import numpy as np
import pandas as pd
from config import TARGETS, EARTH_REGIONS, RESOLUTION_M

os.makedirs("data/scores", exist_ok=True)

REGION_MAFIC_MAP = {r["region_id"]: float(r.get("mafic_index", 0.5)) for r in EARTH_REGIONS}

def get_res_m(npz_data):
    """Reads the true physical pixel spacing (30m Earth, 59m/118m Moon, 200m Mars)."""
    if "res_m" in npz_data:
        return float(npz_data["res_m"])
    return float(RESOLUTION_M)

def calc_slope(npz_data):
    """Calculates true mean physical slope in degrees using the tile's exact resolution."""
    dem = npz_data["dem"]
    res_m = get_res_m(npz_data)
    dz_dy, dz_dx = np.gradient(dem, res_m)
    return float(np.degrees(np.mean(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))))

def calc_roughness(npz_data):
    """
    Calculates scale-normalized Terrain Ruggedness (standard deviation of local slope gradient),
    avoiding false high scores on smooth tilted ramps.
    """
    dem = npz_data["dem"]
    res_m = get_res_m(npz_data)
    dz_dy, dz_dx = np.gradient(dem, res_m)
    slope_mag = np.sqrt(dz_dx**2 + dz_dy**2)
    return float(np.std(slope_mag) * 100.0)

def calc_temp_amplitude(npz_data):
    """Calculates the 2nd-to-98th percentile thermal/illumination contrast (K) across the tile."""
    if "temp" not in npz_data:
        return 0.0
    temp_array = npz_data["temp"]
    return float(np.percentile(temp_array, 98) - np.percentile(temp_array, 2))

SCALAR_EXTRACTORS = {
    "slope": calc_slope,
    "roughness": calc_roughness,
    "temp_swing": calc_temp_amplitude,
}

def run_scalar_pipeline():
    meta_df = pd.read_csv("data/tiles/metadata.csv")
    
    earth_rows = []
    for _, row in meta_df.iterrows():
        earth_npz = np.load(row["npz_path"])
        rec = {"tile_id": row["tile_id"]}
        for k, fn in SCALAR_EXTRACTORS.items():
            rec[f"raw_{k}"] = round(fn(earth_npz), 3)

        # Compute 5th Parameter: Surface Material (Mafic-Silicate Index modulated by bedrock slope exposure)
        reg_id = row["region_id"] if "region_id" in row else row["tile_id"].rsplit("_t", 1)[0]
        base_mafic = REGION_MAFIC_MAP.get(reg_id, 0.5)
        bedrock_exposure = 0.03 * np.clip(rec["raw_slope"] / 15.0, 0.0, 1.0)
        rec["raw_lithology"] = round(float(np.clip(base_mafic + bedrock_exposure, 0.0, 1.0)), 3)

        earth_rows.append(rec)
    base_earth_df = pd.DataFrame(earth_rows)

    all_target_dfs = []
    for target_id, t_info in TARGETS.items():
        t_npz = np.load(f"data/tiles/target_{target_id}.npz")
        t_base = {k: fn(t_npz) for k, fn in SCALAR_EXTRACTORS.items()}
        t_base["lithology"] = float(t_info.get("mafic_index", 0.80))

        print(f"Target [{target_id}] Baselines -> Slope: {t_base['slope']:.2f}°, "
              f"Roughness: {t_base['roughness']:.2f}, ΔT: {t_base['temp_swing']:.1f}K, "
              f"Mafic Index: {t_base['lithology']:.2f}")

        df = base_earth_df.copy()
        df.insert(0, "target_id", target_id)
        for k, target_val in t_base.items():
            df[f"target_{k}"] = round(target_val, 2)
            diff = np.abs(df[f"raw_{k}"] - target_val)
            p5_diff, p95_diff = np.percentile(diff, 5), np.percentile(diff, 95)
            df[f"{k}_score"] = np.round(
                np.clip((p95_diff - diff) / (p95_diff - p5_diff + 1e-6) * 100.0, 0.0, 100.0), 2
            )
        all_target_dfs.append(df)

    pd.concat(all_target_dfs, ignore_index=True).to_csv("data/scores/scalar.csv", index=False)
    print("✅ Saved 5-parameter multi-target data/scores/scalar.csv")

if __name__ == "__main__":
    run_scalar_pipeline()