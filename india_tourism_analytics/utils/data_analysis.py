"""
Data Analysis and Aggregation Utilities
Power BI-style Business Intelligence calculations for India Tourism Analytics
"""

import pandas as pd
import numpy as np


def compute_executive_kpis(df):
    """Compute high-level executive KPI indicators."""
    if df.empty:
        return {
            "total_records": 0,
            "total_states": 0,
            "unique_destinations": 0,
            "avg_rating": 0.0,
            "avg_cost": 0.0,
            "avg_stay": 0.0,
            "recommendation_pct": 0.0,
            "total_visitors": 0,
            "avg_popularity": 0.0,
            "avg_cleanliness": 0.0,
            "avg_safety": 0.0,
            "avg_accessibility": 0.0
        }

    total_records = len(df)
    total_states = df['State'].nunique()
    unique_destinations = df['Place'].nunique()
    avg_rating = df['Rating'].mean()
    avg_cost = df['Estimated_Cost_INR'].mean()
    avg_stay = df['Stay_Days'].mean()
    rec_count = (df['Recommended'] == 'Yes').sum()
    recommendation_pct = (rec_count / total_records) * 100 if total_records > 0 else 0
    total_visitors = df['Visitors_Count'].sum()
    avg_popularity = df['Popularity_Score'].mean()
    avg_cleanliness = df['Cleanliness_Rating'].mean()
    avg_safety = df['Safety_Rating'].mean()
    avg_accessibility = df['Accessibility_Rating'].mean()

    return {
        "total_records": int(total_records),
        "total_states": int(total_states),
        "unique_destinations": int(unique_destinations),
        "avg_rating": round(float(avg_rating), 2),
        "avg_cost": round(float(avg_cost), 2),
        "avg_stay": round(float(avg_stay), 1),
        "recommendation_pct": round(float(recommendation_pct), 1),
        "total_visitors": int(total_visitors),
        "avg_popularity": round(float(avg_popularity), 2),
        "avg_cleanliness": round(float(avg_cleanliness), 2),
        "avg_safety": round(float(avg_safety), 2),
        "avg_accessibility": round(float(avg_accessibility), 2)
    }


