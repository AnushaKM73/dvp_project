"""
Interactive Visualization Modules
Plotly, Matplotlib, Seaborn, and WordCloud functions styled like Power BI
"""

import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', tempfile.gettempdir())

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import io
import folium
from folium.plugins import HeatMap, MarkerCluster

# Power BI Color Palettes
PBI_PALETTE = ['#0284c7', '#0d9488', '#f97316', '#6366f1', '#10b981', '#ec4899', '#eab308', '#8b5cf6', '#14b8a6', '#f43f5e']
PBI_SEQUENTIAL = 'Tealgrn'

CHART_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#1e293b"),
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(248,250,252,0.6)",
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#ffffff", font_family="Inter"),
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0")
)


def apply_pbi_theme(fig):
    """Apply consistent Power BI styling to any Plotly figure."""
    fig.update_layout(**CHART_LAYOUT)
    return fig


# -------------------------------------------------------------
# EXECUTIVE OVERVIEW CHARTS
# -------------------------------------------------------------
def plot_state_distribution(df, top_n=10):
    """Bar chart: Top states by tourist records."""
    state_counts = df['State'].value_counts().head(top_n).reset_index()
    state_counts.columns = ['State', 'Tourist_Records']
    fig = px.bar(
        state_counts,
        x='Tourist_Records',
        y='State',
        orientation='h',
        text='Tourist_Records',
        color='Tourist_Records',
        color_continuous_scale=px.colors.sequential.Teal,
        title=f"Top {top_n} States by Tourism Records"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig.update_traces(textposition='outside')
    return apply_pbi_theme(fig)


def plot_top_destinations(df, top_n=10):
    """Bar chart: Top 10 popular destinations."""
    top_dest = df.groupby(['Place', 'State'])['Popularity_Score'].mean().reset_index()
    top_dest = top_dest.sort_values(by='Popularity_Score', ascending=False).head(top_n)
    fig = px.bar(
        top_dest,
        x='Popularity_Score',
        y='Place',
        orientation='h',
        text=top_dest['Popularity_Score'].apply(lambda x: f"{x:.1f}"),
        color='Popularity_Score',
        color_continuous_scale=px.colors.sequential.Bluyl,
        title=f"Top {top_n} Destinations by Popularity Score"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig.update_traces(textposition='outside')
    return apply_pbi_theme(fig)


def plot_category_distribution(df):
    """Donut chart: Tourism category distribution."""
    cat_counts = df['Category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Records']
    fig = px.pie(
        cat_counts,
        names='Category',
        values='Records',
        hole=0.55,
        color_discrete_sequence=PBI_PALETTE,
        title="Tourism Category Distribution"
    )
    fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    return apply_pbi_theme(fig)


def plot_monthly_trend(df):
    """Show the distribution of visitor records across calendar months."""
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly = df.groupby('Visit_Month')['Visitor_ID'].count().reindex(month_order).dropna().reset_index()
    monthly.columns = ['Month', 'Records']
    fig = px.bar(
        monthly,
        x='Month',
        y='Records',
        text='Records',
        color='Records',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Visitor Records by Month"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Visit month", yaxis_title="Visitor records")
    return apply_pbi_theme(fig)


def plot_segment_metric(df, dimension, metric):
    """Compare a selectable tourism measure across one visitor or destination segment."""
    dimensions = {
        "State": "State",
        "Destination": "Place",
        "Category": "Category",
        "Season": "Season",
        "Travel group": "Travel_Group",
        "Age group": "Age_Group",
    }
    measures = {
        "Visitor records": ("Visitor_ID", "count"),
        "Estimated footfall": ("Visitors_Count", "sum"),
        "Average rating": ("Rating", "mean"),
        "Average estimated cost (INR)": ("Estimated_Cost_INR", "mean"),
        "Average stay (days)": ("Stay_Days", "mean"),
        "Average popularity score": ("Popularity_Score", "mean"),
    }
    dimension_col = dimensions[dimension]
    measure_col, aggregation = measures[metric]
    summary = (
        df.groupby(dimension_col, dropna=True)
        .agg(Value=(measure_col, aggregation))
        .sort_values("Value", ascending=False)
        .head(12)
        .sort_values("Value", ascending=True)
        .reset_index()
    )

    if metric == "Average rating":
        labels = summary["Value"].map(lambda value: f"{value:.2f}")
    elif metric == "Average estimated cost (INR)":
        labels = summary["Value"].map(lambda value: f"₹{value:,.0f}")
    elif metric == "Average stay (days)":
        labels = summary["Value"].map(lambda value: f"{value:.1f}")
    elif metric == "Average popularity score":
        labels = summary["Value"].map(lambda value: f"{value:.1f}")
    else:
        labels = summary["Value"].map(lambda value: f"{value:,.0f}")

    fig = px.bar(
        summary,
        x="Value",
        y=dimension_col,
        orientation="h",
        text=labels,
        color="Value",
        color_continuous_scale=px.colors.sequential.Teal,
        title=f"{metric} by {dimension.lower()}",
        labels={"Value": metric, dimension_col: dimension},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return apply_pbi_theme(fig)


def plot_destination_sunburst(df):
    """Show state-to-category-to-destination hierarchy by estimated footfall."""
    hierarchy = (
        df.groupby(["State", "Category", "Place"], dropna=True)
        .agg(
            Estimated_Footfall=("Visitors_Count", "sum"),
            Average_Rating=("Rating", "mean"),
        )
        .reset_index()
    )
    fig = px.sunburst(
        hierarchy,
        path=["State", "Category", "Place"],
        values="Estimated_Footfall",
        color="Average_Rating",
        color_continuous_scale="RdYlGn",
        range_color=(1, 5),
        color_continuous_midpoint=3,
        hover_data={
            "Estimated_Footfall": ":,.0f",
            "Average_Rating": ":.2f",
        },
        title="Estimated Footfall: State → Category → Destination",
    )
    fig.update_layout(coloraxis_colorbar_title="Avg rating")
    return apply_pbi_theme(fig)


def plot_visitor_pattern_sankey(df):
    """Trace sample records across travel group, category, budget tier, and recommendation."""
    flow = df[["Travel_Group", "Category", "Estimated_Cost_INR", "Recommended"]].dropna().copy()
    if flow.empty:
        return go.Figure().update_layout(title="No records available for this visitor pattern")

    tier_names_by_count = {
        1: ["Only budget level"],
        2: ["Lower cost", "Higher cost"],
        3: ["Lower cost", "Mid-range cost", "Higher cost"],
        4: ["Lower cost", "Mid-low cost", "Mid-high cost", "Higher cost"],
    }
    tier_count = min(4, len(flow))
    tier_names = tier_names_by_count[tier_count]
    if tier_count == 1:
        flow["Budget tier"] = tier_names[0]
    else:
        cost_rank = flow["Estimated_Cost_INR"].rank(method="first")
        tier_codes = pd.qcut(cost_rank, q=tier_count, labels=False)
        flow["Budget tier"] = tier_codes.map(dict(enumerate(tier_names))).astype(str)

    stages = ["Travel_Group", "Category", "Budget tier", "Recommended"]
    stage_labels = []
    stage_lookup = []
    stage_colors = ["#0284c7", "#0d9488", "#f97316", "#6366f1"]

    for stage_index, column in enumerate(stages):
        values = flow[column].dropna().astype(str).unique().tolist()
        if column == "Budget tier":
            values = tier_names
        elif column == "Recommended":
            values = [value for value in ["Yes", "No"] if value in values]
        else:
            values = sorted(values, key=str.casefold)
        stage_lookup.append({value: len(stage_labels) + index for index, value in enumerate(values)})
        stage_labels.extend(values)

    sources, targets, values, link_colors = [], [], [], []
    for stage_index in range(len(stages) - 1):
        left, right = stages[stage_index], stages[stage_index + 1]
        links = (
            flow.groupby([left, right], observed=True)
            .size()
            .reset_index(name="Records")
        )
        for row in links.itertuples(index=False, name=None):
            source_label, target_label, record_count = str(row[0]), str(row[1]), int(row[2])
            sources.append(stage_lookup[stage_index][source_label])
            targets.append(stage_lookup[stage_index + 1][target_label])
            values.append(record_count)
            red, green, blue = tuple(
                int(stage_colors[stage_index].lstrip("#")[offset:offset + 2], 16)
                for offset in (0, 2, 4)
            )
            link_colors.append(f"rgba({red},{green},{blue},0.25)")

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=17,
            line=dict(color="white", width=1),
            label=stage_labels,
            color=[stage_colors[index] for index, column in enumerate(stages)
                   for _ in stage_lookup[index]],
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>%{value:,} records<extra></extra>",
        ),
    ))
    fig.update_layout(
        title="Visitor profile flow across the selected records",
        height=520,
        margin=dict(l=12, r=12, t=58, b=12),
    )
    return apply_pbi_theme(fig)


