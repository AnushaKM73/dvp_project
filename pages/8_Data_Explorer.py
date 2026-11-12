"""
Dashboard 8: Data Explorer & Power BI Integration Hub
Complete searchable dataset, pagination, diagnostic reporting, and Power BI report downloads
"""

import streamlit as st
import pandas as pd
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.report_generator import (
    export_powerbi_tables,
    generate_excel_bi_workbook,
    generate_markdown_brief
)

st.set_page_config(
    page_title="Data Explorer & Power BI Hub - India Tourism BI",
    page_icon="📥",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Data Explorer & Power BI Export Hub",
    subtitle="Full dataset access, pagination, schema diagnostics, Power BI tables generation, and multi-sheet Excel reports",
    badge="POWER BI DASHBOARD 8 • DATA MANAGEMENT & EXPORTS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# EXPORT ACTIONS ROW
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-left: 4px solid #0284c7;">
    <h3 style="margin: 0 0 6px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
        📦 Export Verified Data & Business Intelligence Reports
    </h3>
    <div style="font-size: 12.5px; color: #64748b; margin-bottom: 14px;">
        Download presentation-ready datasets for faculty demonstration or Power BI Desktop reporting.
    </div>
""", unsafe_allow_html=True)

col_d1, col_d2, col_d3, col_d4 = st.columns(4)

# 1. Download Cleaned CSV
with col_d1:
    cleaned_csv = st.session_state.get('cleaned_df', filtered_df).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Cleaned CSV (5dvp_cleaned.csv)",
        data=cleaned_csv,
        file_name="5dvp_cleaned.csv",
        mime="text/csv",
        use_container_width=True
    )

# 2. Download Filtered CSV
with col_d2:
    filtered_csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"🔍 Filtered CSV ({len(filtered_df):,} rows)",
        data=filtered_csv,
        file_name="5dvp_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

# 3. Download Power BI Multi-Tab Excel Workbook
with col_d3:
    excel_buffer = generate_excel_bi_workbook(filtered_df)
    st.download_button(
        label="📊 Power BI Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="India_Tourism_BI_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# 4. Download Executive Markdown Brief
with col_d4:
    md_brief = generate_markdown_brief(filtered_df).encode('utf-8')
    st.download_button(
        label="📝 Executive Brief (.md)",
        data=md_brief,
        file_name="India_Tourism_Executive_Summary.md",
        mime="text/markdown",
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# INTERACTIVE SEARCH & PAGINATION CONTROLS
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
    <h3 style="margin: 0 0 14px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
        🔎 Interactive Search & Data Browser
    </h3>
""", unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1])

with col_s1:
    search_query = st.text_input("Universal Record Search", placeholder="Search destination, state, review, visitor ID...")

with col_s2:
    page_size = st.selectbox("Rows per page", [15, 25, 50, 100], index=0)

display_data = filtered_df.copy()

if search_query.strip():
    mask = display_data.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
    display_data = display_data[mask]

