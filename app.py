"""
India Tourism Analytics & Business Intelligence Dashboard
Python Flask Backend Server
Academic Project for Data Visualization with Python (DVP) Laboratory
"""

import os
import json
import re
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from analytics.data_cleaning import (
    get_cached_cleaned_data,
    apply_filters,
    DESTINATION_COORDINATES,
    DESTINATION_DISTRICT_MAP
)
from analytics.tourism import (
    get_executive_kpis,
    get_executive_charts,
    get_segment_metric_chart,
    get_performance_kpis,
    get_performance_charts
)
from analytics.geographical import (
    get_geographical_kpis,
    get_destination_markers,
    get_geographical_charts,
    load_geojson
)
from analytics.demographics import (
    get_demographics_kpis,
    get_demographics_charts
)
from analytics.financial import (
    get_financial_kpis,
    get_financial_charts,
    match_destinations_by_budget,
    estimate_custom_trip_cost
)
from analytics.reviews import (
    get_review_analytics,
    search_reviews
)
from analytics.recommender import (
    compute_smart_recommendations,
    compute_destination_battle,
    get_3d_opportunity_chart
)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)


def get_df_from_request():
    """Extract filters from request body and return filtered dataframe."""
    base_df = get_cached_cleaned_data()
    if request.is_json:
        data = request.get_json(silent=True) or {}
        filters = data.get("filters", data)
        return apply_filters(base_df, filters)
    return base_df


# -------------------------------------------------------------
# FRONTEND ENTRY POINT
# -------------------------------------------------------------
@app.route("/")
def index():
    """Serve the modern single-page dashboard application."""
    return render_template("index.html")


# -------------------------------------------------------------
# METADATA & FILTER OPTIONS API
# -------------------------------------------------------------
@app.route("/api/filters", methods=["GET"])
def api_filters():
    """Return available filter options dynamically computed from dataset."""
    df = get_cached_cleaned_data()
    states = sorted([str(s) for s in df['State'].dropna().unique().tolist() if s])
    categories = sorted([str(c) for c in df['Category'].dropna().unique().tolist() if c])
    seasons = sorted([str(s) for s in df['Season'].dropna().unique().tolist() if s])
    travel_groups = sorted([str(g) for g in df['Travel_Group'].dropna().unique().tolist() if g])
    destinations = sorted([str(p) for p in df['Place'].dropna().unique().tolist() if p])

    min_budget = int(df['Estimated_Cost_INR'].min())
    max_budget = int(df['Estimated_Cost_INR'].max())

    return jsonify({
        "states": states,
        "categories": categories,
        "seasons": seasons,
        "travel_groups": travel_groups,
        "destinations": destinations,
        "min_budget": min_budget,
        "max_budget": max_budget,
        "total_records": len(df)
    })


# -------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW API
# -------------------------------------------------------------
@app.route("/api/overview", methods=["POST"])
def api_overview():
    filtered_df = get_df_from_request()
    kpis = get_executive_kpis(filtered_df)
    charts = get_executive_charts(filtered_df)

    narrative = {}
    if not filtered_df.empty:
        state_counts = filtered_df['State'].value_counts()
        top_state = str(state_counts.index[0])
        top_state_count = int(state_counts.iloc[0])

        top_places = filtered_df.groupby('Place')['Popularity_Score'].mean().sort_values(ascending=False)
        top_place = str(top_places.index[0])
        top_place_score = float(top_places.iloc[0])

        cat_counts = filtered_df['Category'].value_counts()
        top_cat = str(cat_counts.index[0])
        top_cat_share = float(cat_counts.iloc[0] / len(filtered_df) * 100)

        narrative = {
            "top_state": top_state,
            "top_state_count": top_state_count,
            "top_state_pct": round(top_state_count / len(filtered_df) * 100, 1),
            "top_place": top_place,
            "top_place_score": round(top_place_score, 1),
            "top_category": top_cat,
            "top_category_share": round(top_cat_share, 1)
        }

    return jsonify({
        "kpis": kpis,
        "narrative": narrative,
        "charts": charts,
        "filtered_count": len(filtered_df)
    })


@app.route("/api/overview/segment-metric", methods=["POST"])
def api_segment_metric():
    filtered_df = get_df_from_request()
    data = request.get_json(silent=True) or {}
    dim = data.get("dimension", "Category")
    metric = data.get("metric", "Visitor records")
    chart_json = get_segment_metric_chart(filtered_df, dim, metric)
    return jsonify({"chart": chart_json})


# -------------------------------------------------------------
# 2. GEOGRAPHICAL ANALYSIS API
# -------------------------------------------------------------
@app.route("/api/geographical", methods=["POST"])
def api_geographical():
    filtered_df = get_df_from_request()
    kpis = get_geographical_kpis(filtered_df)
    markers = get_destination_markers(filtered_df)
    charts = get_geographical_charts(filtered_df)
    return jsonify({
        "kpis": kpis,
        "markers": markers,
        "charts": charts,
        "filtered_count": len(filtered_df)
    })