def plot_destination_cost_rating(df):
    """Compare destination-level estimated trip cost and satisfaction in one view."""
    summary = (
        df.groupby(["Place", "State", "Category"], dropna=True)
        .agg(
            Average_Cost=("Estimated_Cost_INR", "mean"),
            Average_Rating=("Rating", "mean"),
            Visitor_Records=("Visitor_ID", "count"),
            Average_Popularity=("Popularity_Score", "mean"),
        )
        .reset_index()
    )
    fig = px.scatter(
        summary,
        x="Average_Cost",
        y="Average_Rating",
        size="Visitor_Records",
        color="Category",
        hover_name="Place",
        hover_data={
            "State": True,
            "Average_Cost": ":,.0f",
            "Average_Rating": ":.2f",
            "Visitor_Records": ":,",
            "Average_Popularity": ":.1f",
        },
        size_max=28,
        color_discrete_sequence=PBI_PALETTE,
        title="Destination cost and visitor rating",
        labels={
            "Average_Cost": "Average estimated trip cost (INR)",
            "Average_Rating": "Average rating (out of 5)",
            "Visitor_Records": "Records in sample",
            "Category": "Tourism category",
        },
    )
    fig.add_vline(x=summary["Average_Cost"].median(), line_dash="dash", line_color="#64748b")
    fig.add_hline(y=summary["Average_Rating"].median(), line_dash="dash", line_color="#64748b")
    fig.update_yaxes(range=[1, 5], dtick=0.5)
    fig.update_layout(legend_title_text="Tourism category")
    return apply_pbi_theme(fig)


