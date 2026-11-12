"""
Dashboard 4: Tourism Performance
Destination benchmarking, ratings, popularity scores, and service quality indices
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.visualizations import (
    plot_rating_vs_popularity_scatter,
    plot_quality_radar,
    apply_pbi_theme
)
from utils.data_analysis import get_destination_summary

st.set_page_config(
    page_title="Tourism Performance - India Tourism BI",
    page_icon="⭐",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Destination Performance & Quality Benchmarks",
    subtitle="Evaluating tourist satisfaction, popularity indices, cleanliness, safety, and accessibility standards",
    badge="POWER BI DASHBOARD 4 • PERFORMANCE"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# PERFORMANCE KPIS
# -------------------------------------------------------------
dest_summary = get_destination_summary(filtered_df)

top_rated = dest_summary.sort_values(by='Average_Rating', ascending=False).iloc[0]
most_pop = dest_summary.sort_values(by='Popularity_Score', ascending=False).iloc[0]
avg_clean = filtered_df['Cleanliness_Rating'].mean()
avg_safety = filtered_df['Safety_Rating'].mean()

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Top Rated Landmark", f"{top_rated['Place']}", f"⭐ {top_rated['Average_Rating']:.2f}/5.0 ({top_rated['State']})", "#10b981", "⭐")
with c2:
    render_kpi_card("Most Popular Place", f"{most_pop['Place']}", f"Score: {most_pop['Popularity_Score']:.1f}/100", "#f97316", "🔥")
with c3:
    render_kpi_card("Avg Cleanliness Index", f"{avg_clean:.2f} / 5.0", "Sanitation benchmark", "#0284c7", "🧼")
with c4:
    render_kpi_card("Avg Safety Index", f"{avg_safety:.2f} / 5.0", "Security benchmark", "#0d9488", "🛡️")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ROW 1: TOP 10 RATED VS TOP 10 POPULAR
# -------------------------------------------------------------
col_r1, col_r2 = st.columns(2)

with col_r1:
    top10_rated = dest_summary.sort_values(by='Average_Rating', ascending=False).head(10)
    fig_tr = px.bar(
        top10_rated,
        x='Average_Rating',
        y='Place',
        orientation='h',
        text=top10_rated['Average_Rating'].apply(lambda x: f"⭐ {x:.2f}"),
        color='Average_Rating',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 10 Highest-Rated Indian Destinations"
    )
    fig_tr.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_tr.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_tr), use_container_width=True)

with col_r2:
    top10_pop = dest_summary.sort_values(by='Popularity_Score', ascending=False).head(10)
    fig_tp = px.bar(
        top10_pop,
        x='Popularity_Score',
        y='Place',
        orientation='h',
        text=top10_pop['Popularity_Score'].apply(lambda x: f"{x:.1f}"),
        color='Popularity_Score',
        color_continuous_scale=px.colors.sequential.Sunset,
        title="Top 10 Most Popular Destinations by Footfall Index"
    )
    fig_tp.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_tp.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_tp), use_container_width=True)

# -------------------------------------------------------------
# ROW 2: SCATTER PLOT & QUALITY MATRIX
# -------------------------------------------------------------
col_scat, col_quad = st.columns([1.3, 1])

with col_scat:
    st.plotly_chart(plot_rating_vs_popularity_scatter(filtered_df), use_container_width=True)

with col_quad:
    st.plotly_chart(plot_quality_radar(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# DESTINATION DEEP-DIVE INSPECTOR & CARD SHOWCASE
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 4px solid #6366f1;">
    <h3 style="margin: 0 0 6px 0; font-size: 17px; font-weight: 700; color: #0f172a;">
        🔎 Individual Destination Deep-Dive Inspector
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Select any destination to inspect verified ratings, cleanliness, safety, accessibility scores, best season, and sample visitor reviews.
    </p>
""", unsafe_allow_html=True)

avail_places = sorted(filtered_df['Place'].unique().tolist())
selected_dest = st.selectbox("Select Landmark to Inspect", avail_places, index=0)

dest_records = filtered_df[filtered_df['Place'] == selected_dest]
first_row = dest_records.iloc[0]

card_col1, card_col2 = st.columns([1.2, 2])

with card_col1:
    cat_badge_color = {
        'Nature': '#10b981', 'Cultural': '#f97316', 'Historical': '#6366f1',
        'Beach': '#06b6d4', 'Adventure': '#e11d48'
    }.get(first_row['Category'], '#0284c7')

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px;">
        <span style="background: {cat_badge_color}; color: white; padding: 3px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase;">
            {first_row['Category']}
        </span>
        <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin: 10px 0 2px 0;">{selected_dest}</div>
        <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">📍 {first_row['Address']}</div>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
        <div style="font-size: 12px; line-height: 1.8; color: #334155;">
            <div><b>Location Type:</b> {first_row['Location_Type']}</div>
            <div><b>Best Time to Visit:</b> {first_row['Best_Time_to_Visit']}</div>
            <div><b>Total Visit Logs:</b> {len(dest_records)}</div>
            <div><b>Recommendation Rate:</b> {(dest_records['Recommended'] == 'Yes').mean()*100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with card_col2:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Rating", f"⭐ {dest_records['Rating'].mean():.2f}")
    m2.metric("Popularity", f"{dest_records['Popularity_Score'].mean():.1f}/100")
    m3.metric("Avg Cost", f"₹{int(dest_records['Estimated_Cost_INR'].mean()):,}")
    m4.metric("Avg Stay", f"{dest_records['Stay_Days'].mean():.1f} Days")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    g1.metric("Cleanliness Index", f"🧼 {dest_records['Cleanliness_Rating'].mean():.2f} / 5.0")
    g2.metric("Safety Index", f"🛡️ {dest_records['Safety_Rating'].mean():.2f} / 5.0")
    g3.metric("Accessibility", f"♿ {dest_records['Accessibility_Rating'].mean():.2f} / 5.0")

    st.markdown("##### Recent Visitor Reviews:")
    sample_reviews = dest_records[['Visitor_ID', 'Rating', 'Travel_Group', 'Review']].head(3)
    for _, rev in sample_reviews.iterrows():
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 12.5px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <b>{rev['Visitor_ID']}</b> ({rev['Travel_Group']})
                <span style="color: #f59e0b; font-weight: 700;">⭐ {rev['Rating']}</span>
            </div>
            <div style="color: #475569; font-style: italic;">"{rev['Review']}"</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# COMPLETE DESTINATION PERFORMANCE SCORECARD TABLE
# -------------------------------------------------------------
with st.expander("📋 Detailed Destination Performance Scorecard", expanded=False):
    scorecard = dest_summary[[
        'Place', 'State', 'Category', 'Total_Records', 'Average_Rating',
        'Popularity_Score', 'Cleanliness', 'Safety', 'Accessibility', 'Recommendation_Rate'
    ]].copy()
    scorecard['Average_Rating'] = scorecard['Average_Rating'].round(2)
    scorecard['Popularity_Score'] = scorecard['Popularity_Score'].round(2)
    scorecard['Cleanliness'] = scorecard['Cleanliness'].round(2)
    scorecard['Safety'] = scorecard['Safety'].round(2)
    scorecard['Accessibility'] = scorecard['Accessibility'].round(2)
    scorecard['Recommendation_Rate'] = scorecard['Recommendation_Rate'].round(1).astype(str) + "%"

    st.dataframe(scorecard, use_container_width=True)
