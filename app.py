# app.py
import streamlit as st
import plotly.graph_objects as go
from config import TARGETS
from src.step4_fusion import load_and_fuse_scores

# Force dark mode and wide layout
st.set_page_config(page_title="LUMSTEM | Analog Search", layout="wide", initial_sidebar_state="expanded")

# --- SESSION STATE FOR PRESETS ---
# Initialize the exact keys the sliders will use
if "slider_vis" not in st.session_state:
    st.session_state.slider_vis = 0.5
    st.session_state.slider_slp = 0.3
    st.session_state.slider_rgh = 0.2

def set_preset(v, s, r):
    # Overwrite the slider keys directly to force the UI to snap
    st.session_state.slider_vis = v
    st.session_state.slider_slp = s
    st.session_state.slider_rgh = r

# --- SIDEBAR CONTROLS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=100)
st.sidebar.title("Mission Parameters")

target_options = {k: v["name"] for k, v in TARGETS.items()}
selected_target_id = st.sidebar.selectbox("Planetary Target", options=list(target_options.keys()), format_func=lambda x: target_options[x])

st.sidebar.markdown("### Architecture Weights")
# The sliders now read their default value directly from the session_state keys
w_vis = st.sidebar.slider("2D Shape (Vision)", 0.0, 1.0, step=0.05, key="slider_vis")
w_slp = st.sidebar.slider("Steepness (Slope)", 0.0, 1.0, step=0.05, key="slider_slp")
w_rgh = st.sidebar.slider("Ruggedness (Roughness)", 0.0, 1.0, step=0.05, key="slider_rgh")

st.sidebar.markdown("### Mission Presets")
col1, col2 = st.sidebar.columns(2)
col1.button("Rover Nav", on_click=set_preset, args=(0.6, 0.3, 0.1), use_container_width=True)
col2.button("ISRU Drill", on_click=set_preset, args=(0.1, 0.8, 0.1), use_container_width=True)
st.sidebar.button("Habitat Landing", on_click=set_preset, args=(0.2, 0.2, 0.6), use_container_width=True)

hide_famous = st.sidebar.checkbox("Discovery Mode (Hide Famous Sites)", value=False)

# --- DATA PROCESSING ---
weights = {"vision_score": w_vis, "slope_score": w_slp, "roughness_score": w_rgh}
df = load_and_fuse_scores(selected_target_id, weights, hide_famous=hide_famous)

# --- MAIN DASHBOARD ---
st.title(f"Multi-Modal Planetary Twin Engine")
st.markdown(f"**Targeting:** {target_options[selected_target_id]}")
st.divider()

if df.empty:
    st.error("No Earth tiles available. Check your filters.")
else:
    top_match = df.iloc[0]

    # Top Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Top Analog Match", top_match['region_name'].split(",")[0])
    m2.metric("Overall Similarity", f"{top_match['final_score']:.1f}%")
    m3.metric("Raw Slope", f"{top_match['raw_slope']:.2f}°")
    m4.metric("Earth Area", f"{top_match['area_km2']} km²")

    # Layout: Radar Chart + Map side-by-side
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown(f"#### Match Breakdown: `{top_match['tile_id']}`")
        categories = ['Vision (2D Shape)', 'Slope', 'Roughness']
        values = [top_match['vision_score'], top_match['slope_score'], top_match['roughness_score']]
        
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

    with c2:
        st.markdown("#### Global Candidate Distribution (Top 5)")
        # Map requires 'latitude' and 'longitude' columns
        map_df = df.head(5).rename(columns={"center_lat": "latitude", "center_lon": "longitude"})
        
        # Color the #1 match green, the rest blue
        map_df["color"] = ["#00FF00"] + ["#0088FF"] * (len(map_df) - 1)
        
        st.map(map_df, latitude="latitude", longitude="longitude", size=5000, color="color", zoom=3)

    # Raw Data Table
    st.markdown("#### Candidate Ranking")
    st.dataframe(
        df[['tile_id', 'region_name', 'final_score', 'vision_score', 'slope_score', 'roughness_score', 'raw_slope']],
        use_container_width=True,
        hide_index=True
    )