def plot_seasonal_distribution(df):
    """Bar chart: Seasonal tourism distribution."""
    season_order = ["Winter", "Summer", "Monsoon", "Spring", "Autumn"]
    present = [s for s in season_order if s in df['Season'].values]
    season_counts = df['Season'].value_counts().reindex(present).dropna().reset_index()
    season_counts.columns = ['Season', 'Records']
    fig = px.bar(
        season_counts,
        x='Season',
        y='Records',
        text='Records',
        color='Season',
        color_discrete_sequence=['#0284c7', '#f97316', '#0d9488', '#10b981', '#8b5cf6'],
        title="Seasonal Tourism Distribution"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    return apply_pbi_theme(fig)


def plot_rating_distribution(df):
    """Histogram: Tourist rating distribution."""
    fig = px.histogram(
        df,
        x='Rating',
        nbins=20,
        marginal='box',
        color_discrete_sequence=['#0d9488'],
        title="Tourist Rating Distribution (1.0 to 5.0)"
    )
    return apply_pbi_theme(fig)


def plot_recommendation_pie(df):
    """Donut chart: Recommended vs Not Recommended."""
    rec_counts = df['Recommended'].value_counts().reset_index()
    rec_counts.columns = ['Recommended', 'Count']
    fig = px.pie(
        rec_counts,
        names='Recommended',
        values='Count',
        hole=0.6,
        color='Recommended',
        color_discrete_map={'Yes': '#10b981', 'No': '#f43f5e'},
        title="Destination Recommendation Split"
    )
    fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    return apply_pbi_theme(fig)


# -------------------------------------------------------------
# GEOGRAPHICAL & FOLIUM MAP
# -------------------------------------------------------------
def create_india_folium_map(df):
    """
    Generate an interactive Folium map of India displaying prominent destinations
    with official full India GeoJSON boundaries (isolated, no surrounding countries),
    distinct category-colored markers, hover tooltips, and detailed Power BI popups.
    """
    import json
    geojson_data = None
    for p in [
        "data/geojson/india_states.geojson",
        os.path.join(os.path.dirname(__file__), "..", "data", "geojson", "india_states.geojson"),
        "india_tourism_analytics/data/geojson/india_states.geojson"
    ]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    geojson_data = json.load(f)
                    break
            except Exception:
                pass

    m = folium.Map(
        location=[22.8, 79.5],
        zoom_start=4,
        tiles=None if geojson_data else "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' if not geojson_data else None,
        control_scale=False,
        prefer_canvas=True
    )

    if geojson_data:
        custom_css = "<style>.leaflet-container { background: #edf2f7 !important; border-radius: 12px; }</style>"
        m.get_root().html.add_child(folium.Element(custom_css))

        def st_style(feat):
            return {'fillColor': '#3498db', 'color': '#ffffff', 'weight': 1.2, 'fillOpacity': 0.8}

        def st_highlight(feat):
            return {'fillColor': '#f39c12', 'color': '#ffffff', 'weight': 2.5, 'fillOpacity': 0.95}

        first_p = geojson_data['features'][0].get('properties', {}) if geojson_data.get('features') else {}
        t_fields = ['st_nm']
        t_aliases = ['State:']
        if 'district' in first_p:
            t_fields.append('district')
            t_aliases.append('District:')

        g_layer = folium.GeoJson(
            geojson_data,
            name="India Full Map",
            style_function=st_style,
            highlight_function=st_highlight,
            tooltip=folium.GeoJsonTooltip(fields=t_fields, aliases=t_aliases)
        ).add_to(m)
        m.fit_bounds(g_layer.get_bounds())

    category_meta = {
        'Nature': {'color': '#10b981', 'icon': '🌿'},
        'Cultural': {'color': '#f97316', 'icon': '🏛️'},
        'Historical': {'color': '#6366f1', 'icon': '🏰'},
        'Beach': {'color': '#06b6d4', 'icon': '🏖️'},
        'Adventure': {'color': '#e11d48', 'icon': '🧗'}
    }

    # Aggregate destination-level stats
    dest_stats = df.groupby(['Place', 'State', 'Category'], dropna=True).agg(
        Records=('Visitor_ID', 'count'),
        Avg_Rating=('Rating', 'mean'),
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Avg_Stay=('Stay_Days', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Popularity=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Rec_Rate=('Recommended', lambda x: (x == 'Yes').mean() * 100 if len(x) > 0 else 0),
        Latitude=('Latitude', 'first'),
        Longitude=('Longitude', 'first'),
        Location_Type=('Location_Type', 'first'),
        Best_Time=('Best_Time_to_Visit', 'first')
    ).reset_index()

    for _, row in dest_stats.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        if pd.isna(lat) or pd.isna(lon):
            continue

        cat = row['Category']
        meta = category_meta.get(cat, {'color': '#0284c7', 'icon': '📍'})
        color = meta['color']
        icon_char = meta['icon']
        place = row['Place']
        state = row['State']
        avg_rating = row['Avg_Rating']
        avg_cost = row['Avg_Cost']
        avg_stay = row['Avg_Stay']
        total_visitors = row['Total_Visitors']
        loc_type = row.get('Location_Type', 'Landmark')
        best_time = row.get('Best_Time', 'October to March')
        if pd.isna(best_time) or not str(best_time).strip():
            best_time = "Year-round / Peak season"

        tooltip_text = f"📍 {place} ({state}) | {cat} | ⭐ {avg_rating:.2f} | ₹{int(avg_cost):,}"

        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 265px; padding: 2px;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid {color}; padding-bottom: 5px; margin-bottom: 8px;">
                <span style="font-size: 14.5px; font-weight: 700; color: #0f172a;">{place}</span>
                <span style="background-color: {color}; color: #ffffff; padding: 2px 7px; border-radius: 9999px; font-size: 10.5px; font-weight: 600;">{icon_char} {cat}</span>
            </div>
            <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">
                📍 <b>{state}</b> &bull; {loc_type}
            </div>
            <table style="width: 100%; font-size: 11.5px; border-collapse: collapse; line-height: 1.45;">
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="color: #64748b; padding: 3px 0;">Average Rating</td>
                    <td style="text-align: right; font-weight: 700; color: #0f172a; padding: 3px 0;">⭐ {avg_rating:.2f} / 5.0</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="color: #64748b; padding: 3px 0;">Estimated Trip Cost</td>
                    <td style="text-align: right; font-weight: 700; color: #0f172a; padding: 3px 0;">₹{int(avg_cost):,}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="color: #64748b; padding: 3px 0;">Stay Duration</td>
                    <td style="text-align: right; font-weight: 600; color: #0f172a; padding: 3px 0;">{avg_stay:.1f} days</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="color: #64748b; padding: 3px 0;">Estimated Visitors</td>
                    <td style="text-align: right; font-weight: 600; color: #0f172a; padding: 3px 0;">{int(total_visitors):,}</td>
                </tr>
                <tr>
                    <td style="color: #64748b; padding: 3px 0;">Best Time to Visit</td>
                    <td style="text-align: right; font-weight: 600; color: #0284c7; padding: 3px 0;">{best_time}</td>
                </tr>
            </table>
        </div>
        """

        pin_html = f"""
        <div style="
            background: {color};
            width: 28px;
            height: 28px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            border: 2px solid #ffffff;
            box-shadow: 0 3px 6px rgba(0,0,0,0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        ">
            <span style="transform: rotate(45deg); font-size: 13px; display: block; line-height: 1;">{icon_char}</span>
        </div>
        """

        icon = folium.DivIcon(
            html=pin_html,
            icon_size=(28, 28),
            icon_anchor=(14, 28),
            popup_anchor=(0, -26)
        )

        folium.Marker(
            location=[lat, lon],
            icon=icon,
            tooltip=tooltip_text,
            popup=folium.Popup(popup_html, max_width=285)
        ).add_to(marker_cluster)

    return m


def create_india_footfall_heatmap(df):
    """Map estimated visitor counts as a smoothed heat layer and proportional bubbles at destination coordinates using OpenStreetMap tiles."""
    m = folium.Map(
        location=[22.0, 78.9],
        zoom_start=5,
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        control_scale=True,
        prefer_canvas=True
    )
    destination_volume = (
        df.groupby(["Place", "State", "Category"], dropna=True)
        .agg(
            Footfall=("Visitors_Count", "sum"),
            Avg_Rating=("Rating", "mean"),
            Avg_Cost=("Estimated_Cost_INR", "mean"),
            Latitude=("Latitude", "first"),
            Longitude=("Longitude", "first"),
        )
        .reset_index()
    )
    max_vis = destination_volume['Footfall'].max() if not destination_volume.empty else 1
    min_vis = destination_volume['Footfall'].min() if not destination_volume.empty else 0

    for _, row in destination_volume.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        if pd.isna(lat) or pd.isna(lon):
            continue
        vis = row['Footfall']
        norm = (vis - min_vis) / (max_vis - min_vis) if max_vis > min_vis else 0.5
        radius = 12 + norm * 20

        tooltip_b = f"👥 {row['Place']} ({row['State']}) • Estimated Footfall: {int(vis):,} visitors"
        popup_b = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 250px; padding: 4px;">
            <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 2px;">{row['Place']}</div>
            <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">📍 {row['State']} &bull; {row['Category']}</div>
            <div style="background: #eff6ff; border-left: 3px solid #0284c7; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px;">
                <div style="font-size: 10px; color: #64748b; text-transform: uppercase;">Estimated Visitor Footfall</div>
                <div style="font-size: 18px; font-weight: 800; color: #0284c7;">{int(vis):,}</div>
            </div>
            <div style="font-size: 11px; color: #475569;">
                Avg Rating: ⭐ <b>{row['Avg_Rating']:.2f}</b> | Avg Cost: <b>₹{int(row['Avg_Cost']):,}</b>
            </div>
        </div>
        """
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color="#e11d48",
            weight=2,
            fill=True,
            fill_color="#f43f5e",
            fill_opacity=0.65,
            tooltip=tooltip_b,
            popup=folium.Popup(popup_b, max_width=270)
        ).add_to(m)

    heat_points = [
        [row.Latitude, row.Longitude, max(float(row.Footfall), 0.0)]
        for row in destination_volume.itertuples(index=False)
        if pd.notna(row.Latitude) and pd.notna(row.Longitude)
    ]
    if heat_points:
        HeatMap(
            heat_points,
            name="Estimated visitor footfall",
            radius=28,
            blur=20,
            min_opacity=0.3,
            max_zoom=7,
        ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def plot_category_by_state(df):
    """Stacked bar chart: Tourism categories across states."""
    state_cat = df.groupby(['State', 'Category'])['Visitor_ID'].count().reset_index()
    state_cat.columns = ['State', 'Category', 'Count']
    top_states = df['State'].value_counts().head(10).index
    filtered = state_cat[state_cat['State'].isin(top_states)]
    fig = px.bar(
        filtered,
        x='State',
        y='Count',
        color='Category',
        color_discrete_sequence=PBI_PALETTE,
        title="Tourism Category Breakdown Across Top 10 States",
        barmode='stack'
    )
    return apply_pbi_theme(fig)


def plot_location_type_distribution(df):
    """Bar chart: Location types distribution."""
    loc_counts = df['Location_Type'].value_counts().reset_index()
    loc_counts.columns = ['Location_Type', 'Records']
    fig = px.bar(
        loc_counts,
        x='Records',
        y='Location_Type',
        orientation='h',
        text='Records',
        color='Records',
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Visitor Distribution by Location Type"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig.update_traces(textposition='outside')
    return apply_pbi_theme(fig)


# -------------------------------------------------------------
# DEMOGRAPHICS CHARTS
# -------------------------------------------------------------
def plot_age_distribution(df):
    """Bar chart: Age group distribution."""
    age_counts = df['Age_Group'].value_counts().reset_index()
    age_counts.columns = ['Age_Group', 'Visitors']
    fig = px.bar(
        age_counts,
        x='Age_Group',
        y='Visitors',
        text='Visitors',
        color='Age_Group',
        color_discrete_sequence=PBI_PALETTE,
        title="Visitor Age Group Distribution"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    return apply_pbi_theme(fig)


def plot_gender_distribution(df):
    """Donut chart: Gender distribution."""
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(
        gender_counts,
        names='Gender',
        values='Count',
        hole=0.55,
        color_discrete_sequence=['#0284c7', '#ec4899', '#f97316', '#64748b'],
        title="Visitor Gender Distribution"
    )
    fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    return apply_pbi_theme(fig)


def plot_travel_group_distribution(df):
    """Bar chart: Travel groups (Family vs Friends vs Solo vs Couple)."""
    group_counts = df['Travel_Group'].value_counts().reset_index()
    group_counts.columns = ['Travel_Group', 'Visitors']
    fig = px.bar(
        group_counts,
        x='Travel_Group',
        y='Visitors',
        text='Visitors',
        color='Travel_Group',
        color_discrete_sequence=PBI_PALETTE,
        title="Travel Group Preferences (Solo, Couple, Family, Friends)"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    return apply_pbi_theme(fig)


def plot_age_vs_travel_heatmap(df):
    """Heatmap: Age Group vs Travel Group cross-tabulation."""
    crosstab = pd.crosstab(df['Age_Group'], df['Travel_Group'])
    fig = px.imshow(
        crosstab,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Age Group vs Travel Group Matrix"
    )
    fig.update_layout(xaxis_title="Travel Group", yaxis_title="Age Cohort")
    return apply_pbi_theme(fig)


# -------------------------------------------------------------
# PERFORMANCE CHARTS
# -------------------------------------------------------------
def plot_rating_vs_popularity_scatter(df):
    """Scatter plot: Rating vs Popularity score with trendline."""
    dest_agg = df.groupby(['Place', 'Category', 'State']).agg(
        Avg_Rating=('Rating', 'mean'),
        Popularity=('Popularity_Score', 'mean'),
        Visitors=('Visitors_Count', 'sum'),
        Cost=('Estimated_Cost_INR', 'mean')
    ).reset_index()

    fig = px.scatter(
        dest_agg,
        x='Popularity',
        y='Avg_Rating',
        size='Visitors',
        color='Category',
        hover_name='Place',
        hover_data={'State': True, 'Cost': ':.0f', 'Avg_Rating': ':.2f', 'Popularity': ':.1f'},
        color_discrete_sequence=PBI_PALETTE,
        title="Destination Performance: Rating vs Popularity Score"
    )
    fig.add_hline(y=dest_agg['Avg_Rating'].mean(), line_dash="dash", line_color="#94a3b8", annotation_text="Avg Rating")
    fig.add_vline(x=dest_agg['Popularity'].mean(), line_dash="dash", line_color="#94a3b8", annotation_text="Avg Popularity")
    return apply_pbi_theme(fig)


def plot_quality_radar(df):
    """Comparative bar chart: Cleanliness, Safety, and Accessibility across Categories."""
    quality_df = df.groupby('Category').agg(
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Accessibility=('Accessibility_Rating', 'mean')
    ).reset_index()

    melted = quality_df.melt(id_vars=['Category'], var_name='Metric', value_name='Rating')
    fig = px.bar(
        melted,
        x='Category',
        y='Rating',
        color='Metric',
        barmode='group',
        color_discrete_sequence=['#0d9488', '#0284c7', '#f97316'],
        title="Comparative Quality Ratings: Cleanliness, Safety, Accessibility"
    )
    fig.update_layout(yaxis=dict(range=[0, 5]))
    return apply_pbi_theme(fig)


# -------------------------------------------------------------
# FINANCIAL CHARTS
# -------------------------------------------------------------
def plot_cost_by_category(df):
    """Box plot: Cost distribution by tourism category."""
    fig = px.box(
        df,
        x='Category',
        y='Estimated_Cost_INR',
        color='Category',
        color_discrete_sequence=PBI_PALETTE,
        points='all',
        custom_data=['Place', 'State', 'Category', 'Estimated_Cost_INR', 'Stay_Days'],
        title="Estimated Travel Cost Distribution Across Tourism Categories"
    )
    fig.update_traces(
        hovertemplate=(
            "<b>Destination:</b> %{customdata[0]}<br>"
            "<b>State:</b> %{customdata[1]}<br>"
            "<b>Category:</b> %{customdata[2]}<br>"
            "<b>Estimated Cost:</b> ₹%{customdata[3]:,}<br>"
            "<b>Stay Duration:</b> %{customdata[4]} days<extra></extra>"
        )
    )
    fig.update_layout(showlegend=False, yaxis_title="Cost in INR (₹)")
    return apply_pbi_theme(fig)


def plot_cost_by_state(df, top_n=10):
    """Bar chart: Average estimated cost per destination across top states."""
    state_cost = df.groupby('State').agg(
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Record_Count=('Estimated_Cost_INR', 'count'),
        Min_Cost=('Estimated_Cost_INR', 'min'),
        Max_Cost=('Estimated_Cost_INR', 'max')
    ).reset_index()
    state_cost = state_cost.sort_values(by='Avg_Cost', ascending=False).head(top_n)
    fig = px.bar(
        state_cost,
        x='Avg_Cost',
        y='State',
        orientation='h',
        custom_data=['State', 'Record_Count', 'Avg_Cost', 'Min_Cost', 'Max_Cost'],
        text=state_cost['Avg_Cost'].apply(lambda x: f"₹{int(round(x)):,}"),
        color='Avg_Cost',
        color_continuous_scale=px.colors.sequential.Sunset,
        title="Top 10 States by Average Estimated Cost per Destination"
    )
    hovertemplate = (
        "<b>State:</b> %{customdata[0]}<br>"
        "<b>Destination Records Included:</b> %{customdata[1]}<br>"
        "<b>Average Estimated Cost:</b> ₹%{customdata[2]:,.0f}<br>"
        "<b>Minimum Destination Cost:</b> ₹%{customdata[3]:,}<br>"
        "<b>Maximum Destination Cost:</b> ₹%{customdata[4]:,}<br>"
        "<i>Note: Average per destination record in state</i><extra></extra>"
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Average Estimated Cost (INR)",
        yaxis_title="State",
        coloraxis_showscale=False
    )
    fig.update_traces(
        textposition='outside',
        hovertemplate=hovertemplate
    )
    return apply_pbi_theme(fig)


def plot_cost_vs_stay(df):
    """Scatter plot: Estimated Cost vs Stay Duration with pure NumPy OLS trendline."""
    fig = px.scatter(
        df,
        x='Stay_Days',
        y='Estimated_Cost_INR',
        color='Category',
        color_discrete_sequence=PBI_PALETTE,
        custom_data=['Place', 'State', 'Category', 'Stay_Days', 'Estimated_Cost_INR'],
        title="Estimated Cost vs Stay Duration (with Linear Regression Trendline)"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Destination:</b> %{customdata[0]}<br>"
            "<b>State:</b> %{customdata[1]}<br>"
            "<b>Category:</b> %{customdata[2]}<br>"
            "<b>Stay Duration:</b> %{customdata[3]} days<br>"
            "<b>Estimated Cost:</b> ₹%{customdata[4]:,}<extra></extra>"
        ),
        selector=dict(type='scatter', mode='markers')
    )

    # Pure NumPy linear regression trendline (zero external statsmodels dependency)
    if len(df) > 1 and df['Stay_Days'].nunique() > 1:
        valid_data = df.dropna(subset=['Stay_Days', 'Estimated_Cost_INR'])
        if len(valid_data) > 1:
            x_vals = valid_data['Stay_Days'].values.astype(float)
            y_vals = valid_data['Estimated_Cost_INR'].values.astype(float)
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            x_line = np.array([x_vals.min(), x_vals.max()])
            y_line = slope * x_line + intercept
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=f'OLS Trend ({slope:+.1f} ₹/day)',
                line=dict(color='#0f172a', width=2.5, dash='dash'),
                hovertemplate=f"<b>OLS Regression Trendline</b><br>Slope: {slope:+.2f} ₹/day<extra></extra>"
            ))

    fig.update_layout(xaxis_title="Stay Duration (Days)", yaxis_title="Estimated Cost (INR)")
    return apply_pbi_theme(fig)


# -------------------------------------------------------------
# REVIEW TEXT ANALYTICS & SENTIMENT VISUALIZATIONS
# -------------------------------------------------------------
def plot_top_review_words(df, top_n=10):
    """Horizontal bar chart: Top N most frequently used words in tourist reviews with rich interactive details."""
    import re
    from collections import Counter

    if df.empty or 'Review' not in df.columns:
        fig = px.bar(title="Top 10 Most Frequently Used Words in Tourist Reviews")
        fig.update_layout(xaxis_title="Frequency Count", yaxis_title="Word")
        return apply_pbi_theme(fig)

    # Standard English stopwords
    stopwords = {
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
        'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but',
        'by', 'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few',
        'for', 'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself',
        'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'me', 'more',
        'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
        'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some',
        'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
        'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
        'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you',
        'your', 'yours', 'yourself', 'yourselves', 'also', 'still'
    }

    all_words = []
    for text in df['Review'].dropna():
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', str(text).lower())
        all_words.extend([w for w in tokens if w not in stopwords])

    if not all_words:
        fig = px.bar(title="Top 10 Most Frequently Used Words in Tourist Reviews")
        fig.update_layout(xaxis_title="Frequency Count", yaxis_title="Word")
        return apply_pbi_theme(fig)

    top_word_counts = Counter(all_words).most_common(top_n)

    has_place = 'Place' in df.columns
    rows = []
    for word, freq in top_word_counts:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        matching = df[df['Review'].astype(str).str.contains(pattern, na=False)]

        top_dest = "No specific destination association established"
        if has_place and not matching.empty:
            dest_counts = matching['Place'].dropna().value_counts()
            if not dest_counts.empty:
                top_dest = f"{dest_counts.index[0]} ({dest_counts.iloc[0]} reviews)"

        example_rev = "No example review available"
        if not matching.empty:
            example_rev = str(matching['Review'].dropna().iloc[0]).strip()

        rows.append({
            'Word': word.capitalize(),
            'Frequency': freq,
            'Top_Destination': top_dest,
            'Example_Review': example_rev
        })

    word_df = pd.DataFrame(rows).sort_values(by='Frequency', ascending=False)

    fig = px.bar(
        word_df,
        x='Frequency',
        y='Word',
        orientation='h',
        text='Frequency',
        custom_data=['Word', 'Frequency', 'Top_Destination', 'Example_Review'],
        color='Frequency',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 10 Most Frequently Used Words in Tourist Reviews"
    )

    hovertemplate = (
        "<b>Word:</b> %{customdata[0]}<br>"
        "<b>Frequency:</b> %{customdata[1]:,} occurrences<br>"
        "<b>Top Associated Destination:</b> %{customdata[2]}<br>"
        "<b>Example Review:</b> \"%{customdata[3]}\"<extra></extra>"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Frequency Count",
        yaxis_title="Word",
        coloraxis_showscale=False
    )
    fig.update_traces(
        textposition='outside',
        hovertemplate=hovertemplate
    )
    return apply_pbi_theme(fig)


def plot_sentiment_doughnut(analysis_df):
    """Doughnut chart: VADER sentiment distribution across Positive, Neutral, and Negative categories."""
    category_order = ['Positive', 'Neutral', 'Negative']
    counts_dict = analysis_df['Sentiment'].value_counts().to_dict() if (not analysis_df.empty and 'Sentiment' in analysis_df.columns) else {}

    senti_data = pd.DataFrame([
        {'Sentiment': cat, 'Count': counts_dict.get(cat, 0)}
        for cat in category_order
    ])

    fig = px.pie(
        senti_data,
        names='Sentiment',
        values='Count',
        hole=0.6,
        color='Sentiment',
        color_discrete_map={
            'Positive': '#10b981',
            'Neutral': '#64748b',
            'Negative': '#ef4444'
        },
        category_orders={'Sentiment': category_order},
        title="VADER Sentiment Distribution"
    )

    fig.update_traces(
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=2)),
        hovertemplate="<b>%{label} Sentiment</b><br>Review Count: %{value:,}<br>Percentage: %{percent}<extra></extra>"
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            title_text=""
        ),
        margin=dict(t=50, b=40, l=20, r=20)
    )
    return apply_pbi_theme(fig)


