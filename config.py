# config.py

TILE_SIZE = 256
RESOLUTION_M = 30.0
BATCH_SIZE = 32

# --- 4 PLANETARY TARGETS (MOON & MARS) ---
# Includes exact pixel resolution (res_m), solar grazing angle (sun_elev_deg),
# and NASA LRO Diviner / Mars THEMIS surface temperature swing across the tile (K).
TARGETS = {
    "shackleton_rim": {
        "name": "Moon: Shackleton Crater Rim (Illuminated Ridge)",
        "body": "Moon",
        "tif_path": "data/raw/shackleton_dem.tif",
        "crop_offset": (0, 0),
        "res_m": 118.0,            # NASA LRO LOLA Global 118m/px
        "sun_elev_deg": 1.5,       # Grazing South Pole solar horizon angle
        "diviner_delta_t": 185.0,  # Illuminated ridge (~220K) vs shadowed slope (~35K)
        "gravity_g": 0.165,
    },
    "shackleton_floor": {
        "name": "Moon: Shackleton PSR (Permanently Shadowed Floor)",
        "body": "Moon",
        "tif_path": "data/raw/shackleton_dem.tif",
        "crop_offset": (128, 128),
        "res_m": 118.0,
        "sun_elev_deg": 1.5,
        "diviner_delta_t": 35.0,   # Permanently shadowed floor (40K-75K via scattered IR)
        "gravity_g": 0.165,
    },
    "jezero_delta": {
        "name": "Mars: Jezero Crater (Perseverance Landing Site)",
        "body": "Mars",
        "tif_path": "data/raw/jezero_dem.tif",
        "crop_offset": (0, 0),
        "res_m": 200.0,            # NASA MGS MOLA / HRSC 200m/px
        "sun_elev_deg": 45.0,      # Mid-latitude Martian solar angle
        "diviner_delta_t": 65.0,   # Mars MEDA/THEMIS diurnal swing (~190K to ~255K)
        "gravity_g": 0.38,
    },
    "hadley_rille": {
        "name": "Moon: Apollo 15 Landing Site (Hadley Rille)",
        "body": "Moon",
        "tif_path": "data/raw/hadley_dem.tif",
        "crop_offset": (0, 0),
        "res_m": 59.2,             # NASA LRO LOLA + Kaguya 512ppd (~59.2m/px)
        "sun_elev_deg": 15.0,      # Morning Apollo landing illumination angle
        "diviner_delta_t": 140.0,  # Sunlit mare vs rille shadow thermal contrast
        "gravity_g": 0.165,
    },
}

# --- 15 EARTH ANALOG REGIONS (FAMOUS BENCHMARKS + OBSCURE DISCOVERIES) ---
# All bounding boxes aligned strictly within single 1x1 degree Copernicus GLO-30 cells.
EARTH_REGIONS = [
    # Famous Benchmarks
    {"region_id": "atacama_01", "name": "Atacama Desert, Chile (Arid Mars Analog)", "bbox": [-68.5, -23.5, -68.1, -23.1], "is_famous": True, "modis_diurnal_k": 38.0, "precip_mm": 15},
    {"region_id": "askja_01", "name": "Askja Highlands, Iceland (Apollo Volcanic Training)", "bbox": [-16.9, 65.05, -16.5, 65.45], "is_famous": True, "modis_diurnal_k": 16.0, "precip_mm": 1200},
    {"region_id": "devon_01", "name": "Devon Island, Canada (Haughton Impact Crater)", "bbox": [-89.9, 75.2, -89.5, 75.6], "is_famous": True, "modis_diurnal_k": 14.0, "precip_mm": 185},
    {"region_id": "pinacate_01", "name": "El Pinacate, Mexico (Lunar Volcanic Field)", "bbox": [-113.6, 31.55, -113.2, 31.95], "is_famous": True, "modis_diurnal_k": 32.0, "precip_mm": 120},
    {"region_id": "kilauea_01", "name": "Kilauea Volcanic Desert, Hawaii", "bbox": [-155.45, 19.25, -155.05, 19.65], "is_famous": True, "modis_diurnal_k": 18.0, "precip_mm": 1000},
    {"region_id": "mcmurdo_01", "name": "McMurdo Dry Valleys, Antarctica (Extreme Cold)", "bbox": [161.5, -77.6, 161.9, -77.2], "is_famous": True, "modis_diurnal_k": 22.0, "precip_mm": 10},
    {"region_id": "wadi_rum_01", "name": "Wadi Rum, Jordan (Martian Geomorphology)", "bbox": [35.3, 29.5, 35.7, 29.9], "is_famous": True, "modis_diurnal_k": 29.0, "precip_mm": 50},
    
    # Obscure Discoveries
    {"region_id": "qaidam_01", "name": "Qaidam Basin Yardangs, China", "bbox": [92.55, 37.55, 92.95, 37.95], "is_famous": False, "modis_diurnal_k": 36.0, "precip_mm": 25},
    {"region_id": "arizaro_01", "name": "Salar de Arizaro, Argentina (High Altitude Salt)", "bbox": [-67.8, -24.95, -67.4, -24.55], "is_famous": False, "modis_diurnal_k": 39.0, "precip_mm": 40},
    {"region_id": "khaybar_01", "name": "Harrat Khaybar Basalt Fields, Saudi Arabia", "bbox": [39.55, 25.5, 39.95, 25.9], "is_famous": False, "modis_diurnal_k": 31.0, "precip_mm": 60},
    {"region_id": "tibesti_01", "name": "Tibesti Volcanic Calderas, Chad", "bbox": [17.2, 20.55, 17.6, 20.95], "is_famous": False, "modis_diurnal_k": 34.0, "precip_mm": 30},
    {"region_id": "lut_01", "name": "Dasht-e Lut Kaluts, Iran (Extreme Heat/Dunes)", "bbox": [58.55, 30.2, 58.95, 30.6], "is_famous": False, "modis_diurnal_k": 42.0, "precip_mm": 30},
    {"region_id": "makgadikgadi_01", "name": "Makgadikgadi Pans, Botswana", "bbox": [25.2, -20.9, 25.6, -20.5], "is_famous": False, "modis_diurnal_k": 28.0, "precip_mm": 400},
    {"region_id": "danakil_01", "name": "Danakil Depression, Ethiopia (Hydrothermal Extremes)", "bbox": [40.1, 14.05, 40.5, 14.45], "is_famous": False, "modis_diurnal_k": 33.0, "precip_mm": 100},
    {"region_id": "namib_01", "name": "Namib Sand Sea, Namibia", "bbox": [15.2, -24.8, 15.6, -24.4], "is_famous": False, "modis_diurnal_k": 30.0, "precip_mm": 20},
]