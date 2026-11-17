"""
India Tourism Analytics and Business Intelligence Dashboard
Academic Project for Data Visualization with Python (DVP) Laboratory
"""

import streamlit as st
import pandas as pd
import importlib
from streamlit_folium import st_folium
import utils.visualizations as visualization_module

# Streamlit can rerun app.py with a previously imported helper module still cached.
# Reload it when the main dashboard's newer chart helpers are missing.
if not all(hasattr(visualization_module, name) for name in (
    "plot_visitor_pattern_sankey",
    "plot_destination_cost_rating",
)):
    importlib.reload(visualization_module)

from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.data_analysis import compute_executive_kpis
from utils.insights import generate_automated_insights
from utils.visualizations import (
    plot_monthly_trend,
    plot_segment_metric,
    plot_destination_sunburst,
    plot_visitor_pattern_sankey,
    plot_destination_cost_rating,
    plot_seasonal_distribution,
    plot_recommendation_pie,
    create_india_folium_map,
    create_india_footfall_heatmap,
    plot_category_by_state,
    plot_location_type_distribution,
    plot_age_distribution,
    plot_gender_distribution,
    plot_travel_group_distribution,
    plot_age_vs_travel_heatmap,
    plot_rating_vs_popularity_scatter,
    plot_quality_radar,
    plot_cost_vs_stay,
    plot_correlation_matrix
)