def plot_review_volume_by_destination(df, top_n=10):
    """Horizontal bar chart: Top N destinations by volume of reviews with rich hover details."""
    if df.empty or 'Place' not in df.columns:
        fig = px.bar(title="Top 10 Destinations by Volume of Reviews")
        fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Destination")
        return apply_pbi_theme(fig)

    dest_agg = df.groupby('Place').agg(
        Reviews_Count=('Place', 'count'),
        State=('State', lambda x: x.mode().iloc[0] if not x.empty else 'Unknown') if 'State' in df.columns else ('Place', lambda x: 'N/A'),
        Avg_Rating=('Rating', 'mean') if 'Rating' in df.columns else ('Place', lambda x: np.nan)
    ).reset_index()

    dest_agg = dest_agg.sort_values(by='Reviews_Count', ascending=False).head(top_n)

    dest_agg['Rating_Display'] = dest_agg['Avg_Rating'].apply(
        lambda r: f"⭐ {r:.2f} / 5.0" if pd.notna(r) else "Rating unavailable"
    )

    fig = px.bar(
        dest_agg,
        x='Reviews_Count',
        y='Place',
        orientation='h',
        text='Reviews_Count',
        custom_data=['Place', 'State', 'Reviews_Count', 'Rating_Display'],
        color='Reviews_Count',
        color_continuous_scale=px.colors.sequential.Blues,
        title="Top 10 Destinations by Volume of Reviews"
    )

    hovertemplate = (
        "<b>Destination:</b> %{customdata[0]}<br>"
        "<b>State:</b> %{customdata[1]}<br>"
        "<b>Number of Reviews:</b> %{customdata[2]:,} reviews<br>"
        "<b>Average Rating:</b> %{customdata[3]}<extra></extra>"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Number of Reviews",
        yaxis_title="Destination",
        coloraxis_showscale=False
    )
    fig.update_traces(
        textposition='outside',
        hovertemplate=hovertemplate
    )
    return apply_pbi_theme(fig)


