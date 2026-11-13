# src/step4_fusion.py
import pandas as pd

def load_and_fuse_scores(target_id, weights_dict, hide_famous=False):
    """
    Loads the offline CSVs, filters by the selected planetary target,
    merges on tile_id, and computes the weighted final score.
    """
    # 1. Load the generated CSVs
    meta = pd.read_csv("data/tiles/metadata.csv")
    vis = pd.read_csv("data/scores/vision.csv")
    scal = pd.read_csv("data/scores/scalar.csv")

    # 2. Filter by the selected planetary target
    vis = vis[vis["target_id"] == target_id]
    scal = scal[scal["target_id"] == target_id]

    # 3. Merge into a single DataFrame
    df = meta.merge(vis, on="tile_id").merge(scal, on=["tile_id", "target_id"])

    # 4. Apply Discovery Mode filter
    if hide_famous:
        df = df[~df["is_famous"]].copy()

    # 5. Calculate Weighted Final Score
    total_w = sum(weights_dict.values())
    if total_w == 0:
        total_w = 1.0  # Prevent division by zero

    df["final_score"] = 0.0
    for col, weight in weights_dict.items():
        if col in df.columns:
            df["final_score"] += (weight / total_w) * df[col]

    # Sort descending so the best match is at index 0
    return df.sort_values(by="final_score", ascending=False).reset_index(drop=True)