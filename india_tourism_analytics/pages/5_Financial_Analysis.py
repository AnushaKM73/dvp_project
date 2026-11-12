"""
Dashboard 5: Financial Analysis
Expense modeling, budget optimization, cost vs duration correlation, and interactive trip budget calculator
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
    plot_cost_by_category,
    plot_cost_by_state,
    plot_cost_vs_stay
)
from utils.data_analysis import get_budget_destinations

st.set_page_config(
    page_title="Financial Analysis - India Tourism BI",
    page_icon="💰",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Financial & Travel Expense Analysis",
    subtitle="Travel cost distribution, state expenditures, cost elasticity, and interactive budget simulator",
    badge="POWER BI DASHBOARD 5 • FINANCIAL ANALYTICS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# FINANCIAL KPIS
# -------------------------------------------------------------
avg_cost = int(round(filtered_df['Estimated_Cost_INR'].mean()))
min_cost = int(filtered_df['Estimated_Cost_INR'].min())
max_cost = int(filtered_df['Estimated_Cost_INR'].max())
avg_stay = round(filtered_df['Stay_Days'].mean(), 1)
daily_burn = int(round(avg_cost / avg_stay)) if avg_stay > 0 else avg_cost

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Average Trip Expense", f"₹{avg_cost:,}", "Overall mean spend", "#0284c7", "💳")
with c2:
    render_kpi_card("Lowest Recorded Cost", f"₹{min_cost:,}", "Minimum budget package", "#10b981", "🏷️")
with c3:
    render_kpi_card("Highest Recorded Cost", f"₹{max_cost:,}", "Maximum premium spend", "#ec4899", "💎")
with c4:
    render_kpi_card("Est. Daily Expenditure", f"₹{daily_burn:,}/day", f"Based on {avg_stay} days avg stay", "#f97316", "⏱️")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ROW 1: COST BY CATEGORY & COST BY STATE
# -------------------------------------------------------------
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.plotly_chart(plot_cost_by_category(filtered_df), use_container_width=True)

with col_c2:
    st.plotly_chart(plot_cost_by_state(filtered_df, top_n=10), use_container_width=True)

# -------------------------------------------------------------
# ROW 2: COST VS STAY DURATION CORRELATION
# -------------------------------------------------------------
st.plotly_chart(plot_cost_vs_stay(filtered_df), use_container_width=True)

# -------------------------------------------------------------
# INTERACTIVE TRIP BUDGET SIMULATOR
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 4px solid #10b981;">
    <h3 style="margin: 0 0 6px 0; font-size: 17px; font-weight: 700; color: #0f172a;">
        🎯 Interactive Destination Budget Matcher
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Slide or enter your maximum budget threshold in INR to dynamically discover matching Indian destinations.
    </p>
""", unsafe_allow_html=True)

col_input, col_stats = st.columns([1, 2])

with col_input:
    user_budget = st.slider(
        "Maximum Budget (INR)",
        min_value=min_cost,
        max_value=max_cost,
        value=min(3000, max_cost),
        step=200,
        help="Select a ceiling budget to filter eligible destinations."
    )

budget_results = get_budget_destinations(filtered_df, user_budget)

