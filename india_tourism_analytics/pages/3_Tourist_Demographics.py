"""
Dashboard 3: Tourist Demographics
Audience segmentation, travel group dynamics, and behavioral insights
"""

import streamlit as st
import pandas as pd
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.visualizations import (
    plot_age_distribution,
    plot_gender_distribution,
    plot_travel_group_distribution,
    plot_age_vs_travel_heatmap,
    plot_seasonal_distribution,
    plot_monthly_trend
)

st.set_page_config(
    page_title="Tourist Demographics - India Tourism BI",
    page_icon="👥",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Tourist Demographics & Persona Analysis",
    subtitle="Behavioral profiling across age cohorts, gender identities, travel party compositions, and seasonal demand",
    badge="POWER BI DASHBOARD 3 • VISITOR DEMOGRAPHICS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# DEMOGRAPHIC KPIS
# -------------------------------------------------------------
top_age = filtered_df['Age_Group'].value_counts().index[0]
top_age_cnt = filtered_df['Age_Group'].value_counts().iloc[0]

top_group = filtered_df['Travel_Group'].value_counts().index[0]
top_group_cnt = filtered_df['Travel_Group'].value_counts().iloc[0]

top_gender = filtered_df['Gender'].value_counts().index[0]
top_gender_cnt = filtered_df['Gender'].value_counts().iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Dominant Age Cohort", f"{top_age}", f"{top_age_cnt} travelers ({top_age_cnt/len(filtered_df)*100:.1f}%)", "#0284c7", "🎯")
with c2:
    render_kpi_card("Primary Travel Style", f"{top_group}", f"{top_group_cnt} bookings ({top_group_cnt/len(filtered_df)*100:.1f}%)", "#0d9488", "👥")
with c3:
    render_kpi_card("Leading Gender Group", f"{top_gender}", f"{top_gender_cnt} respondents ({top_gender_cnt/len(filtered_df)*100:.1f}%)", "#6366f1", "👤")
with c4:
    solo_count = (filtered_df['Travel_Group'] == 'Solo').sum()
    render_kpi_card("Solo Travelers", f"{solo_count}", f"{solo_count/len(filtered_df)*100:.1f}% of total market", "#ec4899", "🎒")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ROW 1: AGE, GENDER & TRAVEL GROUP
# -------------------------------------------------------------
col_a, col_g, col_t = st.columns([1.2, 1, 1.2])

with col_a:
    st.plotly_chart(plot_age_distribution(filtered_df), use_container_width=True)

with col_g:
    st.plotly_chart(plot_gender_distribution(filtered_df), use_container_width=True)

with col_t:
    st.plotly_chart(plot_travel_group_distribution(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# ROW 2: AGE VS TRAVEL GROUP HEATMAP & SEASONAL DEMAND
# -------------------------------------------------------------
col_heat, col_season = st.columns([1.4, 1.2])

with col_heat:
    st.plotly_chart(plot_age_vs_travel_heatmap(filtered_df), use_container_width=True)

with col_season:
    st.plotly_chart(plot_seasonal_distribution(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# UNDERSTANDING TOURIST BEHAVIOUR SECTION
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-left: 4px solid #0284c7;">
    <h3 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 700; color: #0f172a;">
        🧠 Understanding Tourist Behaviour & Cohort Dynamics
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Algorithmic behavioral synthesis generated dynamically from the underlying dataset:
    </p>
""", unsafe_allow_html=True)

# Generate observations dynamically
obs_cols = st.columns(3)

# Group with highest spend
group_spend = filtered_df.groupby('Travel_Group')['Estimated_Cost_INR'].mean().sort_values(ascending=False)
highest_spend_group = group_spend.index[0]
highest_spend_val = int(group_spend.iloc[0])

# Age group with highest rating
age_rating = filtered_df.groupby('Age_Group')['Rating'].mean().sort_values(ascending=False)
highest_rating_age = age_rating.index[0]
highest_rating_val = round(age_rating.iloc[0], 2)

# Category preferred by couples
couple_df = filtered_df[filtered_df['Travel_Group'] == 'Couple']
fav_couple_cat = couple_df['Category'].value_counts().index[0] if not couple_df.empty else "Nature"

with obs_cols[0]:
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
        <div style="font-size: 12px; font-weight: 700; color: #0284c7;">HIGHEST SPENDING SEGMENT</div>
        <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0;">{highest_spend_group}</div>
        <div style="font-size: 12px; color: #64748b;">Average expenditure of <b>₹{highest_spend_val:,}</b> per visit, making them the primary target for premium packages.</div>
    </div>
    """, unsafe_allow_html=True)

with obs_cols[1]:
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
        <div style="font-size: 12px; font-weight: 700; color: #10b981;">MOST SATISFIED COHORT</div>
        <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0;">Age {highest_rating_age}</div>
        <div style="font-size: 12px; color: #64748b;">Registers the highest average rating of <b>⭐ {highest_rating_val}/5.0</b> across destination categories.</div>
    </div>
    """, unsafe_allow_html=True)

with obs_cols[2]:
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
        <div style="font-size: 12px; font-weight: 700; color: #f97316;">COUPLE TRAVEL PREFERENCE</div>
        <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0;">{fav_couple_cat} Tourism</div>
        <div style="font-size: 12px; color: #64748b;">Couples disproportionately gravitate towards <b>{fav_couple_cat}</b> escapes with Scenic backdrops and moderate stays.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

