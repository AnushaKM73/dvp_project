"""
Power BI Compatibility and Report Generation Engine
Exports multi-tab Excel workbooks, Power BI-ready CSV tables, and laboratory reports.
"""

import os
import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from utils.data_analysis import (
    compute_executive_kpis,
    get_state_summary,
    get_destination_summary,
    get_category_summary,
    get_monthly_trends,
    get_seasonal_summary
)


def export_powerbi_tables(df, export_dir="exports"):
    """
    Generate Power BI-ready star-schema / snowflake-compatible summary tables.
    Saves individual CSVs into the exports/ folder.
    """
    os.makedirs(export_dir, exist_ok=True)
    generated_files = {}

    # 1. Destination Master Table
    dest_df = get_destination_summary(df)
    dest_path = os.path.join(export_dir, "power_bi_destination_master.csv")
    dest_df.to_csv(dest_path, index=False)
    generated_files["Destination_Master"] = dest_path

    # 2. State Summary Table
    state_df = get_state_summary(df)
    state_path = os.path.join(export_dir, "power_bi_state_summary.csv")
    state_df.to_csv(state_path, index=False)
    generated_files["State_Summary"] = state_path

    # 3. Category Summary Table
    cat_df = get_category_summary(df)
    cat_path = os.path.join(export_dir, "power_bi_category_summary.csv")
    cat_df.to_csv(cat_path, index=False)
    generated_files["Category_Summary"] = cat_path

    # 4. Monthly Trends Table
    monthly_df = get_monthly_trends(df)
    monthly_path = os.path.join(export_dir, "power_bi_monthly_trends.csv")
    monthly_df.to_csv(monthly_path, index=False)
    generated_files["Monthly_Trends"] = monthly_path

    # 5. Visitor Demographics Table
    demo_df = df.groupby(['Age_Group', 'Gender', 'Travel_Group']).agg(
        Tourist_Count=('Visitor_ID', 'count'),
        Avg_Rating=('Rating', 'mean'),
        Avg_Expense_INR=('Estimated_Cost_INR', 'mean'),
        Avg_Stay_Days=('Stay_Days', 'mean')
    ).reset_index()
    demo_path = os.path.join(export_dir, "power_bi_visitor_demographics.csv")
    demo_df.to_csv(demo_path, index=False)
    generated_files["Visitor_Demographics"] = demo_path

    # 6. Financial Summary Table
    fin_df = df.groupby(['Category', 'Location_Type']).agg(
        Records=('Visitor_ID', 'count'),
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Min_Cost=('Estimated_Cost_INR', 'min'),
        Max_Cost=('Estimated_Cost_INR', 'max'),
        Avg_Stay=('Stay_Days', 'mean')
    ).reset_index()
    fin_path = os.path.join(export_dir, "power_bi_financial_summary.csv")
    fin_df.to_csv(fin_path, index=False)
    generated_files["Financial_Summary"] = fin_path

    return generated_files


def generate_excel_bi_workbook(df):
    """
    Generate a styled, multi-tab Excel workbook containing executive KPIs,
    cleaned dataset, and aggregated dimension tables.
    Returns bytes buffer for Streamlit download.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Sheet 1: Executive KPIs
        kpis = compute_executive_kpis(df)
        kpi_df = pd.DataFrame(list(kpis.items()), columns=['KPI_Metric', 'Value'])
        kpi_df.to_excel(writer, sheet_name='Executive_KPIs', index=False)

        # Sheet 2: Cleaned Raw Data
        df.to_excel(writer, sheet_name='Cleaned_Data', index=False)

        # Sheet 3: Destination Master
        dest_summary = get_destination_summary(df)
        dest_summary.to_excel(writer, sheet_name='Destination_Master', index=False)

        # Sheet 4: State Analysis
        state_summary = get_state_summary(df)
        state_summary.to_excel(writer, sheet_name='State_Analysis', index=False)

        # Sheet 5: Category Insights
        cat_summary = get_category_summary(df)
        cat_summary.to_excel(writer, sheet_name='Category_Insights', index=False)

        # Sheet 6: Monthly Trends
        month_summary = get_monthly_trends(df)
        month_summary.to_excel(writer, sheet_name='Monthly_Trends', index=False)

        # Apply OpenPyXL styles to sheets
        workbook = writer.book
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        for sheet in workbook.worksheets:
            sheet.views.sheetView[0].showGridLines = True
            for col_idx, col in enumerate(sheet.columns, 1):
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col_idx)
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
                # Style header
                first_cell = sheet.cell(row=1, column=col_idx)
                first_cell.fill = header_fill
                first_cell.font = header_font
                first_cell.alignment = Alignment(horizontal="center", vertical="center")

    buffer.seek(0)
    # Also save to disk in exports/ folder
    os.makedirs("exports", exist_ok=True)
    with open(os.path.join("exports", "India_Tourism_BI_Report.xlsx"), "wb") as f:
        f.write(buffer.getvalue())

    buffer.seek(0)
    return buffer


def generate_markdown_brief(df):
    """Generate a structured Markdown laboratory report brief."""
    kpis = compute_executive_kpis(df)
    state_sum = get_state_summary(df)
    dest_sum = get_destination_summary(df)

    top_state = state_sum.iloc[0]['State'] if not state_sum.empty else "N/A"
    top_state_recs = state_sum.iloc[0]['Total_Records'] if not state_sum.empty else 0
    top_dest = dest_sum.iloc[0]['Place'] if not dest_sum.empty else "N/A"
    top_dest_rating = dest_sum.iloc[0]['Average_Rating'] if not dest_sum.empty else 0.0

    md = f"""# INDIA TOURISM ANALYTICS & BUSINESS INTELLIGENCE REPORT
**Course:** Data Visualization with Python (DVP) Laboratory Project  
**Generated Scope:** {len(df):,} verified records across {kpis['total_states']} States and {kpis['unique_destinations']} Iconic Destinations

---

## 1. Executive Performance Metrics
* **Total Tourist Volume:** {kpis['total_records']:,} records
* **Pan-India Geographic Coverage:** {kpis['total_states']} States / UTs ({kpis['unique_destinations']} landmark sites)
* **Average Tourist Satisfaction:** ⭐ {kpis['avg_rating']:.2f} / 5.00
* **Average Estimated Expenditure:** ₹{int(kpis['avg_cost']):,} per traveler
* **Average Trip Duration:** {kpis['avg_stay']:.1f} Days
* **Traveler Recommendation Rate:** {kpis['recommendation_pct']:.1f}%

---

## 2. Market Leadership & Benchmarks
* **Top Tourism State:** **{top_state}** ({top_state_recs} records, {top_state_recs/len(df)*100:.1f}% of sample)
* **Top Footfall Destination:** **{top_dest}** (Satisfaction Rating: ⭐ {top_dest_rating:.2f}/5.0)
* **Quality Indices:** Cleanliness: {kpis['avg_cleanliness']:.2f}/5.0 | Safety: {kpis['avg_safety']:.2f}/5.0 | Accessibility: {kpis['avg_accessibility']:.2f}/5.0

---

## 3. Preprocessing & Data Cleaning Highlights
1. **Malformed Record #1 Fixed:** Repaired Munnar, Kerala (`Visitor_ID: V0001`) with verified numeric and categorical attributes.
2. **Median Imputation:** Numerical missing values imputed via feature median to resist skewness.
3. **Mode Imputation:** Categorical missing values imputed via statistical mode.
4. **GIS Integration:** Validated GPS coordinates mapped for all 20 Indian tourist destinations.

*Report automatically generated by India Tourism Insights BI Engine.*
"""
    return md


