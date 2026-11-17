"""
Dashboard 2: Geographical Tourism Analysis
Spatial intelligence, high-contrast India GIS mapping, regional tourism density, and performance analytics.
Part of the India Tourism Analytics and Business Intelligence Dashboard.
"""

import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.visualizations import apply_pbi_theme

st.set_page_config(
    page_title="Geographical Tourism Analysis - India Tourism BI",
    page_icon="🗺️",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

# -------------------------------------------------------------
# PAGE HEADER BANNER
# -------------------------------------------------------------
render_page_header(
    title="Geographical Tourism Analysis",
    subtitle="Explore tourism destinations, state-wise distribution and geographical patterns across India.",
    badge="POWER BI DASHBOARD 2 • GEOGRAPHY"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# INTERACTIVE IN-PAGE COMPACT FILTERS
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-size: 13px; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px;">
            ⚡ Quick Geographical Slicers
        </span>
        <span style="font-size: 11.5px; color: #64748b;">Filter destinations dynamically across the map and insights</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize filter keys if not in session_state
if "geo_inpage_state" not in st.session_state:
    st.session_state["geo_inpage_state"] = "All States"
if "geo_inpage_cat" not in st.session_state:
    st.session_state["geo_inpage_cat"] = "All Categories"
if "geo_inpage_season" not in st.session_state:
    st.session_state["geo_inpage_season"] = "All Seasons"

col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 1.2, 0.7])

with col_f1:
    available_states = ["All States"] + sorted(filtered_df['State'].dropna().unique().tolist())
    curr_state = st.session_state["geo_inpage_state"]
    state_idx = available_states.index(curr_state) if curr_state in available_states else 0
    selected_state = st.selectbox("State Filter", available_states, index=state_idx, key="geo_inpage_state")

with col_f2:
    available_cats = ["All Categories"] + sorted(filtered_df['Category'].dropna().unique().tolist())
    curr_cat = st.session_state["geo_inpage_cat"]
    cat_idx = available_cats.index(curr_cat) if curr_cat in available_cats else 0
    selected_category = st.selectbox("Tourism Category", available_cats, index=cat_idx, key="geo_inpage_cat")

with col_f3:
    raw_seasons = [s for s in filtered_df['Season'].dropna().unique().tolist() if s]
    available_seasons = ["All Seasons"] + sorted(raw_seasons)
    curr_season = st.session_state["geo_inpage_season"]
    season_idx = available_seasons.index(curr_season) if curr_season in available_seasons else 0
    selected_season = st.selectbox("Travel Season", available_seasons, index=season_idx, key="geo_inpage_season")

with col_f4:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Reset", key="geo_reset_btn", use_container_width=True, help="Reset in-page filters"):
        st.session_state["geo_inpage_state"] = "All States"
        st.session_state["geo_inpage_cat"] = "All Categories"
        st.session_state["geo_inpage_season"] = "All Seasons"
        st.rerun()

# Apply in-page filters
df_geo = filtered_df.copy()
if selected_state != "All States":
    df_geo = df_geo[df_geo['State'] == selected_state]
if selected_category != "All Categories":
    df_geo = df_geo[df_geo['Category'] == selected_category]
if selected_season != "All Seasons":
    df_geo = df_geo[df_geo['Season'] == selected_season]

if df_geo.empty:
    st.warning("⚠️ No tourist destinations match the selected filter combination. Please broaden your slicers or click 'Reset'.")
    st.stop()

# -------------------------------------------------------------
# 4 COMPACT DYNAMIC KPI CARDS
# -------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

total_states = df_geo['State'].nunique()
total_destinations = df_geo['Place'].nunique()

top_state_series = df_geo['State'].value_counts()
top_state = top_state_series.index[0] if not top_state_series.empty else "N/A"
top_state_count = int(top_state_series.iloc[0]) if not top_state_series.empty else 0
top_state_share = (top_state_count / len(df_geo)) * 100 if len(df_geo) > 0 else 0

top_cat_series = df_geo['Category'].value_counts()
top_cat = top_cat_series.index[0] if not top_cat_series.empty else "N/A"
top_cat_count = int(top_cat_series.iloc[0]) if not top_cat_series.empty else 0
top_cat_share = (top_cat_count / len(df_geo)) * 100 if len(df_geo) > 0 else 0

with k1:
    render_kpi_card(
        "Total States Covered",
        f"{total_states}",
        "Geographical jurisdictions",
        "#0284c7",
        "🗺️"
    )