# Page Configuration
st.set_page_config(
    page_title="India Tourism Analytics | DVP Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Power BI Dashboard Theme
apply_theme()

# Sidebar Global Filters
filtered_df = render_sidebar_filters()

# Dashboard Control Bar
render_page_header(
    title="INDIA TOURISM, IN THE DATA",
    subtitle="Explore where visitors go, how they travel, and what shapes their experience.",
    badge="DVP LABORATORY • ACADEMIC DASHBOARD"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please reset or adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# QUICK INTERACTIVE SLICER PRESETS (VIVA DEMO BAR)
# -------------------------------------------------------------
with st.expander("⚡ Interactive Viva Slicer Presets (Click to Test Real-time Recalculations)", expanded=False):
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    if p_col1.button("🎒 Solo Adventure Cohort", use_container_width=True):
        st.session_state['filter_categories'] = ['Adventure']
        st.session_state['filter_travel_groups'] = ['Solo']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col2.button("👨‍👩‍👧 Heritage Family Circuit", use_container_width=True):
        st.session_state['filter_categories'] = ['Historical', 'Cultural']
        st.session_state['filter_travel_groups'] = ['Family']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col3.button("🌴 South India Region", use_container_width=True):
        st.session_state['filter_states'] = ['Karnataka', 'Kerala', 'Tamil Nadu']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col4.button("🔄 Reset All Filters", use_container_width=True):
        for key in ['filter_states', 'filter_categories', 'filter_location_types',
                    'filter_seasons', 'filter_months', 'filter_age_groups',
                    'filter_genders', 'filter_travel_groups', 'filter_recommended']:
            st.session_state[key] = []
        st.session_state['filters_applied'] = False
        st.rerun()

# -------------------------------------------------------------
# EXECUTIVE KPI SUMMARY METRIC CARDS
# -------------------------------------------------------------
kpis = compute_executive_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Visitor Records", f"{kpis['total_records']:,}", "Current filtered sample", "#0284c7", "📊")
with col2:
    render_kpi_card("Destinations", f"{kpis['unique_destinations']}", "Landmarks represented", "#0d9488", "📍")
with col3:
    render_kpi_card("Average Rating", f"⭐ {kpis['avg_rating']}", "Out of 5", "#f59e0b", "🌟")
with col4:
    render_kpi_card("Advocacy Rate", f"{kpis['recommendation_pct']}%", "Recommend: Yes", "#14b8a6", "👍")

state_counts = filtered_df['State'].value_counts()
top_state = state_counts.index[0]
top_state_count = int(state_counts.iloc[0])
top_place_scores = filtered_df.groupby('Place')['Popularity_Score'].mean().sort_values(ascending=False)
top_place = top_place_scores.index[0]
top_place_score = float(top_place_scores.iloc[0])
top_category_counts = filtered_df['Category'].value_counts()
top_category = top_category_counts.index[0]
top_category_share = float(top_category_counts.iloc[0] / len(filtered_df) * 100)

st.markdown("#### What stands out in this selection")
st.info(
    f"**{top_state}** has the most visitor records ({top_state_count:,}; "
    f"{top_state_count / len(filtered_df) * 100:.1f}% of this sample). "
    f"**{top_place}** has the highest average popularity score ({top_place_score:.1f}/100), "
    f"while **{top_category}** is the largest category ({top_category_share:.1f}%). "
    "These are descriptive patterns in the selected records."
)
st.caption(
    f"Also in this selection: {kpis['total_states']} states/UTs · "
    f"₹{int(kpis['avg_cost']):,} average estimated cost · {kpis['avg_stay']} average stay days."
)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# CORE ANALYTICAL DASHBOARD TABS
# -------------------------------------------------------------
tab_overview, tab_geo, tab_eda, tab_demo, tab_patterns, tab_insights = st.tabs([
    "📊 Executive Overview",
    "🗺️ Spatial GIS Map",
    "🔬 Statistical EDA & Correlation",
    "👥 Demographics & Cohorts",
    "🧭 Visitor Patterns Lab",
    "💡 Algorithmic Insights & Audit"
])

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW CHARTS
# -------------------------------------------------------------
with tab_overview:
    st.markdown("#### Compare destinations and visitor segments")
    control_dimension, control_metric = st.columns([1, 1.4])
    with control_dimension:
        selected_dimension = st.selectbox(
            "Break down by",
            ["Destination", "State", "Category", "Season", "Travel group", "Age group"],
        )
    with control_metric:
        selected_metric = st.selectbox(
            "Measure",
            [
                "Visitor records",
                "Estimated footfall",
                "Average rating",
                "Average estimated cost (INR)",
                "Average stay (days)",
                "Average popularity score",
            ],
        )
    st.plotly_chart(
        plot_segment_metric(filtered_df, selected_dimension, selected_metric),
        use_container_width=True,
    )
    st.caption("Counts describe records in this sample; averages and footfall use the selected dataset fields.")

    r2_c1, r2_c2 = st.columns([1.2, 1])
    with r2_c1:
        st.plotly_chart(plot_destination_sunburst(filtered_df), use_container_width=True)
    with r2_c2:
        st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        st.plotly_chart(plot_seasonal_distribution(filtered_df), use_container_width=True)
    with r3_c2:
        st.plotly_chart(plot_recommendation_pie(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# TAB 2: SPATIAL GIS MAPPING
# -------------------------------------------------------------
with tab_geo:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #0f172a;">📍 Pan-India Geospatial Destination Mapping</span>
        <span style="font-size: 12px; color: #64748b; margin-left: 10px;">Interactive Folium GIS Layer with category color badges and clustered coordinates</span>
    </div>
    """, unsafe_allow_html=True)

    map_mode = st.radio(
        "Map layer",
        ["Destination clusters", "Estimated footfall heatmap"],
        horizontal=True,
        key="overview_map_mode",
    )
    map_obj = (
        create_india_folium_map(filtered_df)
        if map_mode == "Destination clusters"
        else create_india_footfall_heatmap(filtered_df)
    )
    st_folium(map_obj, width=None, height=480)
    if map_mode == "Estimated footfall heatmap":
        st.caption("Heat intensity is weighted by estimated visitor counts at destination coordinates; smoothing is a visual aid, not measured density between sites.")

    g_c1, g_c2 = st.columns(2)
    with g_c1:
        st.plotly_chart(plot_category_by_state(filtered_df), use_container_width=True)
    with g_c2:
        st.plotly_chart(plot_location_type_distribution(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# TAB 3: STATISTICAL EDA & CORRELATION MATRIX
# -------------------------------------------------------------
with tab_eda:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #0f172a;">🔬 Statistical EDA, Multi-Variate Correlation & Benchmark Radars</span>
        <span style="font-size: 12px; color: #64748b; margin-left: 10px;">Pearson correlations, bivariate scatter models, and quality benchmarking</span>
    </div>
    """, unsafe_allow_html=True)

    eda_r1_c1, eda_r1_c2 = st.columns(2)
    with eda_r1_c1:
        corr_fig = plot_correlation_matrix(filtered_df)
        st.pyplot(corr_fig, use_container_width=True)
    with eda_r1_c2:
        st.plotly_chart(plot_quality_radar(filtered_df), use_container_width=True)

    eda_r2_c1, eda_r2_c2 = st.columns(2)
    with eda_r2_c1:
        st.plotly_chart(plot_cost_vs_stay(filtered_df), use_container_width=True)
    with eda_r2_c2:
        st.plotly_chart(plot_rating_vs_popularity_scatter(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# TAB 4: DEMOGRAPHICS & COHORT ANALYSIS
# -------------------------------------------------------------
with tab_demo:
    demo_r1_c1, demo_r1_c2 = st.columns(2)
    with demo_r1_c1:
        heat_fig = plot_age_vs_travel_heatmap(filtered_df)
        st.plotly_chart(heat_fig, use_container_width=True)
    with demo_r1_c2:
        st.plotly_chart(plot_age_distribution(filtered_df), use_container_width=True)

    demo_r2_c1, demo_r2_c2 = st.columns(2)
    with demo_r2_c1:
        st.plotly_chart(plot_travel_group_distribution(filtered_df), use_container_width=True)
    with demo_r2_c2:
        st.plotly_chart(plot_gender_distribution(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# TAB 5: VISITOR PATTERNS & DESTINATION VALUE
# -------------------------------------------------------------
with tab_patterns:
    st.markdown("### Follow visitor segments through the sample")
    st.caption(
        "Each link shows how many records share two adjacent attributes. "
        "Budget tiers are recalculated as sample-relative quartile groups (smaller selections show fewer tiers); "
        "the flow is descriptive and does not imply a causal or chronological journey."
    )
    st.plotly_chart(plot_visitor_pattern_sankey(filtered_df), use_container_width=True)

    st.markdown("### Compare destination cost and experience")
    st.caption(
        "Each point is a destination. Bubble size shows its record count in this sample; "
        "dashed lines mark the median destination cost and rating. Hover for details."
    )
    st.plotly_chart(plot_destination_cost_rating(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# TAB 6: ALGORITHMIC INSIGHTS & CLEANING AUDIT
# -------------------------------------------------------------
with tab_insights:
    insights = generate_automated_insights(filtered_df)
    if insights:
        cols_ins = st.columns(5)
        for idx, ins in enumerate(insights[:5]):
            with cols_ins[idx]:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 12px; height: 155px; border-top: 3px solid {ins['color']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 10px; font-weight: 700; color: {ins['color']}; text-transform: uppercase;">{ins['badge']}</span>
                        <span>{ins['icon']}</span>
                    </div>
                    <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 3px;">{ins['title']}</div>
                    <div style="font-size: 14px; font-weight: 800; color: #0284c7; margin-bottom: 4px;">{ins['value']}</div>
                    <div style="font-size: 11px; color: #64748b; line-height: 1.35;">{ins['detail']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("#### 🔬 DVP Preprocessing & Data Cleaning Audit")
    audit = st.session_state.get('audit', {})
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Raw Records Loaded", audit.get('initial_rows', 1000))
    a2.metric("Features Cleaned", audit.get('final_cols', 25))
    a3.metric("Record #1 (Munnar)", "Corrected" if audit.get('first_record_corrected') else "Raw")
    a4.metric("Duplicates Handled", audit.get('duplicates_removed', 0))
