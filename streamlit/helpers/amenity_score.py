import streamlit as st
import pandas as pd
import pydeck as pdk
import h3
from helpers.load import fetch_table

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
    padding: 2rem 0 1rem 0;
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
    margin-top: 0.4rem;
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

/* Make checkboxes blend into the legend style */
div[data-testid="stCheckbox"] {
    margin: 1px 0 !important;
    padding: 0 !important;
}
div[data-testid="stCheckbox"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #5a9e6a !important;
    gap: 6px !important;
}
div[data-testid="stCheckbox"] label p {
    font-size: 0.68rem !important;
    color: #5a9e6a !important;
    margin: 0 !important;
}
/* Selected checkbox label brighter */
div[data-testid="stCheckbox"]:has(input:checked) label p {
    color: #7ddb7d !important;
}
/* Checkbox box itself */
div[data-testid="stCheckbox"] span[data-testid="stWidgetLabel"] {
    color: #5a9e6a !important;
}
input[type="checkbox"] {
    accent-color: #22c55e !important;
}
</style>
""", unsafe_allow_html=True)

CATEGORY_COLS = [
    "Health Care Systems", "Food Access Systems", "Emergency Systems",
    "Education Systems", "Financial Systems", "Public Transport",
    "Green Spaces Systems", "Food and beverages", "Other Systems",
]

@st.cache_data
def load_data():
    df = pd.read_csv("fallback/amenity_score.csv")
    return df

def score_to_rgba(score, min_s=0.0, max_s=10.0):
    if score <= 0:
        return [0, 0, 0, 0]
    t = max(0.0, min(1.0, (score - min_s) / (max_s - min_s))) if max_s != min_s else 0.5
    return [int(10 + t*24), int(15 + t*182), int(13 + t*81), int(40 + t*180)]

@st.cache_data
def build_layer_df(selected: tuple, df):
    rows = []
    for _, row in df.iterrows():
        h3_id = str(row["res_9"]).strip()
        try:
            lat, lng = h3.cell_to_latlng(h3_id)
        except Exception:
            continue

        cat_vals = {c: int(row[c]) for c in selected}
        nonzero  = [v for v in cat_vals.values() if v > 0]

        if set(selected) == set(CATEGORY_COLS):
            score = float(row["gross_amenity_score"])
        else:
            score = (sum(nonzero) / len(nonzero)) if nonzero else 0.0

        lines = [f"{c}: {v}" for c, v in cat_vals.items() if v > 0]

        rows.append({
            "h3_index": h3_id,
            "lat": lat, "lng": lng,
            "gross_amenity_score": round(score, 2),
            "fill_color": score_to_rgba(score),
            **cat_vals,
            "tooltip_categories": "<br>".join(lines) if lines else "No amenities",
        })
    return pd.DataFrame(rows).query("gross_amenity_score > 0")


def render_amenity_map():
    df, source = fetch_table('fct_amenity_score', 'fallback/amenity_score.csv')

    df = df.fillna(0)
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    active_cats = [c for c in CATEGORY_COLS if df[c].sum() > 0]

    map_col, leg_col = st.columns([5, 1])

    with leg_col:
        st.markdown("**Score Scale**")
        for hex_col, label in [
            ("#0a1a10", "0 — None"),
            ("#0a3d1a", "2 — Low"),
            ("#0e6632", "5 — Moderate"),
            ("#19a84a", "7 — Good"),
            ("#22c55e", "10 — Excellent"),
        ]:
            st.markdown(
                f'<div class="legend-row">'
                f'<div class="legend-swatch" style="background:{hex_col}"></div>'
                f'{label}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Categories**")

        selected_cats = []
        for c in active_cats:
            checked = st.checkbox(c, value = True, key = f"cat_{c}")
            if checked:
                selected_cats.append(c)

    with map_col:
        if not selected_cats:
            st.warning("Select at least one category in the legend.")
            st.stop()

        layer_df = build_layer_df(tuple(selected_cats), df)

        hex_layer = pdk.Layer(
            "H3HexagonLayer",
            data = layer_df,
            pickable = True,
            stroked = True,
            filled = True,
            extruded = False,
            get_hexagon = "h3_index",
            get_fill_color = "fill_color",
            get_line_color=[30, 90, 50, 200],
            line_width_min_pixels = 1,
            coverage = 1.05,
            auto_highlight = True,
            highlight_color = [100, 255, 150, 80],
        )

        if "view_state" not in st.session_state:
            st.session_state.view_state = {
                "latitude": 55, "longitude": -4.5,
                "zoom": 4.5, "pitch": 0, "bearing": 0,
            }
        vs = st.session_state.view_state
        view = pdk.ViewState(
            latitude=vs["latitude"],
            longitude=vs["longitude"],
            zoom=vs["zoom"],
            pitch=vs.get("pitch", 0),
            bearing=vs.get("bearing", 0),
        )

        tooltip = {
            "html": """
                <div style="
                    background: #0a0f0d;
                    border: 1px solid #22c55e;
                    border-radius: 4px;
                    padding: 10px 14px;
                    font-family: 'DM Mono', monospace;
                    font-size: 12px;
                    color: #c8d8c8;
                    min-width: 200px;
                    line-height: 1.7;
                ">
                    <div style="color:#22c55e; font-size:10px; letter-spacing:0.12em;
                        text-transform:uppercase; margin-bottom:6px; font-weight:600;">
                        {h3_index}
                    </div>
                    <div style="color:#a0c8a0; margin-bottom:4px;">{tooltip_categories}</div>
                    <div style="border-top:1px solid #1e3028; margin-top:6px;
                        padding-top:6px; color:#7ddb7d;">
                        Score: <b>{gross_amenity_score}</b>
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

        chart_state = st.pydeck_chart(deck, use_container_width=True, height=560, on_select="rerun")
        if chart_state and hasattr(chart_state, "selection"):
            sel = chart_state.selection
            if sel and "view_state" in sel:
                st.session_state.view_state = sel["view_state"]

    with st.expander("Raw data", expanded=False):
        st.dataframe(
            layer_df[["h3_index", "gross_amenity_score"] + selected_cats],
            use_container_width=True,
        )

    # Display footnote
    st.markdown(
        f"<p style='font-size:0.9em; color:grey; margin-bottom:0.1em'>File source: {'Fallback ' + source if source == 'CSV' else source}</p>",
        unsafe_allow_html=True)