with k2:
    render_kpi_card(
        "Total Tourist Destinations",
        f"{total_destinations}",
        "Unique mapped landmarks",
        "#0d9488",
        "📍"
    )
with k3:
    render_kpi_card(
        "Most Represented State",
        f"{top_state}",
        f"{top_state_count} records ({top_state_share:.1f}%)",
        "#f59e0b",
        "🏆"
    )
with k4:
    render_kpi_card(
        "Most Popular Tourism Category",
        f"{top_cat}",
        f"{top_cat_share:.1f}% share ({top_cat_count} records)",
        "#6366f1",
        "🏷️"
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# INTERACTIVE INDIA MAP: DESTINATION DISTRIBUTION
# -------------------------------------------------------------
CATEGORY_METADATA = {
    'Nature': {'color': '#10b981', 'icon': '🌿'},
    'Cultural': {'color': '#f97316', 'icon': '🏛️'},
    'Historical': {'color': '#6366f1', 'icon': '🏰'},
    'Beach': {'color': '#06b6d4', 'icon': '🏖️'},
    'Adventure': {'color': '#e11d48', 'icon': '🧗'}
}

# Category Legend Banner directly above the map
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(15,23,42,0.03); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;">
    <div>
        <div style="font-size: 15px; font-weight: 700; color: #0f172a;">🗺️ India Tourism Destination Distribution Map</div>
        <div style="font-size: 11.5px; color: #64748b;">Interactive geospatial mapping of prominent tourist landmarks across India with category identification</div>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
        <span style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-right: 4px;">Legend:</span>
        <span style="background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">🌿 Nature</span>
        <span style="background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">🏛️ Cultural</span>
        <span style="background: #eef2ff; color: #3730a3; border: 1px solid #c7d2fe; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">🏰 Historical</span>
        <span style="background: #ecfeff; color: #155e75; border: 1px solid #a5f3fc; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">🏖️ Beach</span>
        <span style="background: #fff1f2; color: #9f1239; border: 1px solid #fecdd3; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">🧗 Adventure</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Aggregate destination-level attributes for the map
dest_summary = df_geo.groupby(['Place', 'State', 'Category'], dropna=True).agg(
    Latitude=('Latitude', 'first'),
    Longitude=('Longitude', 'first'),
    Location_Type=('Location_Type', 'first'),
    Best_Time=('Best_Time_to_Visit', 'first'),
    Avg_Rating=('Rating', 'mean'),
    Avg_Cost=('Estimated_Cost_INR', 'mean'),
    Avg_Stay=('Stay_Days', 'mean'),
    Total_Visitors=('Visitors_Count', 'sum'),
    Records=('Visitor_ID', 'count')
).reset_index()

# Dynamic map centering & bounds: properly fitting India inside container without cropping
valid_coords = dest_summary.dropna(subset=['Latitude', 'Longitude'])
if not valid_coords.empty and len(valid_coords) == 1:
    map_center = [valid_coords['Latitude'].iloc[0], valid_coords['Longitude'].iloc[0]]
    map_zoom = 8
    bounds = None
elif not valid_coords.empty and valid_coords['State'].nunique() == 1:
    map_center = [valid_coords['Latitude'].mean(), valid_coords['Longitude'].mean()]
    map_zoom = 7
    bounds = None
else:
    # Centered on central India with bounds covering the complete subcontinent
    map_center = [22.8, 79.5]
    map_zoom = 4
    bounds = [[7.5, 68.0], [36.5, 96.0]]

@st.cache_data
def get_india_states_geojson():
    possible_paths = [
        "data/geojson/india_states.geojson",
        os.path.join(os.path.dirname(__file__), "..", "data", "geojson", "india_states.geojson"),
        "india_tourism_analytics/data/geojson/india_states.geojson"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None

india_geojson = get_india_states_geojson()

# Initialize Folium Map with clean isolated canvas (only India displayed, surrounding countries removed)
india_map = folium.Map(
    location=map_center,
    zoom_start=map_zoom,
    tiles=None,
    control_scale=False,
    prefer_canvas=True
)

# Custom container styling for clean isolated India map matching reference design
custom_map_css = """
<style>
.leaflet-container {
    background: #edf2f7 !important;
    border-radius: 12px;
}
</style>
"""
india_map.get_root().html.add_child(folium.Element(custom_map_css))

# Render India GeoJSON polygons if available (pure India map without external countries)
if india_geojson:
    single_selected = selected_state if selected_state != "All States" else None

    def normalize_state(name):
        n = str(name).lower()
        if 'andaman' in n:
            return 'andaman'
        return ''.join(c for c in n if c.isalnum())

    def state_style(feature):
        st_name = feature['properties'].get('st_nm') or feature['properties'].get('name') or feature['properties'].get('state')
        if single_selected and normalize_state(st_name) == normalize_state(single_selected):
            # Highlight selected state in orange (like reference screenshot)
            return {
                'fillColor': '#f39c12',
                'color': '#ffffff',
                'weight': 2.5,
                'fillOpacity': 0.95
            }
        # Uniform solid full India map styling matching reference design
        return {
            'fillColor': '#3498db',
            'color': '#ffffff',
            'weight': 1.2,
            'fillOpacity': 0.8
        }

    def state_highlight(feature):
        return {
            'fillColor': '#f39c12',
            'color': '#ffffff',
            'weight': 2.5,
            'fillOpacity': 0.95
        }

    # Extract available tooltip fields
    first_props = india_geojson['features'][0].get('properties', {}) if india_geojson.get('features') else {}
    tooltip_fields = ['st_nm']
    tooltip_aliases = ['State:']
    if 'district' in first_props:
        tooltip_fields.append('district')
        tooltip_aliases.append('District:')

    india_geojson_layer = folium.GeoJson(
        india_geojson,
        name="India Full Map",
        style_function=state_style,
        highlight_function=state_highlight,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; padding: 4px 8px; border-radius: 6px;"
        )
    ).add_to(india_map)

    # Automatically fit the complete bounds of the full India map
    india_map.fit_bounds(india_geojson_layer.get_bounds())
else:
    # Graceful fallback to standard OSM if GeoJSON is missing
    folium.TileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ).add_to(india_map)
    if bounds:
        india_map.fit_bounds(bounds)

