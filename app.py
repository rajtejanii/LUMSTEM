# app.py
import streamlit as st
import plotly.graph_objects as go
from config import TARGETS, EARTH_REGIONS
from src.step4_fusion import load_and_fuse_scores

st.set_page_config(page_title="LUMSTEM | Analog Search", layout="wide", initial_sidebar_state="expanded")

REGION_LITH_NAMES = {r["region_id"]: r.get("lithology_name", "Silicate Regolith") for r in EARTH_REGIONS}

# --- SESSION STATE FOR PRESETS (5 PARAMETERS) ---
if "slider_vis" not in st.session_state:
    st.session_state.slider_vis = 0.35
    st.session_state.slider_slp = 0.20
    st.session_state.slider_rgh = 0.15
    st.session_state.slider_tmp = 0.15
    st.session_state.slider_lit = 0.15

def set_preset(v, s, r, t, l):
    st.session_state.slider_vis = v
    st.session_state.slider_slp = s
    st.session_state.slider_rgh = r
    st.session_state.slider_tmp = t
    st.session_state.slider_lit = l

# --- SIDEBAR CONTROLS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=100)
st.sidebar.title("Mission Parameters")

target_options = {k: v["name"] for k, v in TARGETS.items()}
selected_target_id = st.sidebar.selectbox("Planetary Target", options=list(target_options.keys()), format_func=lambda x: target_options[x])
target_info = TARGETS[selected_target_id]

st.sidebar.markdown("### Architecture Weights")
w_vis = st.sidebar.slider("2D Geomorphology (DINOv2)", 0.0, 1.0, step=0.05, key="slider_vis")
w_slp = st.sidebar.slider("Steepness (Slope)", 0.0, 1.0, step=0.05, key="slider_slp")
w_rgh = st.sidebar.slider("Ruggedness (Roughness)", 0.0, 1.0, step=0.05, key="slider_rgh")
w_tmp = st.sidebar.slider("Thermal & Illumination", 0.0, 1.0, step=0.05, key="slider_tmp")
w_lit = st.sidebar.slider("Surface Material (Lithology)", 0.0, 1.0, step=0.05, key="slider_lit")

st.sidebar.markdown("### Mission Presets")
col1, col2 = st.sidebar.columns(2)
col1.button("Rover Nav", on_click=set_preset, args=(0.40, 0.30, 0.20, 0.05, 0.05), use_container_width=True)
col2.button("ISRU Drill", on_click=set_preset, args=(0.10, 0.25, 0.10, 0.20, 0.35), use_container_width=True)
st.sidebar.button("Habitat Landing", on_click=set_preset, args=(0.20, 0.30, 0.30, 0.10, 0.10), use_container_width=True)

hide_famous = st.sidebar.checkbox("Discovery Mode (Hide Famous Sites)", value=False)

# --- DATA PROCESSING ---
weights = {
    "vision_score": w_vis, 
    "slope_score": w_slp, 
    "roughness_score": w_rgh,
    "temp_swing_score": w_tmp,
    "lithology_score": w_lit,
}
df = load_and_fuse_scores(selected_target_id, weights, hide_famous=hide_famous)

# --- MAIN DASHBOARD ---
st.title("Multi-Modal Planetary Twin Engine")
st.markdown(f"**Targeting:** {target_options[selected_target_id]} | **Target Lithology:** *{target_info.get('lithology_name', 'Basalt')}*")
st.divider()

if df.empty:
    st.error("No Earth tiles available. Check your filters.")
else:
    top_match = df.iloc[0]
    top_reg_lith = REGION_LITH_NAMES.get(top_match["region_id"], "Silicate Bedrock")

    # Top Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Top Analog Match", top_match['region_name'].split(",")[0])
    m2.metric("Overall Similarity", f"{top_match['final_score']:.1f}%")
    m3.metric("Tile Mean Slope", f"{top_match['raw_slope']:.2f}° (Target: {top_match['target_slope']:.2f}°)")
    m4.metric("Mafic-Silicate Index", f"{top_match['raw_lithology']:.2f} (Target: {top_match['target_lithology']:.2f})")

    # Layout: Radar Chart + Map side-by-side
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown(f"#### Match Breakdown: `{top_match['tile_id']}`")
        categories = ['2D Geomorphology', 'Slope', 'Roughness', 'Thermal/Illum', 'Surface Material']
        values = [
            top_match['vision_score'],
            top_match['slope_score'],
            top_match['roughness_score'],
            top_match['temp_swing_score'],
            top_match['lithology_score']
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            line_color='#00d2ff'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- SCIENTIFIC BREAKDOWN PANEL (Addresses NASA Video Prompt 3:22) ---
        st.markdown("#### Scientific Assessment: Where the Analogy Works & Breaks Down")
        st.success(
            f"**Where It Works:** Strong multi-modal match ({top_match['final_score']:.1f}% overall). "
            f"Mean slope is {top_match['raw_slope']:.2f}° vs. {top_match['target_slope']:.2f}° on {target_info['body']}. "
            f"Surface composition is **{top_reg_lith}** ({top_match['lithology_score']:.1f}% geochemical match to {target_info.get('lithology_name')})."
        )
        precip = top_match.get("precip_mm", 50)
        st.warning(
            f"**Where It Breaks Down (Physical Constraints):**\n"
            f"- **Gravity & Atmosphere:** Earth 1.0g vs {target_info['body']} {target_info['gravity_g']}g alters regolith angle of repose and rover traction.\n"
            f"- **Thermal Vacuum:** Terrestrial atmosphere caps surface ΔT at {top_match['raw_temp_swing']:.1f} K vs. {top_match['target_temp_swing']:.1f} K radiative swing on {target_info['body']}.\n"
            f"- **Hydrological Weathering:** Site receives ~{precip} mm/yr precipitation, whereas {target_info['body']} regolith is anhydrous."
        )

    with c2:
        st.markdown("#### Global Candidate Distribution (Top 5 Regions)")
        map_df = df.drop_duplicates(subset=["region_id"]).head(5).rename(columns={"center_lat": "latitude", "center_lon": "longitude"})
        map_df["color"] = ["#00FF00"] + ["#0088FF"] * (len(map_df) - 1)
        st.map(map_df, latitude="latitude", longitude="longitude", size=5000, color="color", zoom=1)

    # Raw Data Table
    st.markdown("#### Candidate Ranking")
    st.dataframe(
        df[[
            'tile_id', 'region_name', 'final_score',
            'vision_score', 'slope_score', 'roughness_score', 'temp_swing_score', 'lithology_score',
            'raw_slope', 'raw_roughness', 'raw_temp_swing', 'raw_lithology'
        ]],
        use_container_width=True,
        hide_index=True
    )