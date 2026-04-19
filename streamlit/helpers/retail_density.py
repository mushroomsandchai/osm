import streamlit as st
import pandas as pd
import pydeck as pdk
import h3
import numpy as np
from helpers.load import fetch_table

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0d0d12;
    color: #d0cce8;
}
.stApp { background: #0d0d12; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.title-block {
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #252030;
    margin-bottom: 1.5rem;
}
.title-block h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f0eeff;
    margin: 0;
}
.title-block p {
    color: #6a5a8a;
    font-size: 0.75rem;
    margin-top: 0.4rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    color: #ff6edb;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #5a4a7a;
}
.legend-wrap {
    background: #0d0d12;
    border: 1px solid #252030;
    border-radius: 4px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("fallback/retail_density.csv")
    return df

def build_color_col(df):
    counts = df["retail_count"].values.copy()
    log_counts = np.log1p(counts)
    vmin, vmax = log_counts.min(), log_counts.max()
    t = np.clip((log_counts - vmin) / (vmax - vmin + 1e-9), 0, 1)

    colors = []
    for ti in t:
        if ti < 0.001:
            colors.append([20, 10, 40, 0])
        elif ti < 0.33:
            s = ti / 0.33
            r = 255
            g = int(224 - s * (224 - 136))
            b = int(0)
            a = int(80 + s * 100)
            colors.append([r, g, b, a])
        elif ti < 0.66:
            s = (ti - 0.33) / 0.33
            r = 255
            g = int(136 - s * 136)
            b = int(s * 60)
            a = int(180 + s * 40)
            colors.append([r, g, b, a])
        else:
            s = (ti - 0.66) / 0.34
            r = int(255 - s * (255 - 204))
            g = int(32 * (1 - s))
            b = int(96 + s * (255 - 96))
            a = int(220 + s * 35)
            colors.append([r, g, b, a])
    return colors


def density_label(v, p95, p75):
    if v >= p95: return "Very High"
    if v >= p75: return "High"
    if v > 1:    return "Moderate"
    if v == 1:   return "Low"
    return "None"


def render_retail_map():
    df, source = fetch_table('fct_retail_density', 'fallback/retail_density.csv')

    df.columns = ["h3_index", "retail_count"]
    df["retail_count"] = pd.to_numeric(df["retail_count"], errors="coerce").fillna(0)

    df["fill_color"] = build_color_col(df)

    p95 = df["retail_count"].quantile(0.95)
    p75 = df["retail_count"].quantile(0.75)
    df["density_label"] = df["retail_count"].apply(density_label, p95 = p95, p75 = p75)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    map_col, leg_col = st.columns([5, 1])

    with leg_col:
        st.markdown("**Density**")
        for color, label in [
            ("#cc00ff", "Very High"),
            ("#ff2060", "High"),
            ("#ff8800", "Moderate"),
            ("#ffe000", "Low"),
            ("#251535", "None"),
        ]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin:5px 0;font-size:0.72rem;color:#9080b8">'
                f'<div style="width:14px;height:14px;background:{color};border-radius:2px;flex-shrink:0;border:1px solid #333"></div>'
                f'{label}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    with map_col:
        hex_layer = pdk.Layer(
            "H3HexagonLayer",
            data=df,
            pickable=True,
            stroked=False,
            filled=True,
            extruded=False,
            get_hexagon="h3_index",
            get_fill_color="fill_color",
            coverage=1.05,
            auto_highlight=True,
            highlight_color=[255, 255, 255, 40],
        )

        view = pdk.ViewState(
            latitude = 55,
            longitude = -4.5,
            zoom = 4.5,
            pitch = 0,
            bearing = 0,
        )

        tooltip = {
            "html": """
                <div style="
                    background: #0d0d12;
                    border: 1px solid #cc00ff;
                    border-radius: 4px;
                    padding: 10px 14px;
                    font-family: 'DM Mono', monospace;
                    font-size: 12px;
                    color: #d0cce8;
                    min-width: 180px;
                    line-height: 1.8;
                ">
                    <div style="color:#cc00ff;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;font-weight:600;">
                        {h3_index}
                    </div>
                    <div>Retail outlets: <b style="color:#ff8800">{retail_count}</b></div>
                    <div style="border-top:1px solid #252030;margin-top:6px;padding-top:6px;color:#9080b8">
                        Density: <b style="color:#ff6edb">{density_label}</b>
                    </div>
                </div>
            """,
            "style": {"background": "transparent", "border": "none", "padding": "0"},
        }

        deck = pdk.Deck(
            layers=[hex_layer],
            initial_view_state=view,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        )

        st.pydeck_chart(deck, use_container_width=True, height=580)

    # Display footnote
    st.markdown(
        f"<p style='font-size:0.9em; color:grey; margin-bottom:0.1em'>File source: {'Fallback ' + source if source == 'CSV' else source}</p>",
        unsafe_allow_html=True)