# Render Destination Markers with Category Colors and Rich Popups
for _, row in dest_summary.iterrows():
    lat = row['Latitude']
    lon = row['Longitude']
    if pd.isna(lat) or pd.isna(lon):
        continue

    cat = row['Category']
    meta = CATEGORY_METADATA.get(cat, {'color': '#0284c7', 'icon': '📍'})
    color = meta['color']
    icon_char = meta['icon']
    place = row['Place']
    state = row['State']
    avg_rating = row['Avg_Rating']
    avg_cost = row['Avg_Cost']
    avg_stay = row['Avg_Stay']
    loc_type = row.get('Location_Type', 'Landmark')
    best_time = row.get('Best_Time', 'October to March')
    if pd.isna(best_time) or not str(best_time).strip():
        best_time = "Year-round / Peak season"

    # Hover tooltip: clean and concise
    tooltip_html = f"📍 {place} ({state}) | {cat} | ⭐ {avg_rating:.2f} | ₹{int(avg_cost):,}"

    # Click popup: clear destination card
    popup_html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 245px; padding: 2px;">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid {color}; padding-bottom: 4px; margin-bottom: 6px;">
            <span style="font-size: 14px; font-weight: 700; color: #0f172a;">{place}</span>
            <span style="background-color: {color}; color: #ffffff; padding: 2px 7px; border-radius: 9999px; font-size: 10px; font-weight: 600;">{icon_char} {cat}</span>
        </div>
        <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">
            📍 <b>{state}</b> &bull; {loc_type}
        </div>
        <table style="width: 100%; font-size: 11.5px; border-collapse: collapse; line-height: 1.45;">
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="color: #64748b; padding: 3px 0;">Rating:</td>
                <td style="text-align: right; font-weight: 700; color: #0f172a; padding: 3px 0;">⭐ {avg_rating:.2f} / 5.0</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="color: #64748b; padding: 3px 0;">Estimated Cost:</td>
                <td style="text-align: right; font-weight: 700; color: #0f172a; padding: 3px 0;">₹{int(avg_cost):,}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="color: #64748b; padding: 3px 0;">Stay Duration:</td>
                <td style="text-align: right; font-weight: 600; color: #0f172a; padding: 3px 0;">{avg_stay:.1f} days</td>
            </tr>
            <tr>
                <td style="color: #64748b; padding: 3px 0;">Best Time to Visit:</td>
                <td style="text-align: right; font-weight: 600; color: #0284c7; padding: 3px 0;">{best_time}</td>
            </tr>
        </table>
    </div>
    """

    # High-visibility teardrop pin with white border and drop shadow
    pin_html = f"""
    <div style="
        background: {color};
        width: 26px;
        height: 26px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid #ffffff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    ">
        <span style="transform: rotate(45deg); font-size: 12px; display: block; line-height: 1;">{icon_char}</span>
    </div>
    """

    icon = folium.DivIcon(
        html=pin_html,
        icon_size=(26, 26),
        icon_anchor=(13, 26),
        popup_anchor=(0, -24)
    )

    folium.Marker(
        location=[lat, lon],
        icon=icon,
        tooltip=tooltip_html,
        popup=folium.Popup(popup_html, max_width=265)
    ).add_to(india_map)

# Render Full-Width Map: fits complete country of India comfortably on laptop screens without excessive scrolling
st_folium(india_map, use_container_width=True, height=580)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GEOGRAPHICAL INSIGHTS: EXACTLY THREE CLEAN VISUALIZATIONS
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
    <div style="font-size: 15px; font-weight: 700; color: #0f172a;">
        📊 Executive Geographical Insights & Regional Benchmarks
    </div>
    <div style="font-size: 12px; color: #64748b;">
        Focused analytical breakdown of destination counts, category allocation, and tourist satisfaction across Indian states.
    </div>
</div>
""", unsafe_allow_html=True)

