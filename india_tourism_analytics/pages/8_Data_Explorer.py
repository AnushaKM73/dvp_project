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
# POWER BI DESKTOP IMPORT GUIDE
# -------------------------------------------------------------
with st.expander("💼 Power BI Desktop Integration & Modeling Instructions", expanded=True):
    st.markdown("""
    ### How to import into Power BI Desktop for your Laboratory Presentation:
    
    1. **Importing the Generated Datasets:**
       * Open **Power BI Desktop**.
       * Click **Get Data** &rarr; **Excel Workbook** &rarr; Select `India_Tourism_BI_Report.xlsx` (or **Text/CSV** for individual summary files in `exports/`).
       * Check `Cleaned_Data`, `Destination_Master`, `State_Analysis`, `Category_Insights`, and `Monthly_Trends`.
       * Click **Load**.
    
    2. **Suggested Star-Schema Relationships:**
       * **Fact Table:** `Cleaned_Data` (Foreign Keys: `Place`, `State`, `Category`).
       * **Dimension Tables:**
         * `Destination_Master` &rarr; One-to-Many on `Place`.
         * `State_Analysis` &rarr; One-to-Many on `State`.
         * `Category_Insights` &rarr; One-to-Many on `Category`.
    
    3. **Suggested Power BI Report Pages:**
       * **Page 1: Executive Overview:** Cards for Total Records, Unique Places, Avg Rating, Avg Cost; Slicers for State & Category.
       * **Page 2: Geospatial Distribution:** Map visual using `Place`, `State`, `Latitude`, and `Longitude`.
       * **Page 3: Demographic Profiles:** Clustered bar charts for Age Group, Gender, and Travel Party.
       * **Page 4: Financial & Quality Matrix:** Scatter plot of Cost vs Stay Duration and Cleanliness/Safety clustered bars.
    """)

