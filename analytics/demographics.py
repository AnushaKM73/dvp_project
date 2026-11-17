"""
Tourist Demographics & Persona Analytics
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


def get_demographics_kpis(df):
    """Compute demographic headline KPIs."""
    if df.empty:
        return {
            "dominant_age": "N/A",
            "dominant_age_count": 0,
            "dominant_age_pct": 0.0,
            "primary_group": "N/A",
            "primary_group_count": 0,
            "primary_group_pct": 0.0,
            "leading_gender": "N/A",
            "leading_gender_count": 0,
            "leading_gender_pct": 0.0,
            "solo_ratio": 0.0
        }

    age_cnt = df['Age_Group'].value_counts()
    dominant_age = str(age_cnt.index[0])
    dominant_age_count = int(age_cnt.iloc[0])
    dominant_age_pct = round(dominant_age_count / len(df) * 100, 1)

    group_cnt = df['Travel_Group'].value_counts()
    primary_group = str(group_cnt.index[0])
    primary_group_count = int(group_cnt.iloc[0])
    primary_group_pct = round(primary_group_count / len(df) * 100, 1)

    gender_cnt = df['Gender'].value_counts()
    leading_gender = str(gender_cnt.index[0])
    leading_gender_count = int(gender_cnt.iloc[0])
    leading_gender_pct = round(leading_gender_count / len(df) * 100, 1)

    solo_cnt = int((df['Travel_Group'] == 'Solo').sum())
    solo_ratio = round(solo_cnt / len(df) * 100, 1) if len(df) > 0 else 0.0

    return {
        "dominant_age": dominant_age,
        "dominant_age_count": dominant_age_count,
        "dominant_age_pct": dominant_age_pct,
        "primary_group": primary_group,
        "primary_group_count": primary_group_count,
        "primary_group_pct": primary_group_pct,
        "leading_gender": leading_gender,
        "leading_gender_count": leading_gender_count,
        "leading_gender_pct": leading_gender_pct,
        "solo_ratio": solo_ratio
    }


def get_demographics_charts(df):
    """Generate all charts for Tourist Demographics."""
    if df.empty:
        return {}

    # 1. Age distribution
    age_order = ['18-25', '26-35', '36-50', '50+', 'Senior', 'Under 18']
    age_counts = df['Age_Group'].value_counts().reset_index()
    age_counts.columns = ['Age_Group', 'Records']
    age_counts['Order'] = age_counts['Age_Group'].map(lambda x: age_order.index(x) if x in age_order else 99)
    age_counts = age_counts.sort_values('Order')
    fig_age = px.bar(
        age_counts,
        x='Age_Group',
        y='Records',
        text='Records',
        color='Age_Group',
        color_discrete_sequence=PBI_PALETTE,
        title="Visitor Age Group Distribution"
    )
    fig_age.update_traces(textposition='outside')
    fig_age.update_layout(showlegend=False)
    apply_theme(fig_age)

    # 2. Gender breakdown
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig_gender = px.pie(
        gender_counts,
        names='Gender',
        values='Count',
        hole=0.6,
        color='Gender',
        color_discrete_map={'Male': '#0284c7', 'Female': '#ec4899', 'Other': '#8b5cf6'},
        title="Gender Representation"
    )
    fig_gender.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    apply_theme(fig_gender)

    # 3. Travel group dynamics
    group_counts = df['Travel_Group'].value_counts().reset_index()
    group_counts.columns = ['Travel_Group', 'Count']
    fig_group = px.bar(
        group_counts,
        x='Travel_Group',
        y='Count',
        text='Count',
        color='Travel_Group',
        color_discrete_sequence=['#0d9488', '#f97316', '#6366f1', '#10b981', '#0284c7'],
        title="Travel Group Persona Breakdown"
    )
    fig_group.update_traces(textposition='outside')
    fig_group.update_layout(showlegend=False)
    apply_theme(fig_group)

    # 4. Cross-tabulation: Age vs. Travel Group Heatmap
    crosstab = pd.crosstab(df['Age_Group'], df['Travel_Group'])
    fig_heatmap = px.imshow(
        crosstab,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Cross-Tabulation: Age Cohort vs. Travel Group Matrix"
    )
    fig_heatmap.update_layout(coloraxis_showscale=False)
    apply_theme(fig_heatmap)

    return {
        "age_distribution": fig_to_dict(fig_age),
        "gender_breakdown": fig_to_dict(fig_gender),
        "travel_group_dynamics": fig_to_dict(fig_group),
        "age_vs_travel_heatmap": fig_to_dict(fig_heatmap)
    }

