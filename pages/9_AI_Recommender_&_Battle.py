"""
Dashboard 9: AI Recommender, Head-to-Head Destination Battle & 3D Analytics
Academic WOW Factors: Multi-criteria Decision Analysis, Comparative Benchmarking, and 3D Visual Modeling
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
from utils.data_analysis import compute_smart_recommendations, get_destination_summary
from utils.visualizations import (
    plot_3d_opportunity_matrix,
    plot_destination_battle_radar,
    apply_pbi_theme
)

st.set_page_config(
    page_title="Smart Recommender & 3D Analytics - India Tourism BI",
    page_icon="✨",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Smart Recommender, Destination Battle & 3D Analytics",
    subtitle="Algorithmic Multi-Criteria Decision Analysis (MCDA), Head-to-Head Destination Benchmarking, and 3D Opportunity Space",
    badge="ACADEMIC INNOVATION • WOW FACTORS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# THREE INTERACTIVE WOW TABS
# -------------------------------------------------------------
tab_rec, tab_battle, tab_3d = st.tabs([
    "🤖 Smart Destination Matcher (MCDA Engine)",
    "⚔️ Head-to-Head Destination Battle",
    "🌐 3D Interactive Tourism Space"
])

# -------------------------------------------------------------
# TAB 1: SMART DESTINATION RECOMMENDER
# -------------------------------------------------------------
with tab_rec:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-left: 4px solid #0284c7;">
        <h3 style="margin: 0 0 4px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
            🎯 Algorithmic Multi-Criteria Destination Recommender
        </h3>
        <div style="font-size: 12.5px; color: #64748b;">
            Customize your travel preferences to compute algorithmic match scores across all 20 Indian destinations based on category affinity, budget viability, and historical cohort satisfaction.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_in1, c_in2, c_in3, c_in4 = st.columns(4)

    with c_in1:
        rec_theme = st.selectbox("Preferred Tourism Theme", ["Any Theme", "Nature", "Historical", "Cultural", "Beach", "Adventure"], index=0)
    with c_in2:
        rec_party = st.selectbox("Travel Group Persona", ["Couple", "Family", "Friends", "Solo", "Organized Group"], index=0)
    with c_in3:
        rec_budget = st.slider("Target Budget Ceiling (INR)", min_value=1000, max_value=6000, value=3000, step=250)
    with c_in4:
        rec_season = st.selectbox("Target Season", ["All Seasons", "Winter", "Summer", "Monsoon", "Spring"], index=0)

    recommendations = compute_smart_recommendations(filtered_df, rec_theme, rec_party, rec_budget, rec_season)

    if recommendations:
        st.markdown(f"#### 🏆 Top Recommended Matches (Evaluated out of {len(recommendations)} destinations)")
        top_3 = recommendations[:3]

        rec_cols = st.columns(3)
        medals = ["🥇 Best Match", "🥈 Top Alternative", "🥉 Value Pick"]
        card_borders = ["#0284c7", "#10b981", "#f97316"]

        for idx, item in enumerate(top_3):
            with rec_cols[idx]:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-top: 4px solid {card_borders[idx]}; height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: {card_borders[idx]}; text-transform: uppercase;">{medals[idx]}</span>
                        <span style="font-size: 14px; font-weight: 800; background: #e0f2fe; color: #0369a1; padding: 2px 10px; border-radius: 9999px;">
                            {item['Match_Score']}% MATCH
                        </span>
                    </div>
                    <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin-bottom: 2px;">{item['Place']}</div>
                    <div style="font-size: 12.5px; color: #64748b; margin-bottom: 12px;">📍 {item['State']} &bull; <b>{item['Category']}</b> ({item['Location_Type']})</div>
                    <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 10px 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; margin-bottom: 12px;">
                        <div><b>Avg Rating:</b> ⭐ {item['Avg_Rating']}/5.0</div>
                        <div><b>Avg Cost:</b> ₹{item['Avg_Cost']:,}</div>
                        <div><b>Cleanliness:</b> 🧼 {item['Cleanliness']}/5.0</div>
                        <div><b>Safety:</b> 🛡️ {item['Safety']}/5.0</div>
                    </div>
                    <div style="font-size: 11.5px; color: #334155; background: #f8fafc; border-radius: 8px; padding: 8px 10px; line-height: 1.5;">
                        <b>Algorithmic Match Factors:</b><br>
                        &bull; {'<br>&bull; '.join(item['Justifications'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No destinations matched the specified criteria.")

# -------------------------------------------------------------
# TAB 2: HEAD-TO-HEAD DESTINATION BATTLE
# -------------------------------------------------------------
with tab_battle:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-left: 4px solid #f97316;">
        <h3 style="margin: 0 0 4px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
            ⚔️ Head-to-Head Destination Benchmarking Matrix
        </h3>
        <div style="font-size: 12.5px; color: #64748b;">
            Select any two destinations to compare tourist satisfaction, cost efficiency, safety, cleanliness, and recommendation rates side-by-side.
        </div>
    </div>
    """, unsafe_allow_html=True)

    dest_list = sorted(filtered_df['Place'].unique().tolist())
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        dest_a = st.selectbox("Select Contender A", dest_list, index=0)
    with b_col2:
        default_b_idx = 1 if len(dest_list) > 1 else 0
        dest_b = st.selectbox("Select Contender B", dest_list, index=default_b_idx)

    # Compute statistics for each
    records_a = filtered_df[filtered_df['Place'] == dest_a]
    records_b = filtered_df[filtered_df['Place'] == dest_b]

    def get_dest_stats(rec):
        return {
            'Rating': round(rec['Rating'].mean(), 2),
            'Cost': int(round(rec['Estimated_Cost_INR'].mean())),
            'Stay': round(rec['Stay_Days'].mean(), 1),
            'Popularity': round(rec['Popularity_Score'].mean(), 1),
            'Cleanliness': round(rec['Cleanliness_Rating'].mean(), 2),
            'Safety': round(rec['Safety_Rating'].mean(), 2),
            'Accessibility': round(rec['Accessibility_Rating'].mean(), 2),
            'Recommendation': round((rec['Recommended'] == 'Yes').mean() * 100, 1),
            'Total_Visits': len(rec),
            'Category': rec['Category'].iloc[0] if not rec.empty else "N/A",
            'State': rec['State'].iloc[0] if not rec.empty else "N/A"
        }

    stats_a = get_dest_stats(records_a)
    stats_b = get_dest_stats(records_b)

    # Side-by-side KPI comparison cards
    card_a_col, card_b_col = st.columns(2)

    with card_a_col:
        st.markdown(f"""
        <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 12px; padding: 18px; margin-bottom: 14px;">
            <div style="font-size: 11px; font-weight: 800; color: #1d4ed8; text-transform: uppercase;">CONTENDER A</div>
            <div style="font-size: 24px; font-weight: 800; color: #0f172a;">{dest_a}</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">{stats_a['State']} &bull; {stats_a['Category']}</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                <div><b>Rating:</b> ⭐ {stats_a['Rating']}/5.0</div>
                <div><b>Avg Cost:</b> ₹{stats_a['Cost']:,}</div>
                <div><b>Cleanliness:</b> 🧼 {stats_a['Cleanliness']}/5.0</div>
                <div><b>Safety:</b> 🛡️ {stats_a['Safety']}/5.0</div>
                <div><b>Popularity:</b> {stats_a['Popularity']}/100</div>
                <div><b>Recommended:</b> {stats_a['Recommendation']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with card_b_col:
        st.markdown(f"""
        <div style="background: #fff7ed; border: 2px solid #f97316; border-radius: 12px; padding: 18px; margin-bottom: 14px;">
            <div style="font-size: 11px; font-weight: 800; color: #c2410c; text-transform: uppercase;">CONTENDER B</div>
            <div style="font-size: 24px; font-weight: 800; color: #0f172a;">{dest_b}</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">{stats_b['State']} &bull; {stats_b['Category']}</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                <div><b>Rating:</b> ⭐ {stats_b['Rating']}/5.0</div>
                <div><b>Avg Cost:</b> ₹{stats_b['Cost']:,}</div>
                <div><b>Cleanliness:</b> 🧼 {stats_b['Cleanliness']}/5.0</div>
                <div><b>Safety:</b> 🛡️ {stats_b['Safety']}/5.0</div>
                <div><b>Popularity:</b> {stats_b['Popularity']}/100</div>
                <div><b>Recommended:</b> {stats_b['Recommendation']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radar Comparison Chart
    radar_fig = plot_destination_battle_radar(dest_a, dest_b, stats_a, stats_b)
    st.plotly_chart(radar_fig, use_container_width=True)

    # Analytical Verdict Box
    winner_rating = dest_a if stats_a['Rating'] > stats_b['Rating'] else (dest_b if stats_b['Rating'] > stats_a['Rating'] else "Tie")
    winner_cost = dest_a if stats_a['Cost'] < stats_b['Cost'] else (dest_b if stats_b['Cost'] < stats_a['Cost'] else "Tie")
    winner_clean = dest_a if stats_a['Cleanliness'] > stats_b['Cleanliness'] else (dest_b if stats_b['Cleanliness'] > stats_a['Cleanliness'] else "Tie")

    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-top: 10px;">
        <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">⚖️ Analytical Benchmark Summary:</div>
        <div style="font-size: 12.5px; color: #334155; line-height: 1.6;">
            &bull; <b>Higher Tourist Satisfaction:</b> <span style="color: #0284c7; font-weight: 700;">{winner_rating}</span><br>
            &bull; <b>More Cost-Effective:</b> <span style="color: #10b981; font-weight: 700;">{winner_cost}</span> (₹{min(stats_a['Cost'], stats_b['Cost']):,} vs ₹{max(stats_a['Cost'], stats_b['Cost']):,})<br>
            &bull; <b>Superior Sanitation / Cleanliness:</b> <span style="color: #f97316; font-weight: 700;">{winner_clean}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: 3D INTERACTIVE TOURISM OPPORTUNITY SPACE
# -------------------------------------------------------------
with tab_3d:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-left: 4px solid #8b5cf6;">
        <h3 style="margin: 0 0 4px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
            🌐 3D Interactive Multi-Metric Opportunity Space
        </h3>
        <div style="font-size: 12.5px; color: #64748b;">
            Click, hold, and drag with your mouse to rotate the 3D space in real-time. Scroll to zoom. Bubble sizes represent total visitor counts.
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_3d = plot_3d_opportunity_matrix(filtered_df)
    st.plotly_chart(fig_3d, use_container_width=True)

    st.markdown("""
    **How to Interpret the 3D Space during your Laboratory Presentation:**
    * **Sweet Spot (Upper-Left Zone):** High Satisfaction (Rating > 4.5) + Low Expense (< ₹2,000). Represents high-value tourism opportunities.
    * **Premium Cluster (Right Zone):** Higher travel expenses with steady popularity and specialized experiences.
    * **Bubble Volume:** Demonstrates absolute footfall scaling alongside multidimensional quality metrics.
    """)

