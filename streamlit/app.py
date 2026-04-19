import streamlit as st
from helpers.amenity_score import render_amenity_map
from helpers.retail_density import render_retail_map

st.set_page_config(
    page_title="15-Minute City - Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0f0d;
    color: #c8d8c8;
}
.stApp { background: #0a0f0d; }
h1, h2, h3 { font-family: 'Syne', sans-serif; letter-spacing: -0.02em; }

.title-block {
    padding: 0rem 0 0rem 0;
    border-bottom: 1px solid #1e3028;
    margin-bottom: 2rem;
}
.title-block h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #e8f5e8;
    margin: 0;
    line-height: 1.1;
}
.title-block p {
    color: #5a7a62;
    font-size: 0.78rem;
    margin-top: 0rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.legend-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
    font-size: 0.72rem;
    color: #5a7a62;
}
.legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 2px;
    border: 1px solid #1e3028;
    flex-shrink: 0;
}
div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    color: #7ddb7d;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4a6450;
}
div[data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #5a7a62 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #7ddb7d !important;
    border-bottom-color: #7ddb7d !important;
}
div[data-testid="stCheckbox"] {
    margin: 1px 0 !important;
    padding: 0 !important;
}
div[data-testid="stCheckbox"] label p {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #5a9e6a !important;
    margin: 0 !important;
}
div[data-testid="stCheckbox"]:has(input:checked) label p {
    color: #7ddb7d !important;
}
input[type="checkbox"] { accent-color: #22c55e !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-block">
    <h1>15-Minute City - Dashboard</h1>
    <p>UK Liveability &amp; Retail Density - H3 Spatial Analysis</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Amenity Score", "Retail Density - Heat Map"])

with tab1:
    render_amenity_map()

with tab2:
    render_retail_map()