total_display_rows = len(display_data)
total_pages = max(1, (total_display_rows + page_size - 1) // page_size)

with col_s3:
    current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (current_page - 1) * page_size
end_idx = min(start_idx + page_size, total_display_rows)

st.markdown(f"""
<div style="font-size: 12.5px; color: #64748b; margin-bottom: 10px;">
    Showing records <b>{start_idx + 1 if total_display_rows > 0 else 0}</b> to <b>{end_idx}</b> of <b>{total_display_rows:,}</b> (Page {current_page} of {total_pages})
</div>
""", unsafe_allow_html=True)

page_slice = display_data.iloc[start_idx:end_idx]
st.dataframe(page_slice, use_container_width=True, height=420)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# BUSINESS INTELLIGENCE STUDIO: POWER BI & TABLEAU HUB
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 4px solid #f59e0b;">
    <h3 style="margin: 0 0 6px 0; font-size: 18px; font-weight: 700; color: #0f172a;">
        💼 Business Intelligence Studio: Power BI & Tableau Integration Hub
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Export-ready star schemas, DAX measures, Tableau calculated fields, and multi-sheet models for laboratory evaluation.
    </p>
""", unsafe_allow_html=True)

bi_tab_pbi, bi_tab_tab = st.tabs([
    "📊 Power BI Desktop Integration & DAX Measures",
    "📈 Tableau Desktop & Public Integration"
])

with bi_tab_pbi:
    st.markdown("""
    #### 1. Power BI Star-Schema Data Model
    * **Fact Table:** `Cleaned_Data` (Foreign Keys: `Place`, `State`, `Category`, `Visit_Month`)
    * **Dimension Tables:**
      * `Destination_Master` &rarr; Many-to-One relationship on `[Place]`
      * `State_Analysis` &rarr; Many-to-One relationship on `[State]`
      * `Category_Insights` &rarr; Many-to-One relationship on `[Category]`
      * `Monthly_Trends` &rarr; Many-to-One relationship on `[Visit_Month]`
    """)

    st.markdown("#### 2. Ready-to-Use Power BI DAX Measures:")
    st.code("""
// Total Tourist Volume
Total Tourists = COUNTROWS('Cleaned_Data')

// Average Tourist Satisfaction
Average Rating = AVERAGE('Cleaned_Data'[Rating])

// Average Travel Expenditure
Average Travel Cost = AVERAGE('Cleaned_Data'[Estimated_Cost_INR])

// Overall Traveler Recommendation %
Recommendation Rate = 
DIVIDE(
    CALCULATE(COUNTROWS('Cleaned_Data'), 'Cleaned_Data'[Recommended] = "Yes"),
    COUNTROWS('Cleaned_Data'),
    0
) * 100

// Karnataka Market Share %
Karnataka Volume Share = 
DIVIDE(
    CALCULATE(COUNTROWS('Cleaned_Data'), 'Cleaned_Data'[State] = "Karnataka"),
    COUNTROWS('Cleaned_Data'),
    0
) * 100
    """, language="dax")

    st.markdown("""
    #### 3. Power BI Report Layout Recommendations:
    * **Page 1: Executive KPI Dashboard:** Multi-row KPI cards, State Volume bar chart, Category donut.
    * **Page 2: Geospatial View:** Map visual using `Latitude` & `Longitude` with bubbles sized by `Visitors_Count`.
    * **Page 3: Quality Matrix:** Clustered column chart comparing Cleanliness, Safety, and Accessibility by Category.
    """)

with bi_tab_tab:
    st.markdown("""
    #### 1. Connecting Data in Tableau Desktop / Tableau Public
    1. Open **Tableau** &rarr; **Connect to Data** &rarr; **Text File** &rarr; Select `exports/tableau_tourism_dataset.csv`.
    2. Set Geographic Roles: `State` &rarr; State/Province, `Latitude` &rarr; Latitude, `Longitude` &rarr; Longitude.
    """)

    st.markdown("#### 2. Tableau Calculated Fields:")
    st.code("""
// A. Recommendation Rate (%)
SUM(IIF([Recommended] = "Yes", 1, 0)) / COUNT([Visitor ID])

// B. Daily Expense (INR / Day)
[Estimated Cost INR] / [Stay Days]

// C. Cost Category Tier
IF [Estimated Cost INR] < 2000 THEN "Budget (< ₹2,000)"
ELSEIF [Estimated Cost INR] <= 3500 THEN "Moderate (₹2,000 - ₹3,500)"
ELSE "Luxury (> ₹3,500)"
END
    """, language="text")

    st.markdown("""
    #### 3. Tableau Worksheets to Demonstrate:
    * **Sheet 1 (Geospatial Symbol Map):** `Latitude` vs `Longitude` on rows/columns, marks colored by `Category` and sized by `Visitors Count`.
    * **Sheet 2 (Dual-Axis Monthly Chart):** `Visit Month` on columns, `COUNT(Visitor ID)` line chart on primary axis and `AVG(Estimated Cost INR)` bar chart on secondary axis.
    * **Sheet 3 (Performance Treemap):** Hierarchical treemap grouped by `Category` &rarr; `Location Type` &rarr; `Place`.
    """)

    # Direct download for Tableau CSV
    try:
        with open("exports/tableau_tourism_dataset.csv", "rb") as tab_f:
            st.download_button(
                label="📥 Download Tableau-Optimized Dataset (tableau_tourism_dataset.csv)",
                data=tab_f.read(),
                file_name="tableau_tourism_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )
    except Exception:
        pass

st.markdown("</div>", unsafe_allow_html=True)

