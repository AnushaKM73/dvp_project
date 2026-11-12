"""
India Tourism Analytics and Business Intelligence Dashboard
Academic Project for Data Visualization with Python (DVP) Laboratory
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
from utils.insights import generate_automated_insights
from utils.visualizations import (
    plot_state_distribution,
    plot_category_distribution,
    plot_monthly_trend
)

# Page Configuration
st.set_page_config(
    page_title="India Tourism Analytics & BI Dashboard",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Power BI Theme
apply_theme()

# Sidebar Global Filters
filtered_df = render_sidebar_filters()

# Header Banner
render_page_header(
    title="INDIA TOURISM ANALYTICS & BUSINESS INTELLIGENCE DASHBOARD",
    subtitle="Discover Destinations • Analyse Tourism • Visualize Insights • College DVP Laboratory Project",
    badge="ACADEMIC DVP PROJECT • PYTHON & POWER BI ARCHITECTURE"
)

# -------------------------------------------------------------
# WOW FACTOR: 1-CLICK FACULTY DEMO PRESETS
# -------------------------------------------------------------
with st.expander("🎓 Faculty Laboratory Viva & Instant Demo Presets (Click to Auto-Slice)", expanded=False):
    st.markdown("<div style='font-size: 13px; color: #64748b; margin-bottom: 8px;'>Demonstrate dynamic real-time slicer recalculations across all KPIs, charts, and insights with a single click:</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    if p_col1.button("🎒 Preset: Solo & Adventure", use_container_width=True):
        st.session_state['filter_categories'] = ['Adventure']
        st.session_state['filter_travel_groups'] = ['Solo']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col2.button("👨‍👩‍👧 Preset: Heritage Family", use_container_width=True):
        st.session_state['filter_categories'] = ['Historical', 'Cultural']
        st.session_state['filter_travel_groups'] = ['Family']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col3.button("🌴 Preset: South India Circuit", use_container_width=True):
        st.session_state['filter_states'] = ['Karnataka', 'Kerala', 'Tamil Nadu']
        st.session_state['filters_applied'] = True
        st.rerun()

    if p_col4.button("🔄 Reset to Full Dataset", use_container_width=True):
        st.session_state['filter_states'] = []
        st.session_state['filter_categories'] = []
        st.session_state['filter_location_types'] = []
        st.session_state['filter_seasons'] = []
        st.session_state['filter_months'] = []
        st.session_state['filter_age_groups'] = []
        st.session_state['filter_genders'] = []
        st.session_state['filter_travel_groups'] = []
        st.session_state['filter_recommended'] = []
        st.session_state['filters_applied'] = False
        st.rerun()

# -------------------------------------------------------------
# EXECUTIVE KPI CARDS ROW
# -------------------------------------------------------------
kpis = compute_executive_kpis(filtered_df)

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    render_kpi_card("Total Records", f"{kpis['total_records']:,}", "Verified visits", border_color="#0284c7", icon="📋")
with col2:
    render_kpi_card("Total States", f"{kpis['total_states']}", "Pan-India coverage", border_color="#0d9488", icon="🗺️")
with col3:
    render_kpi_card("Destinations", f"{kpis['unique_destinations']}", "Iconic landmarks", border_color="#6366f1", icon="📍")
with col4:
    render_kpi_card("Avg Rating", f"⭐ {kpis['avg_rating']}", "Out of 5.0 scale", border_color="#f59e0b", icon="🌟")
with col5:
    render_kpi_card("Avg Est. Cost", f"₹{int(kpis['avg_cost']):,}", "Per tourist expense", border_color="#10b981", icon="💰")
with col6:
    render_kpi_card("Avg Stay", f"{kpis['avg_stay']} Days", "Duration per trip", border_color="#ec4899", icon="⏱️")
with col7:
    render_kpi_card("Recommended", f"{kpis['recommendation_pct']}%", "Positive advocacy", border_color="#14b8a6", icon="👍")

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# AUTOMATED TOURISM INSIGHTS
# -------------------------------------------------------------
st.markdown("""
<div style="margin: 16px 0 10px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">
    <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
        💡 Automated Tourism Business Insights
        <span style="font-size: 11px; font-weight: 600; color: #0284c7; background: #e0f2fe; padding: 2px 8px; border-radius: 9999px;">
            Calculated Dynamically via Python
        </span>
    </h3>