# Row 1: Charts 1 & 2
col_chart1, col_chart2 = st.columns([1.1, 0.9])

# -------------------------------------------------------------
# CHART 1: Top 10 States by Number of Tourist Destinations
# -------------------------------------------------------------
with col_chart1:
    state_dest = (
        df_geo.groupby('State')['Place']
        .nunique()
        .reset_index(name='Destinations')
        .sort_values(by='Destinations', ascending=True)
        .tail(10)
    )

    fig1 = px.bar(
        state_dest,
        x='Destinations',
        y='State',
        orientation='h',
        text='Destinations',
        color='Destinations',
        color_continuous_scale=px.colors.sequential.Blues,
        title="Top 10 States by Number of Tourist Destinations",
        labels={'Destinations': 'Destination Count', 'State': 'State'}
    )
    fig1.update_traces(
        textposition='outside',
        cliponaxis=False,
        marker=dict(line=dict(color='#1e293b', width=0.5))
    )
    fig1.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(autorange=True),
        xaxis=dict(title="Unique Destinations Count")
    )
    st.plotly_chart(apply_pbi_theme(fig1), use_container_width=True)

# -------------------------------------------------------------
# CHART 2: Tourist Destinations by Tourism Category
# -------------------------------------------------------------
with col_chart2:
    cat_dest = (
        df_geo[['Place', 'Category']]
        .drop_duplicates()['Category']
        .value_counts()
        .reset_index()
    )
    cat_dest.columns = ['Category', 'Destinations']

    category_palette = {
        'Nature': '#10b981',
        'Cultural': '#f97316',
        'Historical': '#6366f1',
        'Beach': '#06b6d4',
        'Adventure': '#e11d48'
    }

    fig2 = px.pie(
        cat_dest,
        names='Category',
        values='Destinations',
        hole=0.55,
        color='Category',
        color_discrete_map=category_palette,
        title="Tourist Destinations by Tourism Category"
    )
    fig2.update_traces(
        textinfo='label+value+percent',
        textposition='outside',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    fig2.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(apply_pbi_theme(fig2), use_container_width=True)

# -------------------------------------------------------------
# CHART 3: State-wise Average Destination Rating
# -------------------------------------------------------------
state_rating = (
    df_geo.groupby('State')['Rating']
    .mean()
    .reset_index(name='Avg_Rating')
    .sort_values(by='Avg_Rating', ascending=True)
)
state_rating['Rating_Text'] = state_rating['Avg_Rating'].apply(lambda x: f"⭐ {x:.2f}")

fig3 = px.bar(
    state_rating,
    x='Avg_Rating',
    y='State',
    orientation='h',
    text='Rating_Text',
    color='Avg_Rating',
    color_continuous_scale=px.colors.sequential.Greens,
    title="State-wise Average Destination Rating",
    labels={'Avg_Rating': 'Average Rating (out of 5.0)', 'State': 'State'}
)
fig3.update_traces(
    textposition='outside',
    cliponaxis=False,
    marker=dict(line=dict(color='#065f46', width=0.5))
)
fig3.update_layout(
    coloraxis_showscale=False,
    yaxis=dict(autorange=True),
    xaxis=dict(range=[0, 5.5], title="Average Tourist Satisfaction Rating (1 to 5 Stars)")
)
st.plotly_chart(apply_pbi_theme(fig3), use_container_width=True)
