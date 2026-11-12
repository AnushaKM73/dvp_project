"""
Dashboard 1: Executive Overview
Power BI-style Executive Dashboard with core KPIs and key distribution charts
"""

import streamlit as st
import pandas as pd
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.data_analysis import compute_executive_kpis
from utils.visualizations import (
    plot_state_distribution,
    plot_top_destinations,
    plot_category_distribution,
    plot_monthly_trend,
    plot_seasonal_distribution,
    plot_rating_distribution,
    plot_recommendation_pie
)

st.set_page_config(
    page_title="Executive Overview - India Tourism BI",
    page_icon="📈",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Executive Overview Dashboard",
    subtitle="High-level tourism performance, geographical volume, category mix, and seasonal patterns",
    badge="POWER BI DASHBOARD 1 • EXECUTIVE VIEW"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# KPI CARDS ROW
# -------------------------------------------------------------
kpis = compute_executive_kpis(filtered_df)

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
with c1:
    render_kpi_card("Total Records", f"{kpis['total_records']:,}", "Visitor logs", "#0284c7", "📋")
with c2:
    render_kpi_card("Total States", f"{kpis['total_states']}", "Pan-India presence", "#0d9488", "🗺️")
with c3:
    render_kpi_card("Destinations", f"{kpis['unique_destinations']}", "Landmarks", "#6366f1", "📍")
with c4:
    render_kpi_card("Avg Rating", f"⭐ {kpis['avg_rating']}", "Satisfaction (0-5)", "#f59e0b", "🌟")
with c5:
    render_kpi_card("Avg Cost", f"₹{int(kpis['avg_cost']):,}", "Estimated budget", "#10b981", "💰")
with c6:
    render_kpi_card("Avg Stay", f"{kpis['avg_stay']} Days", "Trip duration", "#ec4899", "⏱️")
with c7:
    render_kpi_card("Recommended", f"{kpis['recommendation_pct']}%", "Advocacy rate", "#14b8a6", "👍")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# CHARTS ROW 1: STATE VOLUME & TOP 10 DESTINATIONS
# -------------------------------------------------------------
r1_left, r1_right = st.columns(2)
with r1_left:
    st.plotly_chart(plot_state_distribution(filtered_df, top_n=10), use_container_width=True)

with r1_right:
    st.plotly_chart(plot_top_destinations(filtered_df, top_n=10), use_container_width=True)

# -------------------------------------------------------------
# CHARTS ROW 2: CATEGORY DONUT & MONTHLY TREND
# -------------------------------------------------------------
r2_left, r2_right = st.columns([1, 1.4])
with r2_left:
    st.plotly_chart(plot_category_distribution(filtered_df), use_container_width=True)

with r2_right:
    st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# CHARTS ROW 3: SEASONAL DISTRIBUTION, RATINGS, RECOMMENDATION
# -------------------------------------------------------------
r3_col1, r3_col2, r3_col3 = st.columns([1, 1.2, 1])

with r3_col1:
    st.plotly_chart(plot_seasonal_distribution(filtered_df), use_container_width=True)

with r3_col2:
    st.plotly_chart(plot_rating_distribution(filtered_df), use_container_width=True)

with r3_col3:
    st.plotly_chart(plot_recommendation_pie(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# EXECUTIVE NARRATIVE
# -------------------------------------------------------------
with st.expander("📝 Executive Summary & Strategic Takeaways", expanded=True):
    top_state = filtered_df['State'].value_counts().index[0]
    top_cat = filtered_df['Category'].value_counts().index[0]
    top_season = filtered_df['Season'].value_counts().index[0]
    avg_cost = int(filtered_df['Estimated_Cost_INR'].mean())

    st.markdown(f"""
    * **Market Leadership:** **{top_state}** leads with the highest concentration of tourist records under current filter selections.
    * **Preference Drivers:** **{top_cat}** tourism dominates consumer bookings, indicating strong traveler interest in cultural and environmental preservation.
    * **Seasonality Pattern:** The peak influx occurs in the **{top_season}** season, creating key opportunities for hospitality revenue management.
    * **Financial Envelope:** The portfolio exhibits an average spend of **₹{avg_cost:,}** per traveler with a high advocacy rate of **{kpis['recommendation_pct']}%**.
    """)

