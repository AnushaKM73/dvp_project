"""
AI Recommender, Destination Battle & 3D Analytics (Academic WOW Factors)
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


def compute_smart_recommendations(df, theme="Any Theme", party="Couple", budget=3000, season="All Seasons"):
    """
    Multi-Criteria Decision Analysis (MCDA) Recommender Engine.
    Evaluates all unique destinations against user preferences.
    """
    if df.empty:
        return []

    dest_agg = df.groupby(['Place', 'State', 'Category', 'Location_Type']).agg(
        Avg_Rating=('Rating', 'mean'),
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Avg_Stay=('Stay_Days', 'mean'),
        Popularity=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Records=('Visitor_ID', 'count')
    ).reset_index()

    recommendations = []

    for _, row in dest_agg.iterrows():
        place = row['Place']
        cat = row['Category']
        cost = row['Avg_Cost']
        rating = row['Avg_Rating']

        # 1. Category / Theme affinity (weight: 30%)
        if theme == "Any Theme" or theme == "Any":
            theme_score = 100.0
        elif theme.lower() in cat.lower():
            theme_score = 100.0
        else:
            theme_score = 30.0

        # 2. Budget viability (weight: 25%)
        if cost <= budget:
            budget_score = 100.0
        elif cost <= budget * 1.25:
            budget_score = 75.0
        elif cost <= budget * 1.5:
            budget_score = 50.0
        else:
            budget_score = max(10.0, 100.0 - (cost - budget) / 50.0)

        # 3. Overall Rating & Quality (weight: 20%)
        quality_score = (rating / 5.0) * 100.0

        # 4. Cohort Affinity (weight: 15%)
        # Look at satisfaction of the specific travel group for this place
        cohort_records = df[(df['Place'] == place) & (df['Travel_Group'] == party)]
        if not cohort_records.empty:
            cohort_rating = cohort_records['Rating'].mean()
            cohort_score = (cohort_rating / 5.0) * 100.0
        else:
            cohort_score = quality_score * 0.9

        # 5. Seasonality alignment (weight: 10%)
        if season == "All Seasons" or season == "All":
            season_score = 100.0
        else:
            season_records = df[(df['Place'] == place) & (df['Season'] == season)]
            season_score = 100.0 if not season_records.empty else 40.0

        # Weighted composite MCDA formula
        total_score = (
            theme_score * 0.30 +
            budget_score * 0.25 +
            quality_score * 0.20 +
            cohort_score * 0.15 +
            season_score * 0.10
        )

        # Keep the score auditable: show the evidence and the number of
        # visitor records behind destination level and preference-specific stats.
        if theme in ("Any Theme", "Any"):
            theme_reason = "No theme preference selected"
        elif theme_score == 100.0:
            theme_reason = f"Matches your {theme.lower()} theme"
        else:
            theme_reason = f"Different theme from your {theme.lower()} preference"

        if cost <= budget:
            budget_reason = "Average cost is within your budget"
        else:
            budget_reason = f"Average cost is ₹{int(round(cost - budget)):,} above your budget"

        if not cohort_records.empty:
            cohort_reason = f"{party} visitor rating: {cohort_rating:.1f}/5 ({len(cohort_records)} records)"
        else:
            cohort_reason = f"No {party.lower()}-specific records; overall rating used as a fallback"

        if season in ("All Seasons", "All"):
            season_reason = "No season preference selected"
        elif not season_records.empty:
            season_reason = f"{len(season_records)} visitor records in {season}"
        else:
            season_reason = f"No {season} visits found in this dataset"

        reasons = [theme_reason, budget_reason, cohort_reason, season_reason]

        recommendations.append({
            "Place": place,
            "State": row['State'],
            "Category": cat,
            "Location_Type": row['Location_Type'],
            "Avg_Rating": round(float(rating), 2),
            "Avg_Cost": int(round(cost)),
            "Avg_Stay": round(float(row['Avg_Stay']), 1),
            "Popularity": round(float(row['Popularity']), 1),
            "Cleanliness": round(float(row['Cleanliness']), 2),
            "Safety": round(float(row['Safety']), 2),
            "Match_Score": int(round(total_score)),
            "Records": int(row['Records']),
            "Reasons": reasons,
            "Score_Breakdown": {
                "theme": round(float(theme_score), 1),
                "budget": round(float(budget_score), 1),
                "rating": round(float(quality_score), 1),
                "travel_group": round(float(cohort_score), 1),
                "season": round(float(season_score), 1)
            }
        })

    recommendations.sort(key=lambda x: x['Match_Score'], reverse=True)
    return recommendations


def compute_destination_battle(df, dest_a, dest_b):
    """
    Head-to-head comparison between two destinations with Radar chart and victory scorecard.
    """
    if df.empty:
        return {}

    def get_stats(place_name):
        sub = df[df['Place'] == place_name]
        if sub.empty:
            return None
        return {
            "Place": place_name,
            "State": str(sub['State'].iloc[0]),
            "Category": str(sub['Category'].iloc[0]),
            "Rating": round(float(sub['Rating'].mean()), 2),
            "Popularity": round(float(sub['Popularity_Score'].mean()), 1),
            "Cost": int(round(float(sub['Estimated_Cost_INR'].mean()))),
            "Stay": round(float(sub['Stay_Days'].mean()), 1),
            "Cleanliness": round(float(sub['Cleanliness_Rating'].mean()), 2),
            "Safety": round(float(sub['Safety_Rating'].mean()), 2),
            "Accessibility": round(float(sub['Accessibility_Rating'].mean()), 2),
            "Visitors": int(sub['Visitors_Count'].sum()),
            "Advocacy": round(float((sub['Recommended'] == 'Yes').mean() * 100), 1)
        }

    stats_a = get_stats(dest_a)
    stats_b = get_stats(dest_b)

    if not stats_a or not stats_b:
        return {}

    # Comparative Radar Chart
    categories = ['Satisfaction', 'Popularity (scaled)', 'Cleanliness', 'Safety', 'Accessibility', 'Affordability']
    
    # Scale popularity (0-100 -> 0-5) and affordability (lower cost -> higher score 0-5)
    r_a = [
        stats_a['Rating'],
        stats_a['Popularity'] / 20.0,
        stats_a['Cleanliness'],
        stats_a['Safety'],
        stats_a['Accessibility'],
        max(1.0, 5.0 - (stats_a['Cost'] / 1500.0))
    ]
    r_b = [
        stats_b['Rating'],
        stats_b['Popularity'] / 20.0,
        stats_b['Cleanliness'],
        stats_b['Safety'],
        stats_b['Accessibility'],
        max(1.0, 5.0 - (stats_b['Cost'] / 1500.0))
    ]

    fig_battle = go.Figure()
    fig_battle.add_trace(go.Scatterpolar(
        r=r_a + [r_a[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(2, 132, 199, 0.25)',
        line=dict(color='#0284c7', width=2.5),
        name=dest_a
    ))
    fig_battle.add_trace(go.Scatterpolar(
        r=r_b + [r_b[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(249, 115, 22, 0.25)',
        line=dict(color='#f97316', width=2.5),
        name=dest_b
    ))
    fig_battle.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[1.5, 5.2], gridcolor="#e2e8f0"),
            angularaxis=dict(gridcolor="#e2e8f0")
        ),
        title=f"Head-to-Head Benchmark: {dest_a} vs. {dest_b}",
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
    )
    apply_theme(fig_battle)

    # Determine attribute wins
    wins_a = 0
    wins_b = 0
    criteria = [
        ("Rating", stats_a['Rating'] > stats_b['Rating']),
        ("Popularity", stats_a['Popularity'] > stats_b['Popularity']),
        ("Budget Viability", stats_a['Cost'] < stats_b['Cost']),  # lower cost is better
        ("Cleanliness", stats_a['Cleanliness'] > stats_b['Cleanliness']),
        ("Safety", stats_a['Safety'] > stats_b['Safety']),
        ("Accessibility", stats_a['Accessibility'] > stats_b['Accessibility']),
        ("Advocacy Rate", stats_a['Advocacy'] > stats_b['Advocacy'])
    ]
    for _, a_won in criteria:
        if a_won:
            wins_a += 1
        else:
            wins_b += 1

    winner = dest_a if wins_a > wins_b else (dest_b if wins_b > wins_a else "Tie")

    return {
        "stats_a": stats_a,
        "stats_b": stats_b,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "winner": winner,
        "radar_chart": fig_to_dict(fig_battle)
    }


def get_3d_opportunity_chart(df):
    """3D Scatter Plot (Rating vs. Popularity vs. Cost)."""
    if df.empty:
        return {}

    dest_3d = df.groupby(['Place', 'State', 'Category']).agg(
        Rating=('Rating', 'mean'),
        Popularity=('Popularity_Score', 'mean'),
        Cost=('Estimated_Cost_INR', 'mean'),
        Visitors=('Visitors_Count', 'sum')
    ).reset_index()

    fig_3d = px.scatter_3d(
        dest_3d,
        x='Rating',
        y='Popularity',
        z='Cost',
        color='Category',
        size='Visitors',
        hover_name='Place',
        color_discrete_sequence=PBI_PALETTE,
        title="3D Tourism Opportunity Space (Satisfaction vs. Popularity vs. Budget)"
    )
    fig_3d.update_layout(
        scene=dict(
            xaxis_title="Avg Rating (⭐)",
            yaxis_title="Popularity Score",
            zaxis_title="Estimated Cost (₹ INR)"
        ),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig_to_dict(fig_3d)