</div>
""", unsafe_allow_html=True)

insights = generate_automated_insights(filtered_df)
if insights:
    # Render insights in 5 columns x 2 rows
    row1 = insights[:5]
    row2 = insights[5:]

    cols_r1 = st.columns(5)
    for idx, ins in enumerate(row1):
        with cols_r1[idx]:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 12px; height: 160px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 3px solid {ins['color']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 11px; font-weight: 700; color: {ins['color']}; text-transform: uppercase;">{ins['badge']}</span>
                    <span>{ins['icon']}</span>
                </div>
                <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">{ins['title']}</div>
                <div style="font-size: 15px; font-weight: 800; color: #0284c7; margin-bottom: 6px;">{ins['value']}</div>
                <div style="font-size: 11px; color: #64748b; line-height: 1.4;">{ins['detail']}</div>
            </div>
            """, unsafe_allow_html=True)

    cols_r2 = st.columns(5)
    for idx, ins in enumerate(row2):
        with cols_r2[idx]:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 12px; height: 160px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 3px solid {ins['color']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 11px; font-weight: 700; color: {ins['color']}; text-transform: uppercase;">{ins['badge']}</span>
                    <span>{ins['icon']}</span>
                </div>
                <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">{ins['title']}</div>
                <div style="font-size: 15px; font-weight: 800; color: #0284c7; margin-bottom: 6px;">{ins['value']}</div>
                <div style="font-size: 11px; color: #64748b; line-height: 1.4;">{ins['detail']}</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# QUICK INTERACTIVE VISUALIZATION PREVIEW
# -------------------------------------------------------------
st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
col_left, col_mid, col_right = st.columns([1.4, 1, 1.2])

with col_left:
    st.plotly_chart(plot_state_distribution(filtered_df, top_n=8), use_container_width=True)

with col_mid:
    st.plotly_chart(plot_category_distribution(filtered_df), use_container_width=True)

with col_right:
    st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# DVP LABORATORY & DATA CLEANING AUDIT SUMMARY
# -------------------------------------------------------------
with st.expander("🔬 DVP Laboratory Data Cleaning Pipeline & Preprocessing Audit", expanded=False):
    audit = st.session_state.get('audit', {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw Rows Processed", audit.get('initial_rows', 1000))
    c2.metric("Clean Columns Cast", audit.get('final_cols', 25))
    c3.metric("Record #1 Munnar Clean", "Active" if audit.get('first_record_corrected') else "Raw")
    c4.metric("Duplicates Identified", audit.get('duplicates_removed', 0))

    st.markdown("""
    **Preprocessing Applied for Laboratory Demonstration:**
    1. **First Record Correction (Python Logic):** Visitor V0001 (Munnar, Kerala) repaired with verified attributes.
    2. **Type Casting:** Numerical features converted from text strings into proper `float64` and `int64`.
    3. **Missing Value Imputation:** Numerical missing values imputed using feature **median**; categorical missing values imputed using feature **mode**.
    4. **Geographical Coordinates:** Exact latitude and longitude coordinates attached for the 20 Indian destinations for mapping.
    """)

# -------------------------------------------------------------
# NAVIGATION PORTAL CARDS
# -------------------------------------------------------------
st.markdown("""
<div style="margin: 20px 0 10px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">
    <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">
        📊 Analytics Module Navigation
    </h3>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(4)
pages = [
    ("1. Executive Overview", "pages/1_Executive_Overview.py", "Complete high-level KPI indicators and interactive distribution charts.", "📈"),
    ("2. Geographical Analysis", "pages/2_Geographical_Analysis.py", "Interactive Folium India map, regional breakdowns, and state rankings.", "🗺️"),
    ("3. Tourist Demographics", "pages/3_Tourist_Demographics.py", "Age cohorts, gender split, travel group preferences, and heatmaps.", "👥"),
    ("4. Tourism Performance", "pages/4_Tourism_Performance.py", "Destination ratings, popularity scores, cleanliness, and safety rankings.", "⭐"),
    ("5. Financial Analysis", "pages/5_Financial_Analysis.py", "Budget analysis, travel expense modeling, and interactive budget simulator.", "💰"),
    ("6. Review Analytics", "pages/6_Review_Analytics.py", "Text mining, review word clouds, and tourist satisfaction search engine.", "💬"),
    ("7. Exploratory Data Analysis", "pages/7_Exploratory_Data_Analysis.py", "Statistical EDA, outlier detection via IQR, and correlation matrix.", "🔬"),
    ("8. Data Explorer & Power BI", "pages/8_Data_Explorer.py", "Complete searchable dataset, Power BI exports, and Excel workbook downloads.", "📥"),
    ("9. Smart AI Recommender & 3D", "pages/9_AI_Recommender_&_Battle.py", "MCDA algorithmic trip matcher, head-to-head battle, and 3D visual space.", "✨")
]

for idx, (title, page_file, desc, icon) in enumerate(pages):
    with nav_cols[idx % 4]:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 12px; height: 130px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 18px; margin-bottom: 4px;">{icon}</div>
            <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">{title}</div>
            <div style="font-size: 11.5px; color: #64748b; line-height: 1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 30px; padding: 16px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
    <b>INDIA TOURISM ANALYTICS AND BUSINESS INTELLIGENCE DASHBOARD</b> • College DVP Laboratory Project<br>
    Built with Python, Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Folium & OpenPyXL.
</div>
""", unsafe_allow_html=True)