# -------------------------------------------------------------
# 3. TOURIST DEMOGRAPHICS API
# -------------------------------------------------------------
@app.route("/api/demographics", methods=["POST"])
def api_demographics():
    filtered_df = get_df_from_request()
    kpis = get_demographics_kpis(filtered_df)
    charts = get_demographics_charts(filtered_df)
    return jsonify({
        "kpis": kpis,
        "charts": charts,
        "filtered_count": len(filtered_df)
    })


# -------------------------------------------------------------
# 4. TOURISM PERFORMANCE API
# -------------------------------------------------------------
@app.route("/api/performance", methods=["POST"])
def api_performance():
    filtered_df = get_df_from_request()
    kpis = get_performance_kpis(filtered_df)
    charts = get_performance_charts(filtered_df)
    return jsonify({
        "kpis": kpis,
        "charts": charts,
        "filtered_count": len(filtered_df)
    })


# -------------------------------------------------------------
# 5. FINANCIAL ANALYSIS API
# -------------------------------------------------------------
@app.route("/api/financial", methods=["POST"])
def api_financial():
    filtered_df = get_df_from_request()
    kpis = get_financial_kpis(filtered_df)
    charts = get_financial_charts(filtered_df)
    return jsonify({
        "kpis": kpis,
        "charts": charts,
        "filtered_count": len(filtered_df)
    })


@app.route("/api/financial/budget-matcher", methods=["POST"])
def api_budget_matcher():
    filtered_df = get_df_from_request()
    data = request.get_json(silent=True) or {}
    max_budget = float(data.get("max_budget", 3000))
    result = match_destinations_by_budget(filtered_df, max_budget)
    return jsonify(result)


@app.route("/api/financial/cost-estimator", methods=["POST"])
def api_cost_estimator():
    # The destination is selected explicitly. Use its full sample history so an
    # unrelated active State/Category slicer cannot produce a misleading fallback.
    estimate_df = get_cached_cleaned_data()
    data = request.get_json(silent=True) or {}
    destination = data.get("destination", "Mysore Palace")
    num_travelers = int(data.get("num_travelers", 2))
    trip_days = int(data.get("trip_days", 3))
    comfort_tier = data.get("comfort_tier", "Standard (1.0x)")
    result = estimate_custom_trip_cost(estimate_df, destination, num_travelers, trip_days, comfort_tier)
    return jsonify(result)


# -------------------------------------------------------------
# 6. REVIEW ANALYTICS API
# -------------------------------------------------------------
@app.route("/api/reviews", methods=["POST"])
def api_reviews():
    filtered_df = get_df_from_request()
    result = get_review_analytics(filtered_df)
    result["filtered_count"] = len(filtered_df)
    return jsonify(result)


@app.route("/api/reviews/search", methods=["POST"])
def api_reviews_search():
    filtered_df = get_df_from_request()
    data = request.get_json(silent=True) or {}
    place = data.get("place", "All Destinations")
    keyword = data.get("keyword", "")
    reviews = search_reviews(filtered_df, place, keyword)
    return jsonify({
        "count": len(reviews),
        "reviews": reviews
    })


# -------------------------------------------------------------
# 7. AI RECOMMENDER & BATTLE API
# -------------------------------------------------------------
@app.route("/api/recommender", methods=["POST"])
def api_recommender():
    filtered_df = get_df_from_request()
    data = request.get_json(silent=True) or {}
    theme = data.get("theme", "Any Theme")
    party = data.get("party", "Couple")
    budget = float(data.get("budget", 3000))
    season = data.get("season", "All Seasons")
    recommendations = compute_smart_recommendations(filtered_df, theme, party, budget, season)
    return jsonify({
        "recommendations": recommendations,
        "count": len(recommendations)
    })


@app.route("/api/battle", methods=["POST"])
def api_battle():
    # The destinations are selected explicitly in the battle controls. Compare
    # their full visitor-sample records so a global State filter (e.g. Tamil Nadu)
    # does not silently remove the opponent (e.g. Coorg) and leave the panel blank.
    battle_df = get_cached_cleaned_data()
    data = request.get_json(silent=True) or {}
    dest_a = data.get("dest_a", "Mysore Palace")
    dest_b = data.get("dest_b", "Taj Mahal")
    battle_result = compute_destination_battle(battle_df, dest_a, dest_b)
    return jsonify(battle_result)


@app.route("/api/3d-space", methods=["POST"])
def api_3d_space():
    filtered_df = get_df_from_request()
    chart = get_3d_opportunity_chart(filtered_df)
    return jsonify({"chart": chart})


