# src/step1_ingest_tile.py
import os
import rasterio
from rasterio.windows import from_bounds
import pystac_client
import numpy as np
import pandas as pd
from config import TARGETS, EARTH_REGIONS, TILE_SIZE, RESOLUTION_M

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/tiles", exist_ok=True)

def ingest_planetary_targets():
    for target_id, t_info in TARGETS.items():
        out_npz = f"data/tiles/target_{target_id}.npz"
        tif_path = t_info["tif_path"]
        dy, dx = t_info["crop_offset"]

        if os.path.exists(tif_path):
            with rasterio.open(tif_path) as src:
                raw = src.read(1).astype(np.float32)
                h, w = raw.shape
                cy, cx = h // 2 + dy, w // 2 + dx
                dem_tile = raw[cy - TILE_SIZE//2 : cy + TILE_SIZE//2,
                               cx - TILE_SIZE//2 : cx + TILE_SIZE//2]
                dem_tile = np.nan_to_num(dem_tile, nan=float(np.nanmedian(dem_tile)))
        else:
            y, x = np.ogrid[-128:128, -128:128]
            r = np.sqrt((x - dx//4)**2 + (y - dy//4)**2)
            if t_info["synth_type"] == "crater_rim":
                dem_tile = (np.cos(np.clip(r / 80.0 * np.pi, 0, np.pi)) * -1200.0).astype(np.float32)
            else:
                dem_tile = (np.clip(r - 60.0, 0, 100) * 8.0 - 2000.0).astype(np.float32)

        np.savez_compressed(out_npz, dem=dem_tile)
        print(f"Saved Planetary Target [{target_id}] -> {out_npz}")

def stream_and_tile_earth_region(region):
    bbox = region["bbox"]
    catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
    search = catalog.search(collections=["cop-dem-glo-30"], bbox=bbox)
    items = list(search.items())
    if not items:
        raise RuntimeError(f"No ESA Copernicus DEM items found for {region['name']}")

    href = items[0].assets["data"].href
    meta_records = []
    area_km2 = round(((TILE_SIZE * RESOLUTION_M) / 1000.0) ** 2, 2)

    with rasterio.Env(AWS_NO_SIGN_REQUEST="YES"):
        with rasterio.open(href) as src:
            window = from_bounds(*bbox, transform=src.transform)
            matrix = src.read(1, window=window).astype(np.float32)
            win_transform = src.window_transform(window)
            nodata = src.nodata

            h, w = matrix.shape
            tile_idx = 0
            for r in range(0, h - TILE_SIZE + 1, TILE_SIZE):
                for c in range(0, w - TILE_SIZE + 1, TILE_SIZE):
                    tile = matrix[r:r+TILE_SIZE, c:c+TILE_SIZE]
                    if nodata is not None and np.mean(tile == nodata) > 0.1:
                        continue
                    if np.isnan(tile).mean() > 0.1 or np.std(tile) < 1e-3:
                        continue
                    
                    tile = np.nan_to_num(tile, nan=float(np.nanmedian(tile)))
    
                    lon_min, lat_max = rasterio.transform.xy(win_transform, r, c, offset="ul")
                    lon_max, lat_min = rasterio.transform.xy(win_transform, r + TILE_SIZE, c + TILE_SIZE, offset="lr")
                    center_lon, center_lat = rasterio.transform.xy(win_transform, r + TILE_SIZE // 2, c + TILE_SIZE // 2)
    
                    tile_id = f"{region['region_id']}_t{tile_idx:03d}"
                    npz_path = f"data/tiles/{tile_id}.npz"
                    np.savez_compressed(npz_path, dem=tile)
    
                    meta_records.append({
                        "tile_id": tile_id,
                        "region_id": region["region_id"],
                        "region_name": region["name"],
                        "is_famous": region["is_famous"],
                        "center_lat": round(float(center_lat), 5),
                        "center_lon": round(float(center_lon), 5),
                        "min_lat": round(float(min(lat_min, lat_max)), 5),
                        "max_lat": round(float(max(lat_min, lat_max)), 5),
                        "min_lon": round(float(min(lon_min, lon_max)), 5),
                        "max_lon": round(float(max(lon_min, lon_max)), 5),
                        "area_km2": area_km2,
                        "npz_path": npz_path,
                    })
                    tile_idx += 1
    return meta_records

if __name__ == "__main__":
    ingest_planetary_targets()
    all_meta = []
    for reg in EARTH_REGIONS:
        print(f"Streaming & tiling {reg['name']}...")
        all_meta.extend(stream_and_tile_earth_region(reg))
    pd.DataFrame(all_meta).to_csv("data/tiles/metadata.csv", index=False)
    print(f"✅ Ingestion complete: {len(all_meta)} Earth tiles.")
