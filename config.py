# config.py

TILE_SIZE = 256
RESOLUTION_M = 30.0
BATCH_SIZE = 32

# --- 4 PLANETARY TARGETS (MOON & MARS) ---
TARGETS = {
    "shackleton_rim": {
        "name": "Moon: Shackleton Crater Rim (Illuminated Ridge)",
        "body": "Moon",
        "tif_path": "data/raw/shackleton_dem.tif",
        "crop_offset": (0, 0),
        "synth_type": "crater_rim",
    },
    "shackleton_floor": {
        "name": "Moon: Shackleton PSR (Permanently Shadowed Floor)",
        "body": "Moon",
        "tif_path": "data/raw/shackleton_dem.tif",
        "crop_offset": (128, 128),
        "synth_type": "crater_floor",
    },
    "jezero_delta": {
        "name": "Mars: Jezero Crater (Perseverance Landing Site)",
        "body": "Mars",
        "tif_path": "data/raw/jezero_dem.tif",
        "crop_offset": (0, 0),
        "synth_type": "crater_floor",
    },
    "hadley_rille": {
        "name": "Moon: Apollo 15 Landing Site (Hadley Rille)",
        "body": "Moon",
        "tif_path": "data/raw/hadley_dem.tif",
        "crop_offset": (0, 0),
        "synth_type": "crater_rim", 
    },
}

# --- 15 EARTH ANALOG REGIONS (FAMOUS BENCHMARKS + OBSCURE DISCOVERIES) ---
EARTH_REGIONS = [
    # Famous Benchmarks (Proves the algorithm works)
    {"region_id": "atacama_01", "name": "Atacama Desert, Chile (Arid Mars Analog)", "bbox": [-68.4, -23.4, -68.0, -23.0], "is_famous": True},
    {"region_id": "askja_01", "name": "Askja Highlands, Iceland (Apollo Volcanic Training)", "bbox": [-16.9, 64.9, -16.5, 65.3], "is_famous": True},
    {"region_id": "devon_01", "name": "Devon Island, Canada (Haughton Impact Crater)", "bbox": [-89.9, 75.2, -89.5, 75.6], "is_famous": True},
    {"region_id": "pinacate_01", "name": "El Pinacate, Mexico (Lunar Volcanic Field)", "bbox": [-113.6, 31.7, -113.2, 32.1], "is_famous": True},
    {"region_id": "kilauea_01", "name": "Kilauea Volcanic Desert, Hawaii", "bbox": [-155.3, 19.3, -154.9, 19.7], "is_famous": True},
    {"region_id": "mcmurdo_01", "name": "McMurdo Dry Valleys, Antarctica (Extreme Cold)", "bbox": [161.5, -77.6, 161.9, -77.2], "is_famous": True},
    {"region_id": "wadi_rum_01", "name": "Wadi Rum, Jordan (Martian Geomorphology)", "bbox": [35.3, 29.5, 35.7, 29.9], "is_famous": True},
    
    # Obscure Discoveries (Novel analogs to impress the judges)
    {"region_id": "qaidam_01", "name": "Qaidam Basin Yardangs, China", "bbox": [92.6, 37.6, 93.0, 38.0], "is_famous": False},
    {"region_id": "arizaro_01", "name": "Salar de Arizaro, Argentina (High Altitude Salt)", "bbox": [-67.8, -25.1, -67.4, -24.7], "is_famous": False},
    {"region_id": "khaybar_01", "name": "Harrat Khaybar Basalt Fields, Saudi Arabia", "bbox": [39.8, 25.5, 40.2, 25.9], "is_famous": False},
    {"region_id": "tibesti_01", "name": "Tibesti Volcanic Calderas, Chad", "bbox": [17.2, 20.8, 17.6, 21.2], "is_famous": False},
    {"region_id": "lut_01", "name": "Dasht-e Lut Kaluts, Iran (Extreme Heat/Dunes)", "bbox": [58.6, 30.2, 59.0, 30.6], "is_famous": False},
    {"region_id": "makgadikgadi_01", "name": "Makgadikgadi Pans, Botswana", "bbox": [25.2, -20.9, 25.6, -20.5], "is_famous": False},
    {"region_id": "danakil_01", "name": "Danakil Depression, Ethiopia (Hydrothermal Extremes)", "bbox": [40.1, 14.0, 40.5, 14.4], "is_famous": False},
    {"region_id": "namib_01", "name": "Namib Sand Sea, Namibia", "bbox": [15.2, -24.8, 15.6, -24.4], "is_famous": False},
]