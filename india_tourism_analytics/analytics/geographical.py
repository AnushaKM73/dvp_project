"""
Geographical Analysis & Spatial Intelligence Analytics
"""

import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from analytics.data_cleaning import DESTINATION_COORDINATES

PBI_PALETTE = ['#0284c7', '#0d9488', '#f97316', '#6366f1', '#10b981', '#ec4899', '#eab308', '#8b5cf6', '#14b8a6', '#f43f5e']

CATEGORY_COLORS = {
    'Nature': '#10b981',
    'Cultural': '#f97316',
    'Historical': '#6366f1',
    'Beach': '#06b6d4',
    'Adventure': '#e11d48',
    'Religious': '#8b5cf6',
    'Urban': '#64748b'
}

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


def get_geographical_kpis(df):
    """Calculate 4 core KPIs for Geographical Analysis."""
    if df.empty:
        return {
            "total_states": 0,
            "total_destinations": 0,
            "top_state": "N/A",
            "top_state_records": 0,
            "top_state_share": 0.0,
            "top_category": "N/A",
            "top_category_records": 0,
            "top_category_share": 0.0
        }
    total_states = int(df['State'].nunique())
    total_dest = int(df['Place'].nunique())

    state_counts = df['State'].value_counts()
    top_state = str(state_counts.index[0])
    top_state_rec = int(state_counts.iloc[0])
    top_state_pct = round(top_state_rec / len(df) * 100, 1)

    cat_counts = df['Category'].value_counts()
    top_cat = str(cat_counts.index[0])
    top_cat_rec = int(cat_counts.iloc[0])
    top_cat_pct = round(top_cat_rec / len(df) * 100, 1)

    return {
        "total_states": total_states,
        "total_destinations": total_dest,
        "top_state": top_state,
        "top_state_records": top_state_rec,
        "top_state_share": top_state_pct,
        "top_category": top_cat,
        "top_category_records": top_cat_rec,
        "top_category_share": top_cat_pct
    }


def get_destination_markers(df):
    """
    Extract aggregated destination pins with coordinates, category color,
    and verified popup metrics.
    """
    if df.empty:
        return []

    grouped = df.groupby(["Place", "State"]).agg(
        District=("District", "first"),
        Address=("Address", "first"),
        Category=("Category", "first"),
        Location_Type=("Location_Type", "first"),
        Best_Time=("Best_Time_to_Visit", "first"),
        Avg_Rating=("Rating", "mean"),
        Avg_Cost=("Estimated_Cost_INR", "mean"),
        Avg_Stay=("Stay_Days", "mean"),
        Total_Visitors=("Visitors_Count", "sum"),
        Popularity=("Popularity_Score", "mean"),
        Latitude=("Latitude", "first"),
        Longitude=("Longitude", "first"),
        Records=("Visitor_ID", "count")
    ).reset_index()

    markers = []
    for _, row in grouped.iterrows():
        place = str(row['Place'])
        lat = row['Latitude']
        lon = row['Longitude']
        if pd.isna(lat) or pd.isna(lon):
            coords = DESTINATION_COORDINATES.get(place, {})
            lat = coords.get('lat')
            lon = coords.get('lon')

        if pd.isna(lat) or pd.isna(lon) or lat is None or lon is None:
            continue

        cat = str(row['Category'])
        color = CATEGORY_COLORS.get(cat, '#0284c7')

        markers.append({
            "place": place,
            "state": str(row['State']),
            "district": str(row.get('District', '')) or DESTINATION_COORDINATES.get(place, {}).get('district', ''),
            "category": cat,
            "category_color": color,
            "location_type": str(row.get('Location_Type', '')),
            "best_time": str(row.get('Best_Time', '')),
            "rating": round(float(row['Avg_Rating']), 2),
            "cost": int(round(float(row['Avg_Cost']))),
            "stay": round(float(row['Avg_Stay']), 1),
            "visitors": int(row['Total_Visitors']),
            "popularity": round(float(row['Popularity']), 1),
            "records": int(row['Records']),
            "address": str(row.get('Address', '')),
            "lat": float(lat),
            "lon": float(lon)
        })

    return markers


def get_geographical_charts(df):
    """Generate charts below the map."""
    if df.empty:
        return {}

    # 1. Top 10 States by records
    state_cnt = df['State'].value_counts().head(10).reset_index()
    state_cnt.columns = ['State', 'Records']
    fig_states = px.bar(
        state_cnt,
        x='Records',
        y='State',
        orientation='h',
        text='Records',
        color='Records',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 10 States by Tourism Volume"
    )
    fig_states.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_states.update_traces(textposition='outside')
    apply_theme(fig_states)

    # 2. Tourism Category Mix by State (Top 8 states)
    top_8_states = df['State'].value_counts().head(8).index.tolist()
    state_cat_df = df[df['State'].isin(top_8_states)].groupby(['State', 'Category']).size().reset_index(name='Records')
    fig_cat_state = px.bar(
        state_cat_df,
        x='State',
        y='Records',
        color='Category',
        barmode='stack',
        color_discrete_map=CATEGORY_COLORS,
        title="Tourism Category Mix Across Top 8 States"
    )
    apply_theme(fig_cat_state)

    # 3. Location Type Distribution
    loc_cnt = df['Location_Type'].value_counts().reset_index()
    loc_cnt.columns = ['Location_Type', 'Records']
    fig_loc = px.bar(
        loc_cnt,
        x='Location_Type',
        y='Records',
        text='Records',
        color='Location_Type',
        color_discrete_sequence=PBI_PALETTE,
        title="Geographic Setting / Location Type Distribution"
    )
    fig_loc.update_traces(textposition='outside')
    fig_loc.update_layout(showlegend=False)
    apply_theme(fig_loc)

    return {
        "top_states": fig_to_dict(fig_states),
        "category_by_state": fig_to_dict(fig_cat_state),
        "location_types": fig_to_dict(fig_loc)
    }


def load_geojson(filename):
    """Load local GeoJSON file from data/geojson/."""
    candidates = [
        os.path.join("data", "geojson", filename),
        os.path.join("india_tourism_analytics", "data", "geojson", filename),
        filename
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None
