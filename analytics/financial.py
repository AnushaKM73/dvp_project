"""
Financial & Travel Expense Analytics
"""

import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

PBI_PALETTE = ['#0284c7', '#0d9488', '#f97316', '#6366f1', '#10b981', '#ec4899', '#eab308', '#8b5cf6', '#14b8a6', '#f43f5e']

CHART_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=12, color="#1e293b"),
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(248,250,252,0.6)",
    margin=dict(l=45, r=30, t=45, b=40),
    hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#ffffff", font_family="Inter"),
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0")
)


def apply_theme(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


def fig_to_dict(fig):
    return json.loads(fig.to_json())


def get_financial_kpis(df):
    """Compute financial summary KPIs."""
    if df.empty:
        return {
            "avg_cost": 0,
            "min_cost": 0,
            "max_cost": 0,
            "avg_stay": 0.0,
            "daily_burn": 0
        }
    avg_cost = int(round(float(df['Estimated_Cost_INR'].mean())))
    min_cost = int(df['Estimated_Cost_INR'].min())
    max_cost = int(df['Estimated_Cost_INR'].max())
    avg_stay = round(float(df['Stay_Days'].mean()), 1)
    daily_burn = int(round(avg_cost / avg_stay)) if avg_stay > 0 else avg_cost

    return {
        "avg_cost": avg_cost,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "avg_stay": avg_stay,
        "daily_burn": daily_burn
    }


def get_financial_charts(df):
    """Generate charts and summary tables for Financial Analysis."""
    if df.empty:
        return {}

    # 1. Travel cost distribution (Histogram)
    fig_hist = px.histogram(
        df,
        x='Estimated_Cost_INR',
        nbins=25,
        color_discrete_sequence=['#0284c7'],
        title="Travel Cost Distribution (Estimated Budget in INR)"
    )
    fig_hist.update_layout(xaxis_title="Estimated Cost (₹ INR)", yaxis_title="Record Count")
    apply_theme(fig_hist)

    # 2. Cost by Category (Box / Bar)
    cat_cost = df.groupby('Category')['Estimated_Cost_INR'].mean().reset_index()
    cat_cost = cat_cost.sort_values(by='Estimated_Cost_INR', ascending=False)
    fig_cat_cost = px.bar(
        cat_cost,
        x='Category',
        y='Estimated_Cost_INR',
        text=cat_cost['Estimated_Cost_INR'].apply(lambda x: f"₹{int(round(x)):,}"),
        color='Category',
        color_discrete_sequence=PBI_PALETTE,
        title="Average Estimated Travel Cost by Tourism Category"
    )
    fig_cat_cost.update_traces(textposition='outside')
    fig_cat_cost.update_layout(showlegend=False, yaxis_title="Average Cost (₹ INR)")
    apply_theme(fig_cat_cost)

    # 3. Category Cost Extremes table
    cat_extremes = df.groupby('Category').agg(
        Min_Cost=('Estimated_Cost_INR', 'min'),
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Median_Cost=('Estimated_Cost_INR', 'median'),
        Max_Cost=('Estimated_Cost_INR', 'max'),
        Records=('Visitor_ID', 'count')
    ).reset_index()
    cat_extremes['Avg_Cost'] = cat_extremes['Avg_Cost'].round().astype(int)
    cat_extremes['Median_Cost'] = cat_extremes['Median_Cost'].round().astype(int)
    cat_extremes_records = cat_extremes.sort_values(by='Avg_Cost', ascending=False).to_dict(orient='records')

    # 4. State-wise Average Estimated Cost (Top 10)
    state_cost = df.groupby('State')['Estimated_Cost_INR'].mean().reset_index()
    state_cost = state_cost.sort_values(by='Estimated_Cost_INR', ascending=False).head(10)
    fig_state_cost = px.bar(
        state_cost,
        x='Estimated_Cost_INR',
        y='State',
        orientation='h',
        text=state_cost['Estimated_Cost_INR'].apply(lambda x: f"₹{int(round(x)):,}"),
        color='Estimated_Cost_INR',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 10 States by Average Estimated Destination Cost"
    )
    fig_state_cost.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, xaxis_title="Average Cost (₹ INR)")
    fig_state_cost.update_traces(textposition='outside')
    apply_theme(fig_state_cost)

    # 5. Estimated Cost vs Stay Duration (Scatter with trendline)
    # We sample if too large, or use full filtered set
    fig_scatter = px.scatter(
        df,
        x='Stay_Days',
        y='Estimated_Cost_INR',
        color='Category',
        hover_data=['Place', 'State', 'Rating'],
        color_discrete_sequence=PBI_PALETTE,
        title="Estimated Travel Cost vs. Stay Duration (Days)"
    )
    fig_scatter.update_layout(xaxis_title="Stay Duration (Days)", yaxis_title="Estimated Cost (₹ INR)")
    apply_theme(fig_scatter)

    return {
        "cost_distribution": fig_to_dict(fig_hist),
        "cost_by_category": fig_to_dict(fig_cat_cost),
        "cost_by_state": fig_to_dict(fig_state_cost),
        "cost_vs_stay": fig_to_dict(fig_scatter),
        "category_extremes": cat_extremes_records
    }


