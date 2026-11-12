"""
Dashboard 2: Geographical Analysis
Spatial analysis, interactive Folium India map, and regional performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.visualizations import (
    create_india_folium_map,
    create_india_footfall_heatmap,
    plot_category_by_state,
    plot_location_type_distribution,
    apply_pbi_theme
)
from utils.data_analysis import get_state_summary

st.set_page_config(
    page_title="Geographical Analysis - India Tourism BI",
    page_icon="🗺️",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Geographical & Spatial Tourism Analysis",
    subtitle="Interactive India GIS mapping, regional tourism density, state-wise ratings, and expenditures",
    badge="POWER BI DASHBOARD 2 • GEOGRAPHY"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# GEOGRAPHICAL KPIS
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Active States", f"{filtered_df['State'].nunique()}", "Geographical units", "#0284c7", "🗺️")
with c2:
    render_kpi_card("Unique Destinations", f"{filtered_df['Place'].nunique()}", "Mapped landmarks", "#0d9488", "📍")
with c3:
    top_state = filtered_df['State'].value_counts().index[0]
    render_kpi_card("Top State Volume", f"{top_state}", f"{filtered_df['State'].value_counts().iloc[0]} records", "#f59e0b", "🏆")
with c4:
    top_region = filtered_df['Region'].value_counts().index[0] if 'Region' in filtered_df.columns else "South"
    render_kpi_card("Leading Tourism Zone", f"{top_region} India", "Regional cluster", "#6366f1", "🧭")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# INTERACTIVE FOLIUM MAP OF INDIA
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
    <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">
        📍 Interactive Geospatial Map of Indian Tourism Destinations
    </div>
    <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">
        Click on clusters or individual pins to inspect detailed ratings, average costs, location categories, and visitor volumes.
    </div>
</div>
""", unsafe_allow_html=True)

map_mode = st.radio(
    "Map layer",
    ["Destination clusters", "Estimated footfall heatmap"],
    horizontal=True,
    key="geography_map_mode",
)
folium_map = (
    create_india_folium_map(filtered_df)
    if map_mode == "Destination clusters"
    else create_india_footfall_heatmap(filtered_df)
)
st_folium(folium_map, width="100%", height=520)
if map_mode == "Estimated footfall heatmap":
    st.caption("Heat intensity is weighted by estimated visitor counts at destination coordinates; smoothing is a visual aid, not measured density between sites.")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# STATE LEVEL AGGREGATIONS & CHARTS
# -------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.plotly_chart(plot_category_by_state(filtered_df), use_container_width=True)

with col_chart2:
    st.plotly_chart(plot_location_type_distribution(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# STATE-WISE RATINGS & EXPENSES COMPARISON
# -------------------------------------------------------------
col_s1, col_s2 = st.columns(2)

state_summary = get_state_summary(filtered_df)

with col_s1:
    fig_rate = px.bar(
        state_summary.sort_values(by='Average_Rating', ascending=False),
        x='Average_Rating',
        y='State',
        orientation='h',
        text=state_summary.sort_values(by='Average_Rating', ascending=False)['Average_Rating'].apply(lambda x: f"⭐ {x:.2f}"),
        color='Average_Rating',
        color_continuous_scale=px.colors.sequential.Greens,
        title="State-wise Average Tourist Satisfaction Rating"
    )
    fig_rate.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_rate.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_rate), use_container_width=True)

with col_s2:
    fig_cost = px.bar(
        state_summary.sort_values(by='Average_Cost_INR', ascending=False),
        x='Average_Cost_INR',
        y='State',
        orientation='h',
        text=state_summary.sort_values(by='Average_Cost_INR', ascending=False)['Average_Cost_INR'].apply(lambda x: f"₹{int(x):,}"),
        color='Average_Cost_INR',
        color_continuous_scale=px.colors.sequential.Oranges,
        title="State-wise Average Estimated Travel Cost (INR)"
    )
    fig_cost.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_cost.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_cost), use_container_width=True)

# -------------------------------------------------------------
# DETAILED STATE SUMMARY TABLE
# -------------------------------------------------------------
with st.expander("📊 Complete State-wise Analytical Matrix", expanded=False):
    display_state = state_summary.copy()
    display_state['Average_Rating'] = display_state['Average_Rating'].round(2)
    display_state['Average_Cost_INR'] = display_state['Average_Cost_INR'].round().astype(int)
    display_state['Average_Popularity'] = display_state['Average_Popularity'].round(2)
    st.dataframe(display_state, use_container_width=True)