# -------------------------------------------------------------
# 8. MAP & GEOJSON API (PAN-INDIA 3-LEVEL GIS ENGINE)
# -------------------------------------------------------------
_MASTER_DESTINATIONS_CACHE = None
_INDIA_GEOJSON_CACHE = None


def get_master_destinations():
    """Load and cache the destination catalogue prototype."""
    global _MASTER_DESTINATIONS_CACHE
    if _MASTER_DESTINATIONS_CACHE is not None:
        return _MASTER_DESTINATIONS_CACHE

    master_path = os.path.join(BASE_DIR, "data", "tourist_destinations_master.csv")
    if not os.path.exists(master_path):
        master_path = os.path.join(BASE_DIR, "tourist_destinations_master.csv")

    if os.path.exists(master_path):
        try:
            df_master = pd.read_csv(master_path)
            category_colors = {
                "Historical": "#f97316",
                "Heritage": "#d97706",
                "Religious": "#8b5cf6",
                "Nature": "#10b981",
                "Adventure": "#ef4444",
                "Wildlife": "#059669",
                "Beach": "#06b6d4",
                "Cultural": "#ec4899",
                "Architecture": "#6366f1"
            }
            destinations = []
            for _, row in df_master.iterrows():
                cat = str(row.get("Category", "Heritage"))
                destinations.append({
                    "id": str(row.get("Destination_ID", "")),
                    "place": str(row.get("Place", "")),
                    "state": str(row.get("State", "")),
                    "district": str(row.get("District", "")),
                    "taluk": str(row.get("Taluk_Tehsil", "")),
                    "address": str(row.get("Address", "")),
                    "category": cat,
                    "location_type": str(row.get("Location_Type", "Attraction")),
                    "best_time": str(row.get("Best_Time_to_Visit", "All Year")),
                    "month": str(row.get("Visit_Month", "December")),
                    "season": str(row.get("Season", "Winter")),
                    "rating": float(row.get("Rating", 4.5)),
                    "cost": int(row.get("Estimated_Cost_INR", 250)),
                    "stay": int(row.get("Stay_Days", 1)),
                    "lat": float(row.get("Latitude", 0)),
                    "lon": float(row.get("Longitude", 0)),
                    "region": str(row.get("Region", "Central")),
                    "source_org": str(row.get("Source_Organisation", "Official Portal")),
                    "source_url": str(row.get("Source_URL", "")),
                    "verification_status": str(row.get("Verification_Status", "Portal reference only; not individually verified")),
                    "category_color": category_colors.get(cat, "#0284c7")
                })
            _MASTER_DESTINATIONS_CACHE = destinations
            print(f"Loaded {len(destinations)} master tourist destinations into GIS engine cache.")
            return destinations
        except Exception as e:
            print("Error loading tourist_destinations_master.csv:", e)

    # Fallback to df markers
    df = get_cached_cleaned_data()
    return get_destination_markers(df)


@app.route("/api/map/geojson/<region>", methods=["GET"])
def api_geojson(region):
    """Serve official GeoJSON data from local disk for India and all 36 States/UTs."""
    global _INDIA_GEOJSON_CACHE
    reg = region.lower().strip()
    if reg in ["india", "india_states"]:
        geo = load_geojson("india_states.geojson")
        if geo:
            return jsonify(geo)
    elif reg in ["karnataka", "karnataka_districts"]:
        geo = load_geojson("karnataka_districts.geojson")
        if geo:
            return jsonify(geo)
    else:
        # Check if local dedicated file exists matching region
        geo = load_geojson(f"{reg}.geojson")
        if geo:
            return jsonify(geo)

        # Dynamic extraction from all-India GeoJSON for all 36 States and Union Territories
        if _INDIA_GEOJSON_CACHE is None:
            _INDIA_GEOJSON_CACHE = load_geojson("india_states.geojson")

        if _INDIA_GEOJSON_CACHE and "features" in _INDIA_GEOJSON_CACHE:
            clean_target = re.sub(r'[^a-z0-9]+', '', reg)
            matched_features = []
            for feat in _INDIA_GEOJSON_CACHE.get("features", []):
                st = feat.get("properties", {}).get("st_nm", "")
                clean_st = re.sub(r'[^a-z0-9]+', '', st.lower())
                if clean_st == clean_target or clean_st in clean_target or clean_target in clean_st:
                    matched_features.append(feat)

            if matched_features:
                return jsonify({
                    "type": "FeatureCollection",
                    "features": matched_features
                })

    return jsonify({"error": f"GeoJSON for {region} not found on local disk"}), 404


@app.route("/api/map/destinations", methods=["GET"])
def api_map_destinations():
    """Return destination catalogue entries for the 3-level GIS prototype."""
    destinations = get_master_destinations()
    return jsonify({
        "destinations": destinations,
        "count": len(destinations),
        "district_map": DESTINATION_DISTRICT_MAP
    })


# -------------------------------------------------------------
# SERVER EXECUTION
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting India Tourism Analytics Flask Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