def match_destinations_by_budget(df, max_budget):
    """
    Interactive Destination Budget Matcher.
    Returns destinations with estimated cost within max_budget.
    """
    if df.empty:
        return {"count": 0, "cheapest": None, "results": []}

    dest_summary = df.groupby(['Place', 'State', 'Category']).agg(
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Min_Cost=('Estimated_Cost_INR', 'min'),
        Max_Cost=('Estimated_Cost_INR', 'max'),
        Avg_Rating=('Rating', 'mean'),
        Avg_Stay=('Stay_Days', 'mean'),
        Records=('Visitor_ID', 'count')
    ).reset_index()

    matched = dest_summary[dest_summary['Avg_Cost'] <= float(max_budget)].copy()
    matched = matched.sort_values(by='Avg_Cost', ascending=True)

    if matched.empty:
        return {"count": 0, "cheapest": None, "results": []}

    matched['Avg_Cost'] = matched['Avg_Cost'].round().astype(int)
    matched['Min_Cost'] = matched['Min_Cost'].round().astype(int)
    matched['Max_Cost'] = matched['Max_Cost'].round().astype(int)
    matched['Avg_Rating'] = matched['Avg_Rating'].round(2)
    matched['Avg_Stay'] = matched['Avg_Stay'].round(1)

    results = matched.to_dict(orient='records')
    cheapest = results[0]

    return {
        "count": len(results),
        "cheapest_place": cheapest['Place'],
        "cheapest_cost": cheapest['Avg_Cost'],
        "results": results
    }


def estimate_custom_trip_cost(df, destination, num_travelers=2, trip_days=3, comfort_tier="Standard (1.0x)"):
    """
    Interactive Custom Trip Cost Estimator.
    Empirical baseline multiplied by days, travelers, and comfort tier multiplier.
    """
    multiplier_map = {
        "Budget (0.7x)": 0.7,
        "Standard (1.0x)": 1.0,
        "Premium / Luxury (1.8x)": 1.8
    }
    multiplier = multiplier_map.get(comfort_tier, 1.0)
    for k, v in multiplier_map.items():
        if k in comfort_tier:
            multiplier = v
            break

    dest_data = df[df['Place'] == destination]
    if dest_data.empty:
        base_cost = float(df['Estimated_Cost_INR'].mean())
        base_stay = float(df['Stay_Days'].mean())
        state = "India"
        category = "General"
    else:
        base_cost = float(dest_data['Estimated_Cost_INR'].mean())
        base_stay = float(dest_data['Stay_Days'].mean())
        state = str(dest_data['State'].iloc[0])
        category = str(dest_data['Category'].iloc[0])

    daily_rate = (base_cost / base_stay) if base_stay > 0 else 600.0
    estimated_person = int(round(daily_rate * trip_days * multiplier))
    total_projected = int(round(estimated_person * num_travelers))
    daily_person = int(round(estimated_person / trip_days)) if trip_days > 0 else estimated_person

    return {
        "destination": destination,
        "state": state,
        "category": category,
        "num_travelers": int(num_travelers),
        "trip_days": int(trip_days),
        "comfort_tier": comfort_tier,
        "multiplier": multiplier,
        "daily_rate_baseline": int(round(daily_rate)),
        "cost_per_person": estimated_person,
        "daily_per_person": daily_person,
        "total_projected": total_projected
    }

