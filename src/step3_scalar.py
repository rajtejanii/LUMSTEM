# src/step3_scalar.py
import os
import numpy as np
import pandas as pd
from config import TARGETS, RESOLUTION_M

os.makedirs("data/scores", exist_ok=True)

def calc_slope(npz_data):
    dem = npz_data["dem"]
    dz_dy, dz_dx = np.gradient(dem, RESOLUTION_M)
    return float(np.degrees(np.mean(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))))

def calc_roughness(npz_data):
    return float(np.std(npz_data["dem"]))

def calc_temp_amplitude(npz_data):
    """Calculates the max thermal swing (Max Temp - Min Temp) of the tile."""
    # Fallback to 0 if the temp array hasn't been added to the .npz yet
    if "temp" not in npz_data:
        return 0.0
    temp_array = npz_data["temp"]
    return float(np.max(temp_array) - np.min(temp_array))

def calc_sar_roughness(npz_data):
    """Calculates sub-surface rock/ice density using SAR backscatter."""
    if "sar" not in npz_data:
        return 0.0
    return float(np.mean(npz_data["sar"]))

SCALAR_EXTRACTORS = {
    "slope": calc_slope,
    "roughness": calc_roughness,
    "temp_swing": calc_temp_amplitude,
    "sar_density": calc_sar_roughness
}

def run_scalar_pipeline():
    meta_df = pd.read_csv("data/tiles/metadata.csv")
    
    earth_rows = []
    for _, row in meta_df.iterrows():
        earth_npz = np.load(row["npz_path"])
        rec = {"tile_id": row["tile_id"]}
        for k, fn in SCALAR_EXTRACTORS.items():
            rec[f"raw_{k}"] = round(fn(earth_npz), 3)
        earth_rows.append(rec)
    base_earth_df = pd.DataFrame(earth_rows)

    all_target_dfs = []
    for target_id in TARGETS.keys():
        t_npz = np.load(f"data/tiles/target_{target_id}.npz")
        t_base = {k: fn(t_npz) for k, fn in SCALAR_EXTRACTORS.items()}

        df = base_earth_df.copy()
        df.insert(0, "target_id", target_id)
        for k, target_val in t_base.items():
            diff = np.abs(df[f"raw_{k}"] - target_val)
            p95_diff = np.percentile(diff, 95) + 1e-6
            df[f"{k}_score"] = np.round(np.clip((1.0 - diff / p95_diff) * 100.0, 0.0, 100.0), 2)
        all_target_dfs.append(df)

    pd.concat(all_target_dfs, ignore_index=True).to_csv("data/scores/scalar.csv", index=False)
    print("✅ Saved multi-target data/scores/scalar.csv")

if __name__ == "__main__":
    run_scalar_pipeline()
