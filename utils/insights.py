"""
Automated Tourism Insights Engine
Calculates business intelligence takeaways dynamically from actual dataset records.
"""

import pandas as pd


def generate_automated_insights(df):
    """
    Generate dynamic key insights from the dataset.
    Returns a list of structured insight dictionaries.
    """
    if df.empty:
        return []

    insights = []

    # 1. State with highest records
    state_counts = df['State'].value_counts()
    top_state = state_counts.index[0]
    top_state_count = int(state_counts.iloc[0])
    top_state_pct = round((top_state_count / len(df)) * 100, 1)
    insights.append({
        "title": "Top Tourism State",
        "value": f"{top_state} ({top_state_count} records)",
        "detail": f"{top_state} accounts for {top_state_pct}% of all recorded tourist visits.",
        "icon": "🏆",
        "badge": "State Leader",
        "color": "#0284c7"
    })

    # 2. Most Popular Destination
    dest_pop = df.groupby('Place')['Popularity_Score'].mean().sort_values(ascending=False)
    most_pop_place = dest_pop.index[0]
    most_pop_score = round(dest_pop.iloc[0], 2)
    place_state = df[df['Place'] == most_pop_place]['State'].iloc[0]
    insights.append({
        "title": "Most Popular Destination",
        "value": f"{most_pop_place}",
        "detail": f"Located in {place_state} with an industry-leading popularity score of {most_pop_score}/100.",
        "icon": "🌟",
        "badge": "High Demand",
        "color": "#f97316"
    })

    # 3. Highest-Rated Destination
    dest_rating = df.groupby('Place').agg(
        avg_rating=('Rating', 'mean'),
        count=('Visitor_ID', 'count')
    ).sort_values(by='avg_rating', ascending=False)
    top_rated_place = dest_rating.index[0]
    top_rating_val = round(dest_rating.iloc[0]['avg_rating'], 2)
    insights.append({
        "title": "Highest-Rated Destination",
        "value": f"{top_rated_place} (⭐ {top_rating_val}/5.0)",
        "detail": f"Maintains the highest tourist satisfaction score across {int(dest_rating.iloc[0]['count'])} visitor evaluations.",
        "icon": "⭐",
        "badge": "Top Rated",
        "color": "#10b981"
    })

    # 4. Most Common Tourism Category
    cat_counts = df['Category'].value_counts()
    top_cat = cat_counts.index[0]
    top_cat_count = int(cat_counts.iloc[0])
    top_cat_pct = round((top_cat_count / len(df)) * 100, 1)
    insights.append({
        "title": "Dominant Tourism Category",
        "value": f"{top_cat}",
        "detail": f"{top_cat} travel represents {top_cat_count} trips ({top_cat_pct}% of total tourism traffic).",
        "icon": "🧭",
        "badge": "Category Leader",
        "color": "#0d9488"
    })

    # 5. Most Common Travel Group
    group_counts = df['Travel_Group'].value_counts()
    top_group = group_counts.index[0]
    top_group_count = int(group_counts.iloc[0])
    top_group_pct = round((top_group_count / len(df)) * 100, 1)
    insights.append({
        "title": "Primary Travel Segment",
        "value": f"{top_group} Travelers",
        "detail": f"{top_group} travel represents {top_group_pct}% of all tourist bookings in this dataset.",
        "icon": "👥",
        "badge": "Demographic",
        "color": "#6366f1"
    })

    # 6. Most Common Age Group
    age_counts = df['Age_Group'].value_counts()
    top_age = age_counts.index[0]
    top_age_count = int(age_counts.iloc[0])
    top_age_pct = round((top_age_count / len(df)) * 100, 1)
    insights.append({
        "title": "Core Visitor Age Cohort",
        "value": f"Age {top_age}",
        "detail": f"Travelers aged {top_age} constitute the largest single demographic block ({top_age_pct}%).",
        "icon": "🎯",
        "badge": "Age Cohort",
        "color": "#8b5cf6"
    })

    # 7. Most Affordable Destination
    dest_cost = df.groupby('Place')['Estimated_Cost_INR'].mean().sort_values(ascending=True)
    cheapest_place = dest_cost.index[0]
    cheapest_val = int(round(dest_cost.iloc[0]))
    cheapest_state = df[df['Place'] == cheapest_place]['State'].iloc[0]
    insights.append({
        "title": "Most Affordable Destination",
        "value": f"{cheapest_place}",
        "detail": f"Average estimated expense of ₹{cheapest_val:,} per tourist in {cheapest_state}.",
        "icon": "💰",
        "badge": "Budget Friendly",
        "color": "#14b8a6"
    })

    # 8. Most Premium / Expensive Destination
    expensive_place = dest_cost.index[-1]
    expensive_val = int(round(dest_cost.iloc[-1]))
    expensive_state = df[df['Place'] == expensive_place]['State'].iloc[0]
    insights.append({
        "title": "Most Premium Destination",
        "value": f"{expensive_place}",
        "detail": f"Average estimated expense of ₹{expensive_val:,} per tourist in {expensive_state}.",
        "icon": "💎",
        "badge": "Luxury Travel",
        "color": "#ec4899"
    })

    # 9. Average Estimated Travel Expense
    avg_expense = int(round(df['Estimated_Cost_INR'].mean()))
    avg_stay = round(df['Stay_Days'].mean(), 1)
    daily_cost = int(round(avg_expense / avg_stay)) if avg_stay > 0 else avg_expense
    insights.append({
        "title": "Average Travel Expense",
        "value": f"₹{avg_expense:,}",
        "detail": f"Average stay is {avg_stay} days, translating to approximately ₹{daily_cost:,} per day.",
        "icon": "💳",
        "badge": "Financial Benchmark",
        "color": "#3b82f6"
    })

    # 10. Most Represented Season
    season_counts = df['Season'].value_counts()
    top_season = season_counts.index[0]
    top_season_count = int(season_counts.iloc[0])
    top_season_pct = round((top_season_count / len(df)) * 100, 1)
    insights.append({
        "title": "Peak Travel Season",
        "value": f"{top_season} Season",
        "detail": f"{top_season} registers {top_season_count} visits ({top_season_pct}% of total annual travel).",
        "icon": "☀️",
        "badge": "Seasonal Peak",
        "color": "#eab308"
    })

    return insights

