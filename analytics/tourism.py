"""
Tourism Performance & Executive Overview Analytics
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
    """Serialize Plotly figure to a JSON-compatible Python dict."""
    return json.loads(fig.to_json())


# -------------------------------------------------------------
# EXECUTIVE OVERVIEW
# -------------------------------------------------------------
def get_executive_kpis(df):
    """High-level KPIs for executive cards."""
    if df.empty:
        return {
            "total_records": 0,
            "total_states": 0,
            "unique_destinations": 0,
            "avg_rating": 0.0,
            "avg_cost": 0,
            "avg_stay": 0.0,
            "recommendation_pct": 0.0
        }
    total_records = len(df)
    total_states = int(df['State'].nunique())
    unique_destinations = int(df['Place'].nunique())
    avg_rating = round(float(df['Rating'].mean()), 2)
    avg_cost = int(round(float(df['Estimated_Cost_INR'].mean())))
    avg_stay = round(float(df['Stay_Days'].mean()), 1)
    rec_count = int((df['Recommended'] == 'Yes').sum())
    recommendation_pct = round((rec_count / total_records) * 100, 1) if total_records > 0 else 0.0

    return {
        "total_records": total_records,
        "total_states": total_states,
        "unique_destinations": unique_destinations,
        "avg_rating": avg_rating,
        "avg_cost": avg_cost,
        "avg_stay": avg_stay,
        "recommendation_pct": recommendation_pct
    }


def get_executive_charts(df):
    """Generate all charts for Executive Overview."""
    if df.empty:
        return {}

    # 1. State volume (Top 10)
    state_counts = df['State'].value_counts().head(10).reset_index()
    state_counts.columns = ['State', 'Records']
    fig_state = px.bar(
        state_counts,
        x='Records',
        y='State',
        orientation='h',
        text='Records',
        color='Records',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 10 States by Tourism Records"
    )
    fig_state.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_state.update_traces(textposition='outside')
    apply_theme(fig_state)

    # 2. Top 10 destinations by popularity
    top_dest = df.groupby(['Place', 'State'])['Popularity_Score'].mean().reset_index()
    top_dest = top_dest.sort_values(by='Popularity_Score', ascending=False).head(10)
    fig_dest = px.bar(
        top_dest,
        x='Popularity_Score',
        y='Place',
        orientation='h',
        text=top_dest['Popularity_Score'].apply(lambda x: f"{x:.1f}"),
        color='Popularity_Score',
        color_continuous_scale=px.colors.sequential.Bluyl,
        title="Top 10 Destinations by Popularity Score"
    )
    fig_dest.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_dest.update_traces(textposition='outside')
    apply_theme(fig_dest)

    # 3. Category distribution (Donut)
    cat_counts = df['Category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Records']
    fig_cat = px.pie(
        cat_counts,
        names='Category',
        values='Records',
        hole=0.55,
        color_discrete_sequence=PBI_PALETTE,
        title="Tourism Category Distribution"
    )
    fig_cat.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    apply_theme(fig_cat)

    # 4. Monthly Trend
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    available_months = [m for m in month_order if m in df['Visit_Month'].unique()]
    month_data = df.groupby('Visit_Month', as_index=False).agg(
        Records=('Visitor_ID', 'count'),
        Avg_Rating=('Rating', 'mean')
    )
    month_data['Month_Order'] = month_data['Visit_Month'].map(lambda x: month_order.index(x) if x in month_order else 99)
    month_data = month_data.sort_values('Month_Order')

    fig_month = go.Figure()
    fig_month.add_trace(go.Bar(
        x=month_data['Visit_Month'],
        y=month_data['Records'],
        name='Visitor Records',
        marker_color='#0284c7'
    ))
    fig_month.add_trace(go.Scatter(
        x=month_data['Visit_Month'],
        y=month_data['Avg_Rating'],
        name='Average Rating (⭐)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#f59e0b', width=3),
        marker=dict(size=7)
    ))
    fig_month.update_layout(
        title="Monthly Influx Trend & Satisfaction Rating",
        yaxis=dict(title="Records", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Avg Rating (⭐)", overlaying='y', side='right', range=[3.0, 5.0], showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    apply_theme(fig_month)

    # 5. Seasonal Distribution
    season_order = ['Winter', 'Summer', 'Monsoon', 'Spring']
    season_data = df.groupby('Season', as_index=False).agg(
        Records=('Visitor_ID', 'count'),
        Avg_Cost=('Estimated_Cost_INR', 'mean')
    )
    season_data['Season_Order'] = season_data['Season'].map(lambda s: season_order.index(s) if s in season_order else 99)
    season_data = season_data.sort_values('Season_Order')
    fig_season = px.bar(
        season_data,
        x='Season',
        y='Records',
        text='Records',
        color='Season',
        color_discrete_sequence=['#0284c7', '#f97316', '#10b981', '#6366f1'],
        title="Seasonal Travel Distribution"
    )
    fig_season.update_traces(textposition='outside')
    fig_season.update_layout(showlegend=False)
    apply_theme(fig_season)

    # 6. Recommendation Pie
    rec_counts = df['Recommended'].value_counts().reset_index()
    rec_counts.columns = ['Status', 'Count']
    fig_rec = px.pie(
        rec_counts,
        names='Status',
        values='Count',
        hole=0.6,
        color='Status',
        color_discrete_map={'Yes': '#10b981', 'No': '#ef4444'},
        title="Traveler Recommendation Rate"
    )
    fig_rec.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    apply_theme(fig_rec)

    # 7. Interactive Segment Metric Explorer
    # Default segment: Category, Measure: Visitor records
    return {
        "state_volume": fig_to_dict(fig_state),
        "top_destinations": fig_to_dict(fig_dest),
        "category_donut": fig_to_dict(fig_cat),
        "monthly_trend": fig_to_dict(fig_month),
        "seasonal_distribution": fig_to_dict(fig_season),
        "recommendation_pie": fig_to_dict(fig_rec)
    }


def get_segment_metric_chart(df, dimension="Category", metric="Visitor records"):
    """Compute flexible dynamic slice comparison."""
    dim_map = {
        "Destination": "Place",
        "State": "State",
        "Category": "Category",
        "Season": "Season",
        "Travel group": "Travel_Group",
        "Age group": "Age_Group"
    }
    col = dim_map.get(dimension, "Category")

    metric_map = {
        "Visitor records": ("Visitor_ID", "count", "Records Count"),
        "Estimated footfall": ("Visitors_Count", "sum", "Total Footfall"),
        "Average rating": ("Rating", "mean", "Average Rating (⭐)"),
        "Average estimated cost (INR)": ("Estimated_Cost_INR", "mean", "Average Cost (₹)"),
        "Average stay (days)": ("Stay_Days", "mean", "Average Stay (Days)"),
        "Average popularity score": ("Popularity_Score", "mean", "Average Popularity (0-100)")
    }
    target_col, agg_fn, title_metric = metric_map.get(metric, ("Visitor_ID", "count", "Records Count"))

    agg_df = df.groupby(col, as_index=False).agg(Value=(target_col, agg_fn))
    agg_df = agg_df.sort_values(by='Value', ascending=False)
    if len(agg_df) > 12:
        agg_df = agg_df.head(12)

    is_int = agg_fn in ['count', 'sum']
    agg_df['Formatted_Val'] = agg_df['Value'].apply(lambda x: f"{int(round(x)):,}" if is_int else f"{x:.2f}")

    fig = px.bar(
        agg_df,
        x=col,
        y='Value',
        text='Formatted_Val',
        color='Value',
        color_continuous_scale=px.colors.sequential.Teal,
        title=f"{title_metric} broken down by {dimension}"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(coloraxis_showscale=False)
    apply_theme(fig)
    return fig_to_dict(fig)


# -------------------------------------------------------------
# TOURISM PERFORMANCE
# -------------------------------------------------------------
def get_performance_kpis(df):
    """KPIs for Tourism Performance dashboard."""
    if df.empty:
        return {}
    dest_grouped = df.groupby(['Place', 'State']).agg(
        Avg_Rating=('Rating', 'mean'),
        Popularity_Score=('Popularity_Score', 'mean')
    ).reset_index()

    top_rated_row = dest_grouped.sort_values(by='Avg_Rating', ascending=False).iloc[0]
    top_pop_row = dest_grouped.sort_values(by='Popularity_Score', ascending=False).iloc[0]

    avg_clean = round(float(df['Cleanliness_Rating'].mean()), 2)
    avg_safety = round(float(df['Safety_Rating'].mean()), 2)

    return {
        "top_rated_place": str(top_rated_row['Place']),
        "top_rated_state": str(top_rated_row['State']),
        "top_rated_val": round(float(top_rated_row['Avg_Rating']), 2),
        "most_popular_place": str(top_pop_row['Place']),
        "most_popular_state": str(top_pop_row['State']),
        "most_popular_val": round(float(top_pop_row['Popularity_Score']), 1),
        "avg_cleanliness": avg_clean,
        "avg_safety": avg_safety
    }


def get_performance_charts(df):
    """Generate charts for Tourism Performance page."""
    if df.empty:
        return {}

    # 1. Rating vs. Popularity Scatter
    dest_df = df.groupby(['Place', 'State', 'Category', 'Location_Type']).agg(
        Rating=('Rating', 'mean'),
        Popularity=('Popularity_Score', 'mean'),
        Visitors=('Visitors_Count', 'sum'),
        Cost=('Estimated_Cost_INR', 'mean')
    ).reset_index()

    fig_scatter = px.scatter(
        dest_df,
        x='Rating',
        y='Popularity',
        size='Visitors',
        color='Category',
        hover_name='Place',
        custom_data=['Place'],
        hover_data={'State': True, 'Cost': ':.0f', 'Rating': ':.2f', 'Popularity': ':.1f', 'Visitors': True},
        color_discrete_sequence=PBI_PALETTE,
        title="Satisfaction Rating vs. Popularity Score Matrix (Bubble Size = Visitors)"
    )
    apply_theme(fig_scatter)

    # 2. Quality Benchmark Radar
    categories = ['Satisfaction', 'Cleanliness', 'Safety', 'Accessibility']
    # Scale each between 0 and 5
    avg_sat = df['Rating'].mean()
    avg_cln = df['Cleanliness_Rating'].mean()
    avg_sft = df['Safety_Rating'].mean()
    avg_acc = df['Accessibility_Rating'].mean()

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[avg_sat, avg_cln, avg_sft, avg_acc, avg_sat],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(2, 132, 199, 0.25)',
        line=dict(color='#0284c7', width=2),
        name='National Average'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[2.5, 5.0], gridcolor="#e2e8f0"),
            angularaxis=dict(gridcolor="#e2e8f0")
        ),
        title="Multi-Dimensional Quality Index (0-5)",
        showlegend=False
    )
    apply_theme(fig_radar)

    # 3. Benchmark Rankings Table data
    benchmark_tbl = df.groupby(['Place', 'State', 'Category']).agg(
        Avg_Rating=('Rating', 'mean'),
        Popularity_Score=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Accessibility=('Accessibility_Rating', 'mean'),
        Advocacy=('Recommended', lambda x: (x == 'Yes').mean() * 100),
        Records=('Visitor_ID', 'count')
    ).reset_index()

    benchmark_tbl['Avg_Rating'] = benchmark_tbl['Avg_Rating'].round(2)
    benchmark_tbl['Popularity_Score'] = benchmark_tbl['Popularity_Score'].round(1)
    benchmark_tbl['Cleanliness'] = benchmark_tbl['Cleanliness'].round(2)
    benchmark_tbl['Safety'] = benchmark_tbl['Safety'].round(2)
    benchmark_tbl['Accessibility'] = benchmark_tbl['Accessibility'].round(2)
    benchmark_tbl['Advocacy'] = benchmark_tbl['Advocacy'].round(1)
    benchmark_records = benchmark_tbl.sort_values(by='Popularity_Score', ascending=False).to_dict(orient='records')

    return {
        "scatter_matrix": fig_to_dict(fig_scatter),
        "quality_radar": fig_to_dict(fig_radar),
        "benchmark_table": benchmark_records
    }

