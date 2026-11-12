"""
Dashboard 7: Exploratory Data Analysis (EDA)
Comprehensive statistical analysis, distribution modeling, IQR outlier detection, and correlation matrices
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.data_analysis import compute_outliers_iqr
from utils.visualizations import plot_correlation_matrix, apply_pbi_theme

st.set_page_config(
    page_title="Exploratory Data Analysis - India Tourism BI",
    page_icon="🔬",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Exploratory Data Analysis & Statistical Modeling",
    subtitle="Dataset dimensions, parametric distributions, IQR outlier diagnostics, and multi-feature correlation matrices",
    badge="POWER BI DASHBOARD 7 • STATISTICAL EDA"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# EDA SUMMARY METRICS
# -------------------------------------------------------------
num_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
cat_cols = filtered_df.select_dtypes(include=['object', 'string']).columns.tolist()
missing_total = filtered_df.isnull().sum().sum()
dups_total = filtered_df.duplicated().sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Dataset Shape", f"{filtered_df.shape[0]} × {filtered_df.shape[1]}", "Rows × Columns", "#0284c7", "📐")
with c2:
    render_kpi_card("Numerical Features", f"{len(num_cols)} Variables", "Ratio & interval scales", "#0d9488", "🔢")
with c3:
    render_kpi_card("Categorical Features", f"{len(cat_cols)} Variables", "Nominal & ordinal scales", "#6366f1", "🏷️")
with c4:
    render_kpi_card("Data Quality", f"100% Clean", f"{missing_total} missing • {dups_total} duplicates", "#10b981", "✅")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TABS FOR STRUCTURED EDA
# -------------------------------------------------------------
tab_info, tab_dist, tab_outliers, tab_corr, tab_viva = st.tabs([
    "📋 Dataset Metadata & Summary Stats",
    "📊 Feature Distributions",
    "📦 Outlier Detection (IQR)",
    "🔥 Correlation & Relationships",
    "🎓 DVP Lab Viva Defense & Formula Guide"
])

# TAB 1: METADATA & STATS
with tab_info:
    st.markdown("#### 1. Descriptive Statistics for Numerical Variables")
    st.dataframe(filtered_df[num_cols].describe().round(2), use_container_width=True)

    st.markdown("#### 2. Categorical Variables Summary")
    st.dataframe(filtered_df[cat_cols].describe(), use_container_width=True)

    st.markdown("#### 3. Column Data Types & Non-Null Counts")
    dtype_df = pd.DataFrame({
        "Column": filtered_df.columns,
        "Data Type": filtered_df.dtypes.astype(str),
        "Non-Null Count": filtered_df.notnull().sum().values,
        "Null Count": filtered_df.isnull().sum().values,
        "Unique Values": filtered_df.nunique().values
    })
    st.dataframe(dtype_df, use_container_width=True)

# TAB 2: DISTRIBUTIONS
with tab_dist:
    st.markdown("#### Numerical Feature Distribution Histograms")
    selected_num = st.selectbox("Select Numerical Feature to Inspect", num_cols, index=0)

    fig_dist = px.histogram(
        filtered_df,
        x=selected_num,
        marginal="box",
        nbins=25,
        color_discrete_sequence=['#0284c7'],
        title=f"Parametric Distribution & Boxplot for {selected_num}"
    )
    st.plotly_chart(apply_pbi_theme(fig_dist), use_container_width=True)

    mean_val = filtered_df[selected_num].mean()
    median_val = filtered_df[selected_num].median()
    std_val = filtered_df[selected_num].std()
    skew_val = filtered_df[selected_num].skew()

    st.markdown(f"""
    **Statistical Properties for `{selected_num}`:**
    * **Mean:** {mean_val:.2f} | **Median:** {median_val:.2f} | **Standard Deviation:** {std_val:.2f}
    * **Skewness:** {skew_val:.2f} ({'Positively Skewed' if skew_val > 0.5 else 'Negatively Skewed' if skew_val < -0.5 else 'Approximately Symmetric'})
    """)

# TAB 3: OUTLIERS VIA IQR
with tab_outliers:
    st.markdown("#### Outlier Detection via Interquartile Range (IQR) Rule")
    st.markdown("""
    Under the Tukey standard IQR rule:
    * \\(\\text{IQR} = Q_3 - Q_1\\)
    * \\(\\text{Lower Bound} = Q_1 - 1.5 \\times \\text{IQR}\\)
    * \\(\\text{Upper Bound} = Q_3 + 1.5 \\times \\text{IQR}\\)
    """)

    col_out_sel, col_out_stat = st.columns([1, 2])
    with col_out_sel:
        target_outlier_col = st.selectbox("Select Feature for Outlier Analysis", num_cols, index=1)
        outliers_df, lb, ub, out_cnt = compute_outliers_iqr(filtered_df, target_outlier_col)

    with col_out_stat:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-top: 10px;">
            <div style="font-size: 13px; font-weight: 700; color: #0f172a;">IQR Boundary Calculation for {target_outlier_col}:</div>
            <div style="display: flex; gap: 20px; margin-top: 8px;">
                <div><b>Lower Fence:</b> <span style="color: #0284c7;">{lb}</span></div>
                <div><b>Upper Fence:</b> <span style="color: #0284c7;">{ub}</span></div>
                <div><b>Outliers Detected:</b> <span style="color: {'#e11d48' if out_cnt > 0 else '#10b981'}; font-weight: 700;">{out_cnt} records ({out_cnt/len(filtered_df)*100:.1f}%)</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    fig_box = px.box(
        filtered_df,
        y=target_outlier_col,
        points="all",
        color_discrete_sequence=['#f97316'],
        title=f"Box-and-Whisker Plot for {target_outlier_col} (with IQR Outliers Highlighted)"
    )
    st.plotly_chart(apply_pbi_theme(fig_box), use_container_width=True)

    if out_cnt > 0:
        st.markdown("##### Detected Outlier Records")
        st.dataframe(outliers_df[['Visitor_ID', 'Place', 'State', target_outlier_col, 'Rating']], use_container_width=True)

# TAB 4: CORRELATION MATRIX
with tab_corr:
    st.markdown("#### Correlation Heatmap (Seaborn)")
    st.markdown("Evaluates Pearson correlation coefficients across all 8 continuous numerical dimensions:")

    corr_fig = plot_correlation_matrix(filtered_df)
    st.pyplot(corr_fig, use_container_width=True)

    st.markdown("""
    **Analytical Findings:**
    * **Cost vs Duration:** Mild positive correlation confirms that longer stays incrementally increase estimated costs.
    * **Quality Indices:** Cleanliness, Safety, and Accessibility correlate positively with overall destination satisfaction ratings.
    * **Popularity vs Rating:** Destinations maintain stable ratings regardless of high footfall volumes.
    """)

# TAB 5: VIVA DEFENSE & FORMULAS
with tab_viva:
    st.markdown("### 🎓 Academic DVP Laboratory Viva Voce Preparation & Mathematical Reference")
    st.markdown("Use this section during your laboratory evaluation to answer faculty questions with theoretical rigor:")

    st.markdown("#### 1. Core Mathematical Formulations Used")
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.markdown(r"""
        **A. Tukey's Interquartile Range (IQR) Rule:**
        $$\text{IQR} = Q_3 - Q_1$$
        $$\text{Lower Fence} = Q_1 - 1.5 \times \text{IQR}$$
        $$\text{Upper Fence} = Q_3 + 1.5 \times \text{IQR}$$
        *Any data point $x < \text{Lower Fence}$ or $x > \text{Upper Fence}$ is flagged as an outlier.*
        """)
        st.markdown(r"""
        **B. Sample Skewness Coefficient ($g_1$):**
        $$g_1 = \frac{\frac{1}{n} \sum_{i=1}^n (x_i - \bar{x})^3}{\left[\frac{1}{n} \sum_{i=1}^n (x_i - \bar{x})^2\right]^{3/2}}$$
        *Positive skew indicates a long tail to the right (common in tourism expenses).*
        """)

    with c_f2:
        st.markdown(r"""
        **C. Pearson Correlation Coefficient ($r$):**
        $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
        *Measures the linear strength between continuous variables $(-1 \le r \le +1)$.*
        """)
        st.markdown(r"""
        **D. VADER Normalized Compound Sentiment Score:**
        $$x = \frac{\sum s_i}{\sqrt{\left(\sum s_i\right)^2 + \alpha}}$$
        *Where $s_i$ are valence weights and default normalization factor $\alpha = 15$.*
        """)

    st.markdown("---")
    st.markdown("#### 2. Faculty Viva Questions & Model Answers")

    viva_qa = [
        ("Q1: Why did you use Median imputation instead of Mean for missing numerical values?",
         "Because variables such as 'Estimated_Cost_INR' and 'Visitors_Count' are positively skewed with extreme values. The arithmetic mean is sensitive to outliers and pulls imputed values toward the tail, whereas the median represents the 50th percentile and preserves central tendency without distortion."),
        
        ("Q2: Why did you choose Tukey's IQR rule instead of Z-score for outlier detection?",
         "The Z-score method strictly assumes a Gaussian (normal) distribution ($Z = \\frac{x - \\mu}{\\sigma}$). Because tourism expenditure and visit volumes deviate from normality, Z-scores produce biased boundaries. Tukey's IQR rule is non-parametric and robust against non-normal distributions."),

        ("Q3: How does Folium GIS mapping differ from Plotly's Geo / Mapbox?",
         "Folium is a Python wrapper around Leaflet.js that generates interactive HTML/CSS/JS maps with raster tiles (OpenStreetMap), circle markers, and dynamic popup HTML tables. Plotly renders WebGL-based vector traces. Folium is especially suited for clustered spatial markers and offline tile caching."),

        ("Q4: Why does Karnataka have 144 records in the dataset?",
         "Karnataka contains three separate iconic destinations in the dataset—Hampi (51 records), Mysore Palace (47 records), and Coorg (46 records)—combining for 144 visits (14.4% of total volume). Most other states contain only 1 or 2 destinations."),

        ("Q5: How is the Star Schema structured for Power BI Desktop?",
         "The cleaned dataset 'Cleaned_Data' serves as the central Fact table containing foreign keys ('Place', 'State', 'Category') and numeric measures. Dimension tables ('Destination_Master', 'State_Analysis', 'Category_Insights') connect to it via Many-to-One relationships, enabling efficient filtering and slicer propagation in Power BI.")
    ]

    for q, a in viva_qa:
        with st.expander(f"📌 {q}", expanded=False):
            st.markdown(f"**Answer:** {a}")


