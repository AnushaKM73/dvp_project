"""
Dashboard 8: Interactive Hierarchical GIS Map (India -> State -> District -> Tourist Places)
3-Level Spatial Drill-Down Engine with Leaflet.js, GeoJSON boundary rendering, and tourist attraction mapping
"""

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.map_component import generate_hierarchical_map_html, extract_tourism_destinations

# Page Configuration
st.set_page_config(
    page_title="Interactive GIS Map - India Tourism BI",
    page_icon="🗺️",
    layout="wide"
)

# Apply Power BI Theme
apply_theme()

# Global Sidebar Filters
filtered_df = render_sidebar_filters()

# Header Banner
render_page_header(
    title="Interactive GIS Map: India, States, Districts & Tourist Places",
    subtitle="Hierarchical 3-Level Drill-Down GIS Engine: Country ➔ State Districts ➔ Verified Tourist Attractions",
    badge="GEOSPATIAL INTELLIGENCE • LEAFLET GIS ENGINE"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# QUICK KPI SUMMARY
# -------------------------------------------------------------
dest_records = extract_tourism_destinations(filtered_df)
total_landmarks = len(dest_records)
states_represented = len(filtered_df['State'].unique())

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("Active Records", f"{len(filtered_df):,}", "Verified tourist visits", "#0284c7", "📊")
with k2:
    render_kpi_card("Iconic Landmarks", f"{total_landmarks}", "Covered in GIS engine", "#0d9488", "📍")
with k3:
    render_kpi_card("States Represented", f"{states_represented}", "Pan-India coverage", "#6366f1", "🗺️")
with k4:
    render_kpi_card("Drill-Down Depth", "3 Levels", "Country ➔ State ➔ District", "#10b981", "🔍")

# -------------------------------------------------------------
# INTERACTIVE GIS INSTRUCTIONS & DEMO GUIDE
# -------------------------------------------------------------
with st.expander("ℹ️ How to Use the Interactive GIS Map (Evaluation & Viva Guide)", expanded=False):
    st.markdown("""
    **3-Level Hierarchical Drill-Down:**
    1. **Level 1 (All India):** Hover over any state to inspect landmark counts. Click on a state (e.g. **Karnataka**) to zoom into its district map.
    2. **Level 2 (District Map):** Hover over districts to view district names. Click any district (e.g. **Mandya** or **Mysuru**) to inspect tourist places.
    3. **Level 3 (Tourist Places):**
       - **Mandya District:** Displays *"No tourist places are currently available in the dataset for this district."* (as required, since the dataset contains no Mandya records).
       - **Mysuru / Kodagu / Vijayanagara:** Displays pins and rich tourist destination cards (Mysore Palace, Coorg, Hampi) with category, rating, cost, and address.
    4. **Navigation:** Use the **← Back to State** and **← Back to India** buttons, or click the breadcrumbs (`India ❯ Karnataka ❯ Mandya`) to navigate backward at any time.
    """)

# -------------------------------------------------------------
# MAIN INTERACTIVE LEAFLET MAP COMPONENT
# -------------------------------------------------------------
map_html = generate_hierarchical_map_html(filtered_df)
components.html(map_html, height=740, scrolling=False)

# -------------------------------------------------------------
# DATASET DISTRICT CORRELATION AUDIT TABLE
# -------------------------------------------------------------
st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="margin: 10px 0 10px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">
    <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">
        📋 Destination to District Correlation Master Reference
    </h3>
</div>
""", unsafe_allow_html=True)

tab_table, tab_arch = st.tabs(["📊 Verified Landmark Registry", "🏛️ Technical Architecture & Limitations"])

with tab_table:
    dest_table_data = []
    for d in dest_records:
        dest_table_data.append({
            "Landmark": d["Place"],
            "State": d["State"],
            "Matched District": d["District"],
            "Address": d["Address"],
            "Category": d["Category"],
            "Avg Rating": f"⭐ {d['Rating']}",
            "Avg Cost": f"₹{d['Estimated_Cost']:,}",
            "Best Time": d["Best_Time"],
            "Latitude": d["Latitude"],
            "Longitude": d["Longitude"]
        })
    df_table = pd.DataFrame(dest_table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
    st.caption("Matches derived strictly from actual dataset coordinates and address attributes without inventing data.")

with tab_arch:
    st.markdown("""
    **Architectural Highlights:**
    - **No NIC Taluk API Delays:** Direct GeoJSON boundary rendering prevents network timeouts previously experienced with government taluk APIs.
    - **Dual-Layer GeoJSON Delivery:** Attempts fast CDN edge fetch (`jsDelivr`) with instant zero-delay fallback to bundled local GeoJSON files (`data/geojson/`).
    - **District Matching Rigor:** Strict matching based on destination coordinates and verified address fields. Uncovered districts (like *Mandya*) display the standardized *"No tourist places are currently available in the dataset for this district"* advisory.
    - **Zero Foreign Geography:** Map automatically centers and bounds tightly to Indian national and state territories.
    """)

