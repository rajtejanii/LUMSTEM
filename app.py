# app.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from config import TARGETS, EARTH_REGIONS
from src.step4_fusion import load_and_fuse_scores

st.set_page_config(
    page_title="LUMSTEM | Planetary Analog Mission Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. JPL / AEROSPACE TELEMETRY THEME (ANTI-"AI SLOP" CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B0F17;
        color: #E2E8F0;
    }
    .stApp {
        background-color: #0B0F17;
    }
    /* Tactical Telemetry Cards */
    .telemetry-card {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-left: 3px solid #38BDF8;
        border-radius: 4px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .telemetry-card-mars {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-left: 3px solid #F97316;
        border-radius: 4px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .telemetry-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .telemetry-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.25rem;
        font-weight: 600;
        color: #F8FAFC;
    }
    .telemetry-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 2px;
    }
    .spec-box {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .spec-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #38BDF8;
        margin-bottom: 6px;
        font-weight: 600;
    }
    /* Hide Streamlit default chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. SCIENTIFIC METADATA DICTIONARIES (WHY CHOSEN, ICE/WATER, PROCESSES) ---
REGION_META = {r["region_id"]: r for r in EARTH_REGIONS}

REGION_SCIENTIFIC_NOTES = {
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
    "shackleton_rim": "Artemis III candidate landing ridge at 89.9°S. Receives near-continuous grazing sunlight (1.5° horizon angle) while overlooking cryogenic shadows.",
    "shackleton_floor": "Permanently Shadowed Region (PSR) interior floor (~40–75 K). Traps ancient cometary/solar-wind water ice in anorthositic impact regolith.",
    "hadley_rille": "Apollo 15 landing site at Mare Imbrium edge (26.1°N). Features a 1.5-km-wide sinuous volcanic lava channel cut into high-Fe/Ti mare basalt.",
    "jezero_delta": "Mars 2020 Perseverance landing site (18.4°N). Ancient river delta fan rich in Fe/Mg-smectite clays and carbonates deposited inside a 45-km impact basin.",
    "valles_marineris": "Coprates Chasma tectonic canyon wall (-13.5°S). Exposes kilometers of layered flood basalt and sulfate bedrock along steep fault escarpments.",
    "arsia_mons": "Southernmost Tharsis shield volcano flank (-9.2°S). Hosts high-altitude basaltic lava tubes and collapse skylights ideal for radiation-shielded habitats.",
}

# --- 3. SESSION STATE INITIALIZATION ---
if "slider_vis" not in st.session_state:
    st.session_state.slider_vis = 0.35
    st.session_state.slider_slp = 0.20
    st.session_state.slider_rgh = 0.15
    st.session_state.slider_tmp = 0.15
    st.session_state.slider_lit = 0.15

if "selected_body" not in st.session_state:
    st.session_state.selected_body = "Moon"

if "selected_target_id" not in st.session_state:
    st.session_state.selected_target_id = "shackleton_rim"

if "inspected_tile_id" not in st.session_state:
    st.session_state.inspected_tile_id = None

def set_preset(v, s, r, t, l):
    st.session_state.slider_vis = v
    st.session_state.slider_slp = s
    st.session_state.slider_rgh = r
    st.session_state.slider_tmp = t
    st.session_state.slider_lit = l

def select_body(body_name):
    st.session_state.selected_body = body_name
    body_targets = [k for k, v in TARGETS.items() if v["body"] == body_name]
    if body_targets:
        st.session_state.selected_target_id = body_targets[0]
    st.session_state.inspected_tile_id = None

def select_target(tid):
    st.session_state.selected_target_id = tid
    st.session_state.inspected_tile_id = None

# --- 4. SIDEBAR: WEIGHT SLIDERS & DISCOVERY MODE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=85)
st.sidebar.markdown("### LUMSTEM // TELEMETRY")
st.sidebar.caption("Lunar & Martian Surface To Earth Mapping")

st.sidebar.markdown("#### 1. Mission Presets")
p_col1, p_col2 = st.sidebar.columns(2)
p_col1.button("Rover Nav", on_click=set_preset, args=(0.40, 0.30, 0.20, 0.05, 0.05), use_container_width=True)
p_col2.button("ISRU Drill", on_click=set_preset, args=(0.10, 0.25, 0.10, 0.20, 0.35), use_container_width=True)
st.sidebar.button("Habitat Landing", on_click=set_preset, args=(0.20, 0.30, 0.30, 0.10, 0.10), use_container_width=True)

st.sidebar.markdown("#### 2. Similarity Weights")
w_vis = st.sidebar.slider("2D Geomorphology (DINOv2)", 0.0, 1.0, step=0.05, key="slider_vis")
w_slp = st.sidebar.slider("Steepness (Slope)", 0.0, 1.0, step=0.05, key="slider_slp")
w_rgh = st.sidebar.slider("Ruggedness (Roughness)", 0.0, 1.0, step=0.05, key="slider_rgh")
w_tmp = st.sidebar.slider("Thermal & Illumination", 0.0, 1.0, step=0.05, key="slider_tmp")
w_lit = st.sidebar.slider("Surface Material (Lithology)", 0.0, 1.0, step=0.05, key="slider_lit")

st.sidebar.divider()
hide_famous = st.sidebar.checkbox("Discovery Mode (Hide Famous Sites)", value=False)
st.sidebar.caption("Filters out well-known benchmarks (Atacama, Devon, Askja, Hawaii, Antarctica) to surface unrecognized planetary analogs.")

# --- 5. TOP NAVIGATION: STEP 1 (MOON vs MARS) & STEP 2 (SITE SELECTOR + VISUAL) ---
st.markdown("## LUMSTEM // Multi-Modal Planetary Analog Engine")

b_col1, b_col2, b_spacer = st.columns([1.2, 1.2, 3.6])
is_moon = st.session_state.selected_body == "Moon"
b_col1.button(
    "🌕 MOON // ARTEMIS TARGETS",
    on_click=select_body,
    args=("Moon",),
    type="primary" if is_moon else "secondary",
    use_container_width=True
)
b_col2.button(
    "🔴 MARS // EXPLORATION TARGETS",
    on_click=select_body,
    args=("Mars",),
    type="primary" if not is_moon else "secondary",
    use_container_width=True
)

# Filter targets by selected body
body_targets = {k: v for k, v in TARGETS.items() if v["body"] == st.session_state.selected_body}
if st.session_state.selected_target_id not in body_targets:
    st.session_state.selected_target_id = list(body_targets.keys())[0]

selected_target_id = st.session_state.selected_target_id
target_info = TARGETS[selected_target_id]
accent_color = "#38BDF8" if is_moon else "#F97316"
card_class = "telemetry-card" if is_moon else "telemetry-card-mars"

# Site selection buttons + Target Planetary Visual Banner
t_cols = st.columns(len(body_targets))
for idx, (tid, t_meta) in enumerate(body_targets.items()):
    short_label = t_meta["name"].split(": ")[-1]
    t_cols[idx].button(
        f"🎯 {short_label}",
        key=f"btn_{tid}",
        on_click=select_target,
        args=(tid,),
        type="primary" if tid == selected_target_id else "secondary",
        use_container_width=True
    )

# Render Target Planetary Visual (Real NASA LRO LOLA / MGS MOLA DEM + Illumination Heatmap)
vis_col, spec_col = st.columns([1.3, 2.7])
target_npz_path = f"data/tiles/target_{selected_target_id}.npz"

with vis_col:
    if os.path.exists(target_npz_path):
        t_npz = np.load(target_npz_path)
        t_dem = t_npz["dem"]
        colorscale = "Cividis" if is_moon else "YlOrRd"
        fig_target = go.Figure(data=go.Heatmap(
            z=t_dem,
            colorscale=colorscale,
            showscale=False,
            hovertemplate="Elev: %{z:.0f} m<extra></extra>"
        ))
        fig_target.update_layout(
            title=dict(text=f"NASA Orbital DEM ({target_info['res_m']:.0f}m/px)", font=dict(size=11, color="#94A3B8"), x=0.02, y=0.95),
            margin=dict(l=0, r=0, t=24, b=0),
            height=155,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False, scaleanchor="x"),
            paper_bgcolor="#111827",
            plot_bgcolor="#111827"
        )
        st.plotly_chart(fig_target, use_container_width=True, config={"displayModeBar": False})

with spec_col:
    desc_text = TARGET_DESCRIPTIONS.get(selected_target_id, "Official NASA planetary landing/operations reference site.")
    st.markdown(f"""
    <div class="{card_class}">
        <div class="telemetry-label">ACTIVE PLANETARY REFERENCE // {target_info['body'].upper()}</div>
        <div class="telemetry-value">{target_info['name']}</div>
        <div style="color: #CBD5E1; font-size: 0.88rem; margin-top: 6px; margin-bottom: 8px;">{desc_text}</div>
        <div class="telemetry-sub">
            <b>SOLAR GRAZING ANGLE:</b> {target_info['sun_elev_deg']}° &nbsp;|&nbsp;
            <b>ORBITAL ΔT SWING:</b> {target_info['diviner_delta_t']} K &nbsp;|&nbsp;
            <b>TARGET LITHOLOGY:</b> {target_info.get('lithology_name', 'Basalt')} (Mafic Index {target_info.get('mafic_index', 0.8):.2f}) &nbsp;|&nbsp;
            <b>GRAVITY:</b> {target_info['gravity_g']}g
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. FUSE SCORES ---
weights = {
    "vision_score": w_vis,
    "slope_score": w_slp,
    "roughness_score": w_rgh,
    "temp_swing_score": w_tmp,
    "lithology_score": w_lit,
}
df = load_and_fuse_scores(selected_target_id, weights, hide_famous=hide_famous)

if df.empty:
    st.error("No Earth tiles available. Check your filters.")
    st.stop()

# Default to #1 ranked tile unless user clicked a specific site on the map/selector
if st.session_state.inspected_tile_id not in df["tile_id"].values:
    st.session_state.inspected_tile_id = df.iloc[0]["tile_id"]

# --- 7. MAIN WORKSPACE: INTERACTIVE CLICKABLE WORLD MAP (LEFT) + SITE DOSSIER (RIGHT) ---
map_col, dossier_col = st.columns([1.45, 1.25])

with map_col:
    st.markdown("#### Global Analog Candidates (Click Any Marker on Map to Inspect)")

    # Best tile per region for clean global map markers + Top 25 individual tiles
    region_best_df = df.drop_duplicates(subset=["region_id"]).reset_index(drop=True)
    region_best_df["rank_label"] = [f"#{i+1} {r.split(',')[0]} ({s:.1f}%)" for i, (r, s) in enumerate(zip(region_best_df["region_name"], region_best_df["final_score"]))]

    marker_colors = []
    marker_sizes = []
    for idx, row in region_best_df.iterrows():
        if row["tile_id"] == st.session_state.inspected_tile_id:
            marker_colors.append("#10B981")  # Emerald green for currently inspected site
            marker_sizes.append(18)
        elif idx == 0:
            marker_colors.append(accent_color)  # Cyan or Mars Orange for #1 overall
            marker_sizes.append(15)
        else:
            marker_colors.append("#64748B")
            marker_sizes.append(11)

    fig_map = go.Figure(go.Scattergeo(
        lon=region_best_df["center_lon"],
        lat=region_best_df["center_lat"],
        text=region_best_df["rank_label"],
        customdata=region_best_df["tile_id"],
        mode="markers+text",
        textposition="top center",
        textfont=dict(family="JetBrains Mono, monospace", size=10, color="#E2E8F0"),
        marker=dict(
            size=marker_sizes,
            color=marker_colors,
            line=dict(width=1.5, color="#F8FAFC"),
            opacity=0.95
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Tile ID: %{customdata}<br>"
            "Lat: %{lat:.3f}°, Lon: %{lon:.3f}°<br>"
            "<i>Click marker to load full site dossier</i><extra></extra>"
        )
    ))

    fig_map.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#131C2E",
        showocean=True,
        oceancolor="#090D16",
        showcountries=True,
        countrycolor="#1E293B",
        showcoastlines=True,
        coastlinecolor="#334155",
        showframe=False,
        bgcolor="#0B0F17"
    )
    fig_map.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        dragmode="pan"
    )

    # Interactive map selection event!
    map_event = st.plotly_chart(
        fig_map,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key="global_analog_map"
    )

    # If user clicked a map marker, update the inspected tile ID
    if map_event and map_event.get("selection") and map_event["selection"].get("points"):
        clicked_point = map_event["selection"]["points"][0]
        clicked_tile = clicked_point.get("customdata")
        if clicked_tile in df["tile_id"].values:
            st.session_state.inspected_tile_id = clicked_tile

    # Quick-select dropdown synchronized with map click
    tile_options = region_best_df["tile_id"].tolist()
    tile_labels = {
        row["tile_id"]: f"Rank #{i+1}: {row['region_name']} [{row['tile_id']}] — {row['final_score']:.1f}%"
        for i, row in region_best_df.iterrows()
    }
    selected_from_list = st.selectbox(
        "Or Select Candidate Region Directly:",
        options=tile_options,
        index=tile_options.index(st.session_state.inspected_tile_id) if st.session_state.inspected_tile_id in tile_options else 0,
        format_func=lambda x: tile_labels.get(x, x)
    )
    if selected_from_list != st.session_state.inspected_tile_id:
        st.session_state.inspected_tile_id = selected_from_list
        st.rerun()

# --- 8. RIGHT COLUMN: INSPECTED SITE DOSSIER & SCIENTIFIC BREAKDOWN ---
inspected_row = df[df["tile_id"] == st.session_state.inspected_tile_id].iloc[0]
overall_rank = int(df.index[df["tile_id"] == st.session_state.inspected_tile_id][0]) + 1
reg_id = inspected_row["region_id"]
reg_meta = REGION_META.get(reg_id, {})
sci_notes = REGION_SCIENTIFIC_NOTES.get(reg_id, {})
reg_lith_name = reg_meta.get("lithology_name", "Silicate Regolith")
precip_mm = inspected_row.get("precip_mm", 50)

with dossier_col:
    st.markdown(f"#### Site Dossier // `{inspected_row['tile_id']}` (Global Tile Rank #{overall_rank})")

    # Top 3 Telemetry Cards for Selected Site
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="telemetry-label">WEIGHTED MATCH</div>
            <div class="telemetry-value">{inspected_row['final_score']:.1f}%</div>
            <div class="telemetry-sub">Tile Area: {inspected_row['area_km2']} km²</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="telemetry-label">MEAN SLOPE</div>
            <div class="telemetry-value">{inspected_row['raw_slope']:.2f}°</div>
            <div class="telemetry-sub">Target: {inspected_row['target_slope']:.2f}°</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="telemetry-label">MAFIC LITHOLOGY</div>
            <div class="telemetry-value">{inspected_row['raw_lithology']:.2f}</div>
            <div class="telemetry-sub">Target: {inspected_row['target_lithology']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Tabs: Primary Scientific & Score Breakdown vs Secondary Pentagon Radar Chart
    tab_specs, tab_radar = st.tabs([
        "📋 Scientific Rationale, Ice/Water & Breakdown",
        "📐 5-Axis Radar Fingerprint (Secondary)"
    ])

    with tab_specs:
        # 1. Why Chosen + Lithology + Ice/Water + Active Processes
        st.markdown(f"""
        <div class="spec-box">
            <div class="spec-title">1. GEOLOGICAL RATIONALE & ENVIRONMENTAL SPECIFICATIONS</div>
            <b>Location:</b> {inspected_row['region_name']} ({inspected_row['center_lat']:.3f}°, {inspected_row['center_lon']:.3f}°)<br>
            <b>Why Selected as Analog:</b> {sci_notes.get('why_chosen', 'High structural and geochemical similarity.')}<br>
            <b>Surface Material (Lithology):</b> {reg_lith_name} (Score: {inspected_row['lithology_score']:.1f}%)<br>
            <b>Ice, Water & Permafrost State:</b> {sci_notes.get('ice_water', 'Arid terrestrial regime.')} (~{precip_mm} mm/yr precipitation)<br>
            <b>Dominant Physical Processes:</b> {sci_notes.get('process', 'Aeolian and volcanic resurfacing.')}
        </div>
        """, unsafe_allow_html=True)

        # 2. Clean Horizontal Parameter Score Bars (Intuitive Replacement for Pentagon)
        st.markdown("**Parameter Similarity Breakdown (0–100%):**")
        param_items = [
            ("2D Geomorphology (DINOv2)", inspected_row["vision_score"]),
            ("Steepness (Slope)", inspected_row["slope_score"]),
            ("Ruggedness (Roughness)", inspected_row["roughness_score"]),
            ("Thermal & Illumination", inspected_row["temp_swing_score"]),
            ("Surface Material (Lithology)", inspected_row["lithology_score"]),
        ]
        for label, val in param_items:
            st.progress(int(round(val)), text=f"{label}: {val:.1f}%")

        # 3. Where the Analogy Breaks Down (NASA Challenge Requirement)
        st.warning(
            f"**Where the Analogy Breaks Down (Physical Constraints vs. {target_info['body']}):**\n"
            f"- **Gravity & Traction:** Earth 1.0g vs. {target_info['body']} {target_info['gravity_g']}g increases soil compaction and alters rover wheel slip.\n"
            f"- **Atmospheric Buffering:** Earth atmosphere limits tile ΔT to {inspected_row['raw_temp_swing']:.1f} K vs. {inspected_row['target_temp_swing']:.1f} K on {target_info['body']}.\n"
            f"- **Hydrological Weathering:** ~{precip_mm} mm/yr terrestrial moisture alters clay/salts compared to {target_info['body']} vacuum/cryogenic regolith."
        )

    with tab_radar:
        st.caption(
            "How to read this chart: Each corner of the pentagon represents one of the 5 physical parameters (0% at center, 100% at outer edge). "
            "A full, balanced pentagon indicates a strong all-around analog; a 'dent' shows where the Earth site diverges from the planetary target."
        )
        categories = ['2D Geomorphology', 'Slope', 'Roughness', 'Thermal/Illum', 'Surface Material']
        values = [
            inspected_row['vision_score'],
            inspected_row['slope_score'],
            inspected_row['roughness_score'],
            inspected_row['temp_swing_score'],
            inspected_row['lithology_score']
        ]
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            line_color=accent_color
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#0F172A",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#334155"),
                angularaxis=dict(gridcolor="#334155")
            ),
            showlegend=False,
            height=280,
            margin=dict(l=40, r=40, t=25, b=25),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0", size=11)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# --- 9. FULL RANKED DATA TABLE ---
st.divider()
st.markdown("#### Complete Multi-Modal Candidate Ranking Table")
st.dataframe(
    df[[
        'tile_id', 'region_name', 'final_score',
        'vision_score', 'slope_score', 'roughness_score', 'temp_swing_score', 'lithology_score',
        'raw_slope', 'raw_roughness', 'raw_temp_swing', 'raw_lithology'
    ]],
    use_container_width=True,
    hide_index=True
)