def generate_review_wordcloud(df):
    """Generate WordCloud image from the Review column."""
    text = " ".join(df['Review'].dropna().astype(str).tolist())
    stopwords = set(STOPWORDS)
    stopwords.update(["place", "visit", "destination", "travel", "experience", "also"])

    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=stopwords,
        colormap='winter',
        max_words=80,
        random_state=42
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    return fig


def get_top_review_words(df, top_n=15):
    """Calculate most frequently occurring words in reviews."""
    from collections import Counter
    import re
    text = " ".join(df['Review'].dropna().astype(str).tolist()).lower()
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
    stopwords = set(STOPWORDS)
    stopwords.update(["place", "visit", "destination", "travel", "experience", "also", "with", "were", "this", "that", "from"])
    filtered_words = [w for w in words if w not in stopwords]
    counts = Counter(filtered_words).most_common(top_n)
    word_df = pd.DataFrame(counts, columns=['Word', 'Frequency'])
    return word_df


# -------------------------------------------------------------
# EDA SEABORN / MATPLOTLIB STATISTICAL CHARTS
# -------------------------------------------------------------
def plot_correlation_matrix(df):
    """Correlation Heatmap using Seaborn."""
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 6), facecolor='white')
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linewidths=0.5,
        ax=ax,
        cbar_kws={'label': 'Correlation Coefficient'}
    )
    ax.set_title("Correlation Matrix of Numerical Tourism Features", fontsize=13, fontweight='bold', pad=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    return fig


# -------------------------------------------------------------
# WOW FACTOR 3D & COMPARATIVE CHARTS
# -------------------------------------------------------------
def plot_3d_opportunity_matrix(df):
    """
    3D Interactive Tourism Opportunity Space (Plotly 3D Scatter).
    X-axis: Estimated Cost (INR)
    Y-axis: Tourist Rating (⭐)
    Z-axis: Popularity Score (0-100)
    Size: Total Visitors Count
    Color: Category
    """
    dest_agg = df.groupby(['Place', 'Category', 'State']).agg(
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Avg_Rating=('Rating', 'mean'),
        Avg_Pop=('Popularity_Score', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Avg_Stay=('Stay_Days', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean')
    ).reset_index()

    fig = px.scatter_3d(
        dest_agg,
        x='Avg_Cost',
        y='Avg_Rating',
        z='Avg_Pop',
        color='Category',
        size='Total_Visitors',
        hover_name='Place',
        hover_data={
            'State': True,
            'Avg_Cost': ':.0f',
            'Avg_Rating': ':.2f',
            'Avg_Pop': ':.1f',
            'Avg_Stay': ':.1f',
            'Total_Visitors': ':,',
            'Cleanliness': ':.2f',
            'Safety': ':.2f'
        },
        color_discrete_sequence=PBI_PALETTE,
        title="3D Interactive Tourism Opportunity Space (Rotate & Zoom in 3D)"
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Avg Cost (INR ₹)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            yaxis=dict(title='Rating (⭐ / 5.0)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            zaxis=dict(title='Popularity Score (/100)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0")
        ),
        font=dict(family="Inter, sans-serif", size=11, color="#1e293b"),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig


def plot_destination_battle_radar(name1, name2, stats1, stats2):
    """
    Polar / Radar comparative benchmark for two destinations across 6 normalized dimensions.
    """
    categories = [
        'Rating (⭐/5)',
        'Cleanliness (/5)',
        'Safety (/5)',
        'Accessibility (/5)',
        'Popularity (/20)',
        'Recommendation (/20%)'
    ]

    r1 = [
        stats1['Rating'],
        stats1['Cleanliness'],
        stats1['Safety'],
        stats1['Accessibility'],
        stats1['Popularity'] / 5.0,
        stats1['Recommendation'] / 5.0
    ]

    r2 = [
        stats2['Rating'],
        stats2['Cleanliness'],
        stats2['Safety'],
        stats2['Accessibility'],
        stats2['Popularity'] / 5.0,
        stats2['Recommendation'] / 5.0
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=r1 + [r1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=name1,
        line=dict(color='#0284c7', width=2.5),
        fillcolor='rgba(2, 132, 199, 0.25)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=r2 + [r2[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=name2,
        line=dict(color='#f97316', width=2.5),
        fillcolor='rgba(249, 115, 22, 0.25)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#e2e8f0")
        ),
        showlegend=True,
        title=f"Head-to-Head Radar Benchmark: {name1} vs {name2}",
        font=dict(family="Inter, sans-serif", size=12, color="#0f172a"),
        paper_bgcolor="#ffffff"
    )
    return fig