with col_stats:
    if not budget_results.empty:
        matched_count = len(budget_results)
        cheapest_match = budget_results.iloc[0]['Place']
        cheapest_val = int(budget_results.iloc[0]['Avg_Cost'])
        st.markdown(f"""
        <div style="display: flex; gap: 16px; margin-top: 10px;">
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px; flex: 1;">
                <div style="font-size: 11px; font-weight: 700; color: #166534;">MATCHING DESTINATIONS</div>
                <div style="font-size: 20px; font-weight: 800; color: #15803d;">{matched_count} Places</div>
                <div style="font-size: 11px; color: #166534;">Within ₹{user_budget:,} budget</div>
            </div>
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px 14px; flex: 1;">
                <div style="font-size: 11px; font-weight: 700; color: #1e40af;">MOST AFFORDABLE MATCH</div>
                <div style="font-size: 20px; font-weight: 800; color: #1d4ed8;">{cheapest_match}</div>
                <div style="font-size: 11px; color: #1e40af;">Avg cost: ₹{cheapest_val:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"No destinations found with an estimated cost below ₹{user_budget:,}. Try expanding your budget.")

if not budget_results.empty:
    display_budget = budget_results.copy()
    display_budget['Avg_Cost'] = display_budget['Avg_Cost'].round().astype(int)
    display_budget['Min_Cost'] = display_budget['Min_Cost'].round().astype(int)
    display_budget['Max_Cost'] = display_budget['Max_Cost'].round().astype(int)
    display_budget['Avg_Rating'] = display_budget['Avg_Rating'].round(2)
    display_budget['Avg_Stay'] = display_budget['Avg_Stay'].round(1)

    st.dataframe(
        display_budget.rename(columns={
            'Place': 'Destination',
            'Avg_Cost': 'Average Cost (₹)',
            'Min_Cost': 'Min (₹)',
            'Max_Cost': 'Max (₹)',
            'Avg_Rating': 'Rating (⭐)',
            'Avg_Stay': 'Avg Stay (Days)',
            'Records': 'Sample Trips'
        }),
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# INTERACTIVE TRIP COST CALCULATOR & ESTIMATOR
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 4px solid #0284c7;">
    <h3 style="margin: 0 0 6px 0; font-size: 17px; font-weight: 700; color: #0f172a;">
        🧮 Interactive Custom Trip Cost Estimator
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Model customized trip budgets by selecting a destination, party size, duration, and comfort tier based on empirical dataset averages.
    </p>
""", unsafe_allow_html=True)

all_dest_list = sorted(filtered_df['Place'].unique().tolist())
calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)

with calc_c1:
    calc_dest = st.selectbox("Destination", all_dest_list, index=0)
with calc_c2:
    num_travelers = st.number_input("Number of Travelers", min_value=1, max_value=20, value=2, step=1)
with calc_c3:
    trip_days = st.number_input("Trip Duration (Days)", min_value=1, max_value=30, value=3, step=1)
with calc_c4:
    comfort_tier = st.selectbox("Travel Comfort Tier", ["Budget (0.7x)", "Standard (1.0x)", "Premium / Luxury (1.8x)"], index=1)

multiplier = 0.7 if "Budget" in comfort_tier else (1.8 if "Luxury" in comfort_tier else 1.0)
dest_data = filtered_df[filtered_df['Place'] == calc_dest]
base_cost = dest_data['Estimated_Cost_INR'].mean() if not dest_data.empty else filtered_df['Estimated_Cost_INR'].mean()
base_stay = dest_data['Stay_Days'].mean() if not dest_data.empty else filtered_df['Stay_Days'].mean()

daily_rate = (base_cost / base_stay) if base_stay > 0 else 600
estimated_person = int(round(daily_rate * trip_days * multiplier))
total_projected = int(round(estimated_person * num_travelers))

st.markdown(f"""
<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-top: 14px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">PROJECTED TOTAL TRIP EXPENSE</div>
            <div style="font-size: 28px; font-weight: 800; color: #0284c7;">₹{total_projected:,}</div>
            <div style="font-size: 12px; color: #64748b;">For {num_travelers} traveler(s) for {trip_days} day(s) at {calc_dest} ({comfort_tier})</div>
        </div>
        <div style="display: flex; gap: 20px;">
            <div style="text-align: right;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b;">COST PER PERSON</div>
                <div style="font-size: 18px; font-weight: 700; color: #0f172a;">₹{estimated_person:,}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b;">DAILY BURN / PERSON</div>
                <div style="font-size: 18px; font-weight: 700; color: #10b981;">₹{int(estimated_person / trip_days):,}/day</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