def get_state_summary(df):
    """Aggregate tourism metrics by State."""
    if df.empty:
        return pd.DataFrame()
    state_df = df.groupby('State').agg(
        Total_Records=('Visitor_ID', 'count'),
        Unique_Destinations=('Place', 'nunique'),
        Average_Rating=('Rating', 'mean'),
        Average_Cost_INR=('Estimated_Cost_INR', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Average_Popularity=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Accessibility=('Accessibility_Rating', 'mean')
    ).reset_index()
    return state_df.sort_values(by='Total_Records', ascending=False)


def get_destination_summary(df):
    """Aggregate tourism metrics by Destination (Place)."""
    if df.empty:
        return pd.DataFrame()
    dest_df = df.groupby(['Place', 'State', 'Category', 'Location_Type']).agg(
        Total_Records=('Visitor_ID', 'count'),
        Average_Rating=('Rating', 'mean'),
        Average_Cost_INR=('Estimated_Cost_INR', 'mean'),
        Average_Stay_Days=('Stay_Days', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Popularity_Score=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Accessibility=('Accessibility_Rating', 'mean'),
        Recommendation_Rate=('Recommended', lambda x: (x == 'Yes').mean() * 100)
    ).reset_index()
    return dest_df.sort_values(by='Popularity_Score', ascending=False)


def get_category_summary(df):
    """Aggregate tourism metrics by Category."""
    if df.empty:
        return pd.DataFrame()
    cat_df = df.groupby('Category').agg(
        Total_Records=('Visitor_ID', 'count'),
        Average_Rating=('Rating', 'mean'),
        Average_Cost_INR=('Estimated_Cost_INR', 'mean'),
        Average_Stay=('Stay_Days', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum'),
        Avg_Popularity=('Popularity_Score', 'mean')
    ).reset_index()
    return cat_df.sort_values(by='Total_Records', ascending=False)


def get_monthly_trends(df):
    """Aggregate records and costs across the 12 calendar months."""
    if df.empty:
        return pd.DataFrame()
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly = df.groupby('Visit_Month').agg(
        Total_Records=('Visitor_ID', 'count'),
        Average_Rating=('Rating', 'mean'),
        Average_Cost=('Estimated_Cost_INR', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum')
    ).reindex(month_order).dropna().reset_index()
    return monthly


def get_seasonal_summary(df):
    """Aggregate records by Season."""
    if df.empty:
        return pd.DataFrame()
    season_order = ["Winter", "Summer", "Monsoon", "Spring", "Autumn"]
    present_seasons = [s for s in season_order if s in df['Season'].values]
    seasonal = df.groupby('Season').agg(
        Total_Records=('Visitor_ID', 'count'),
        Average_Rating=('Rating', 'mean'),
        Average_Cost=('Estimated_Cost_INR', 'mean'),
        Total_Visitors=('Visitors_Count', 'sum')
    ).reindex(present_seasons).dropna().reset_index()
    return seasonal


def get_demographics_summary(df):
    """Extract demographic distributions."""
    if df.empty:
        return {}, {}, {}, pd.DataFrame()
    age_dist = df['Age_Group'].value_counts().reset_index()
    age_dist.columns = ['Age_Group', 'Count']

    gender_dist = df['Gender'].value_counts().reset_index()
    gender_dist.columns = ['Gender', 'Count']

    travel_dist = df['Travel_Group'].value_counts().reset_index()
    travel_dist.columns = ['Travel_Group', 'Count']

    # Cross-tabulation: Age Group vs Travel Group
    crosstab = pd.crosstab(df['Age_Group'], df['Travel_Group'])

    return age_dist, gender_dist, travel_dist, crosstab


def get_budget_destinations(df, max_budget):
    """Filter destinations within a user-specified budget."""
    if df.empty:
        return pd.DataFrame()
    filtered = df[df['Estimated_Cost_INR'] <= max_budget]
    if filtered.empty:
        return pd.DataFrame()
    dest_summary = filtered.groupby(['Place', 'State', 'Category']).agg(
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Min_Cost=('Estimated_Cost_INR', 'min'),
        Max_Cost=('Estimated_Cost_INR', 'max'),
        Avg_Rating=('Rating', 'mean'),
        Avg_Stay=('Stay_Days', 'mean'),
        Records=('Visitor_ID', 'count')
    ).reset_index().sort_values(by='Avg_Cost', ascending=True)
    return dest_summary


def compute_outliers_iqr(df, column):
    """Detect outliers for a given numerical column using the IQR method."""
    if column not in df.columns:
        return pd.DataFrame(), 0, 0, 0
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers, round(lower_bound, 2), round(upper_bound, 2), len(outliers)


def compute_smart_recommendations(df, preferred_category, travel_party, max_budget, preferred_season):
    """
    Multi-Criteria Decision Analysis (MCDA) Destination Recommender.
    Evaluates each destination across:
    1. Category alignment (30 pts)
    2. Budget viability & value (25 pts)
    3. Party demographic affinity (20 pts)
    4. Seasonal optimal match (15 pts)
    5. Quality assurance rating (10 pts)
    Returns sorted list with Match_Score (0-100%) and justifications.
    """
    if df.empty:
        return []

    dest_stats = df.groupby(['Place', 'State', 'Category', 'Location_Type', 'Best_Time_to_Visit']).agg(
        Avg_Rating=('Rating', 'mean'),
        Avg_Cost=('Estimated_Cost_INR', 'mean'),
        Avg_Stay=('Stay_Days', 'mean'),
        Popularity=('Popularity_Score', 'mean'),
        Cleanliness=('Cleanliness_Rating', 'mean'),
        Safety=('Safety_Rating', 'mean'),
        Accessibility=('Accessibility_Rating', 'mean'),
        Rec_Rate=('Recommended', lambda x: (x == 'Yes').mean() * 100),
        Total_Logs=('Visitor_ID', 'count')
    ).reset_index()

    recommendations = []

    for _, row in dest_stats.iterrows():
        score = 0.0
        reasons = []

        # 1. Category alignment (30 pts)
        if preferred_category == "Any Theme" or row['Category'] == preferred_category:
            score += 30.0
            reasons.append(f"Direct match for {row['Category']} tourism")
        else:
            score += 10.0

        # 2. Budget viability (25 pts)
        cost = row['Avg_Cost']
        if cost <= max_budget:
            score += 20.0
            savings = max_budget - cost
            if savings > 500:
                score += 5.0
                reasons.append(f"Highly affordable (₹{int(savings):,} within budget)")
            else:
                reasons.append("Within designated budget ceiling")
        else:
            pct_over = (cost - max_budget) / max_budget
            score += max(0.0, 15.0 - (pct_over * 20.0))

        # 3. Party demographic affinity (20 pts)
        party_subset = df[(df['Place'] == row['Place']) & (df['Travel_Group'] == travel_party)]
        if not party_subset.empty:
            party_pct = len(party_subset) / row['Total_Logs']
            party_pts = min(20.0, party_pct * 50.0 + 10.0)
            score += party_pts
            reasons.append(f"Popular choice among {travel_party} travelers")
        else:
            score += 10.0

        # 4. Season alignment (15 pts)
        if preferred_season in str(row['Best_Time_to_Visit']) or preferred_season == "All Seasons":
            score += 15.0
            reasons.append(f"Ideal climate during {preferred_season}")
        else:
            season_subset = df[(df['Place'] == row['Place']) & (df['Season'] == preferred_season)]
            if not season_subset.empty:
                score += 10.0
                reasons.append(f"Consistently visited during {preferred_season}")
            else:
                score += 5.0

        # 5. Quality assurance rating (10 pts)
        rating_pts = (row['Avg_Rating'] / 5.0) * 10.0
        score += rating_pts

        match_pct = min(99.0, max(50.0, score))

        recommendations.append({
            "Place": row['Place'],
            "State": row['State'],
            "Category": row['Category'],
            "Location_Type": row['Location_Type'],
            "Best_Time": row['Best_Time_to_Visit'],
            "Avg_Rating": round(row['Avg_Rating'], 2),
            "Avg_Cost": int(round(row['Avg_Cost'])),
            "Avg_Stay": round(row['Avg_Stay'], 1),
            "Popularity": round(row['Popularity'], 1),
            "Cleanliness": round(row['Cleanliness'], 2),
            "Safety": round(row['Safety'], 2),
            "Rec_Rate": round(row['Rec_Rate'], 1),
            "Match_Score": round(match_pct, 1),
            "Justifications": reasons[:3]
        })

    recommendations.sort(key=lambda x: x['Match_Score'], reverse=True)
    return recommendations


