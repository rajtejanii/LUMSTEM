# src/step0_fetch_nasa_targets.py
import os
import numpy as np
import rasterio
from rasterio.windows import Window

os.makedirs("data/raw", exist_ok=True)

# Official NASA PDS / USGS Astrogeology Cloud-Optimized GeoTIFF Endpoints
# 1. NASA LRO LOLA Global DEM (118m, covers full Moon including 89.9°S Shackleton South Pole)
LRO_LOLA_GLOBAL_URL = (
    "https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
)

# 2. NASA LRO LOLA + JAXA Kaguya Merged DEM (59m high-res, covers 60°N to 60°S including Hadley Rille)
LRO_KAGUYA_MERGE_URL = (
    "https://planetarymaps.usgs.gov/mosaic/LolaKaguya_Topo/"
    "Lunar_LRO_LOLAKaguya_DEMmerge_60N60S_512ppd.tif"
)

# 3. NASA MGS MOLA + ESA Mars Express HRSC Blended Global DEM (200m, covers Jezero Crater)
MARS_MOLA_HRSC_URL = (
    "https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/"
    "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"
)

# Target Planetary Coordinates (Latitude, Longitude, Window Size in Pixels)
NASA_TARGETS = [
    {
        "out_file": "data/raw/shackleton_dem.tif",
        "title": "Moon: Shackleton Crater South Pole (NASA LRO LOLA)",
        "url": LRO_LOLA_GLOBAL_URL,
        "lat": -89.5,   # Near 89.9°S rim/floor boundary
        "lon": 0.0,
        "window_size": 512,  # 512x512 so both (0,0) and (128,128) offsets in config.py work!
    },
    {
        "out_file": "data/raw/hadley_dem.tif",
        "title": "Moon: Apollo 15 Hadley Rille (NASA LRO LOLA + JAXA SELENE)",
        "url": LRO_KAGUYA_MERGE_URL,
        "lat": 26.132,  # Official Apollo 15 Lunar Module Falcon landing coordinates
        "lon": 3.633,
        "window_size": 512,
    },
    {
        "out_file": "data/raw/jezero_dem.tif",
        "title": "Mars: Jezero Crater Delta (NASA MGS MOLA / HRSC)",
        "url": MARS_MOLA_HRSC_URL,
        "lat": 18.444,  # Official Mars 2020 Perseverance Rover Octavia E. Butler landing site
        "lon": 77.451,
        "window_size": 512,
    },
]

def lonlat_to_pixel(src, lon, lat):
    """
    Converts planetary (lon, lat) in degrees to raster (row, col) pixel indices,
    automatically handling cylindrical/equirectangular projections in meters or degrees.
    """
    bounds = src.bounds
    # Check if the GeoTIFF CRS is in projected meters (Simple Cylindrical) vs degrees
    if abs(bounds.right) > 360.0 or abs(bounds.top) > 90.0:
        # Map normalized [-180..180] or [0..360] longitude and [-90..90] latitude to raster extent
        norm_lon = ((lon + 180.0) % 360.0) - 180.0  # [-180, 180]
        col = int(((norm_lon + 180.0) / 360.0) * src.width)
        row = int(((90.0 - lat) / 180.0) * src.height)
    else:
        row, col = src.index(lon, lat)
    return row, col

def fetch_nasa_target_window(target):
    print(f"Streaming {target['title']} from NASA/USGS PDS...")
    half = target["window_size"] // 2

    # GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR' speeds up HTTP range requests by 10x
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with rasterio.open(target["url"]) as src:
            r, c = lonlat_to_pixel(src, target["lon"], target["lat"])

            # Clamp window safely inside raster boundaries
            r_start = max(0, min(src.height - target["window_size"], r - half))
            c_start = max(0, min(src.width - target["window_size"], c - half))
            win = Window(c_start, r_start, target["window_size"], target["window_size"])

            raw_data = src.read(1, window=win).astype(np.float32)

            # Apply official NASA PDS scale factor & offset if stored as scaled int16 (e.g., LOLA * 0.5m)
            scale = src.scales[0] if src.scales and src.scales[0] is not None else 1.0
            offset = src.offsets[0] if src.offsets and src.offsets[0] is not None else 0.0
            if scale == 1.0 and "LDEM_118m" in target["url"]:
                scale = 0.5  # Official LRO LOLA 118m PDS DN-to-meters scale factor

            elev_meters = raw_data * scale + offset

            # Clean nodata spikes
            if src.nodata is not None:
                elev_meters[raw_data == src.nodata] = np.nan
            elev_meters = np.nan_to_num(elev_meters, nan=float(np.nanmedian(elev_meters)))

            # Write clean float32 GeoTIFF to data/raw/
            profile = src.profile.copy()
            profile.update({
                "driver": "GTiff",
                "height": target["window_size"],
                "width": target["window_size"],
                "dtype": "float32",
                "nodata": None,
                "transform": src.window_transform(win),
            })

            with rasterio.open(target["out_file"], "w", **profile) as dst:
                dst.write(elev_meters, 1)

    print(f"  -> Saved real planetary DEM to {target['out_file']} "
          f"(Min: {elev_meters.min():.1f}m, Max: {elev_meters.max():.1f}m)")

if __name__ == "__main__":
    for t in NASA_TARGETS:
        fetch_nasa_target_window(t)
    print("All real NASA Moon & Mars target DEMs downloaded!")