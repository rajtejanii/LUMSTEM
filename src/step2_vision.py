# src/step2_vision.py
import os
import torch
import torch.nn.functional as F
import numpy as np
import pandas as pd
from config import TARGETS, BATCH_SIZE

os.makedirs("data/scores", exist_ok=True)
MODEL_INPUT_SIZE = 224

def prep_batch_tensors(tiles_list, device):
    batch = np.stack(tiles_list, axis=0)
    mins = batch.min(axis=(1, 2), keepdims=True)
    maxs = batch.max(axis=(1, 2), keepdims=True)
    norm = (batch - mins) / (maxs - mins + 1e-6)

    tensor = torch.from_numpy(norm).float().unsqueeze(1).to(device)
    tensor = F.interpolate(tensor, size=(MODEL_INPUT_SIZE, MODEL_INPUT_SIZE), mode="bilinear", align_corners=False)
    return tensor.repeat(1, 3, 1, 1)

def run_vision_pipeline():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(device)
    model.eval()

    meta_df = pd.read_csv("data/tiles/metadata.csv")
    paths = meta_df["npz_path"].tolist()
    all_embs = []

    with torch.no_grad():
        for i in range(0, len(paths), BATCH_SIZE):
            batch_tiles = [np.load(p)["dem"] for p in paths[i:i+BATCH_SIZE]]
            embs = model(prep_batch_tensors(batch_tiles, device))
            embs = F.normalize(embs, p=2, dim=-1).cpu().numpy()
            all_embs.append(embs)
    earth_embs = np.vstack(all_embs)

    all_target_dfs = []
    with torch.no_grad():
        for target_id in TARGETS.keys():
            t_dem = np.load(f"data/tiles/target_{target_id}.npz")["dem"]
            t_emb = model(prep_batch_tensors([t_dem], device))
            t_emb = F.normalize(t_emb, p=2, dim=-1).cpu().numpy()

            cos_sims = (earth_embs @ t_emb.T).flatten()
            p5, p95 = np.percentile(cos_sims, 5), np.percentile(cos_sims, 95)
            scores = np.clip((cos_sims - p5) / (p95 - p5 + 1e-6) * 100.0, 0.0, 100.0)

            all_target_dfs.append(pd.DataFrame({
                "target_id": target_id,
                "tile_id": meta_df["tile_id"],
                "vision_score": np.round(scores, 2),
            }))

    pd.concat(all_target_dfs, ignore_index=True).to_csv("data/scores/vision.csv", index=False)
    print("✅ Saved multi-target data/scores/vision.csv")

if __name__ == "__main__":
    run_vision_pipeline()
