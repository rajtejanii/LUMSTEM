# src/step1_ingest_tile.py
import os
import rasterio
import pystac_client
import numpy as np
import pandas as pd
import earthaccess
from dotenv import load_dotenv
from rasterio.windows import from_bounds
from config import TARGETS, EARTH_REGIONS, TILE_SIZE, RESOLUTION_M

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/tiles", exist_ok=True)

load_dotenv()

# Authenticate once at module initialization if NASA Earthdata credentials exist
NASA_AUTH_READY = False
if os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD"):
    try:
        earthaccess.login(strategy="environment")
        NASA_AUTH_READY = True
    except Exception as e:
        print(f"[NASA Earthdata] Auth warning: {e}")

def compute_3d_illumination_and_thermal(dem, res_m, sun_elev_deg, base_delta_t, is_target=False):
    """
    Computes 3D solar incidence illumination and surface temperature variation.
    For Earth tiles, modulates the baseline diurnal swing by the tile's 3D shadow
    contrast so deep craters/canyons exhibit stronger thermal swings than flat plains.
    """
    dz_dy, dz_dx = np.gradient(dem, res_m)
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    aspect_rad = np.arctan2(-dz_dy, dz_dx)

    sun_zenith_rad = np.radians(90.0 - sun_elev_deg)
    sun_azimuth_rad = np.radians(180.0)

    cos_i = (
        np.cos(sun_zenith_rad) * np.cos(slope_rad)
        + np.sin(sun_zenith_rad) * np.sin(slope_rad) * np.cos(sun_azimuth_rad - aspect_rad)
    )
    illum_map = np.clip(cos_i, 0.0, 1.0).astype(np.float32)

    p2, p98 = np.percentile(illum_map, 2), np.percentile(illum_map, 98)
    illum_span = float(p98 - p2)
    if illum_span > 1e-4:
        norm_illum = np.clip((illum_map - p2) / illum_span, 0.0, 1.0)
    else:
        s2, s98 = np.percentile(slope_rad, 2), np.percentile(slope_rad, 98)
        norm_illum = np.clip((slope_rad - s2) / (s98 - s2 + 1e-6), 0.0, 1.0)

    # For Earth tiles, modulate thermal contrast by 3D topographic shadow depth (0.75x on flat pan up to 1.25x in deep canyon)
    if is_target:
        topo_factor = 1.0
    else:
        topo_factor = 0.75 + 0.50 * np.clip(illum_span / 0.35, 0.0, 1.0)

    elev_cooling = -((dem - np.min(dem)) / 1000.0) * 6.5
    temp_map = (norm_illum * (base_delta_t * topo_factor) + elev_cooling).astype(np.float32)

    return illum_map, temp_map

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
            raise FileNotFoundError(f"Missing {tif_path}! Run step0_fetch_nasa_targets first.")

        # ---> ADD is_target=True RIGHT HERE <---
        illum_tile, temp_tile = compute_3d_illumination_and_thermal(
            dem_tile,
            res_m=t_info["res_m"],
            sun_elev_deg=t_info["sun_elev_deg"],
            base_delta_t=t_info["diviner_delta_t"],
            is_target=True
        )

        np.savez_compressed(
            out_npz,
            dem=dem_tile,
            temp=temp_tile,
            illum=illum_tile,
            res_m=np.float32(t_info["res_m"])
        )
        print(f"Saved Planetary Target [{target_id}] (res={t_info['res_m']}m) -> {out_npz}")

def fetch_stac_href(catalog, bbox, collections, asset_name):
    search = catalog.search(collections=collections, bbox=bbox, max_items=1)
    items = list(search.items())
    if not items or asset_name not in items[0].assets:
        return None
    return items[0].assets[asset_name].href

def verify_nasa_modis_granule(region):
    """Queries NASA CMR for MODIS MOD11A1 thermal granule coverage & returns baseline swing."""
    base_swing = float(region.get("modis_diurnal_k", 25.0))
    if not NASA_AUTH_READY:
        return base_swing
    try:
        results = earthaccess.search_data(
            short_name="MOD11A1",
            bounding_box=tuple(region["bbox"]),
            temporal=("2023-07-01", "2023-07-07"),
            count=1
        )
        if results:
            print(f"  [NASA Earthdata] Verified MODIS MOD11A1 granule for {region['name']} (ΔT_base={base_swing}K)")
    except Exception as e:
        print(f"  [NASA Earthdata] Using offline MODIS climatic baseline ({base_swing}K): {e}")
    return base_swing

def stream_and_tile_earth_region(region):
    bbox = region["bbox"]
    catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
    
    dem_href = fetch_stac_href(catalog, bbox, ["cop-dem-glo-30"], "data")
    if not dem_href:
        raise RuntimeError(f"No ESA Copernicus DEM items found for {region['name']}")

    base_diurnal_k = verify_nasa_modis_granule(region)
    mean_lat = abs((bbox[1] + bbox[3]) / 2.0)
    earth_sun_elev = max(5.0, 90.0 - mean_lat - 15.0)

    meta_records = []
    area_km2 = round(((TILE_SIZE * RESOLUTION_M) / 1000.0) ** 2, 2)

    with rasterio.Env(AWS_NO_SIGN_REQUEST="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(dem_href) as src_dem:
            window = from_bounds(*bbox, transform=src_dem.transform)
            # Round window offsets/lengths to integer pixels inside raster bounds
            window = window.round_offsets().round_lengths()
            matrix = src_dem.read(1, window=window, boundless=True, fill_value=np.nan).astype(np.float32)
            win_transform = src_dem.window_transform(window)
            nodata = src_dem.nodata

            h, w = matrix.shape
            tile_idx = 0
            
            for r in range(0, h - TILE_SIZE + 1, TILE_SIZE):
                for c in range(0, w - TILE_SIZE + 1, TILE_SIZE):
                    dem_tile = matrix[r:r+TILE_SIZE, c:c+TILE_SIZE].copy()
                    if nodata is not None:
                        dem_tile[dem_tile == nodata] = np.nan

                    if np.mean(np.isnan(dem_tile)) > 0.1 or np.nanstd(dem_tile) < 1e-3:
                        continue

                    dem_tile = np.nan_to_num(dem_tile, nan=float(np.nanmedian(dem_tile)))

                    illum_tile, temp_tile = compute_3d_illumination_and_thermal(
                        dem_tile,
                        res_m=RESOLUTION_M,
                        sun_elev_deg=earth_sun_elev,
                        base_delta_t=base_diurnal_k
                    )

                    lon_min, lat_max = rasterio.transform.xy(win_transform, r, c, offset="ul")
                    lon_max, lat_min = rasterio.transform.xy(win_transform, r + TILE_SIZE, c + TILE_SIZE, offset="lr")
                    center_lon, center_lat = rasterio.transform.xy(win_transform, r + TILE_SIZE // 2, c + TILE_SIZE // 2)

                    tile_id = f"{region['region_id']}_t{tile_idx:03d}"
                    npz_path = f"data/tiles/{tile_id}.npz"

                    np.savez_compressed(
                        npz_path,
                        dem=dem_tile,
                        temp=temp_tile,
                        illum=illum_tile,
                        res_m=np.float32(RESOLUTION_M)
                    )

                    meta_records.append({
                        "tile_id": tile_id,
                        "region_id": region["region_id"],
                        "region_name": region["name"],
                        "is_famous": region["is_famous"],
                        "precip_mm": region.get("precip_mm", 50),
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