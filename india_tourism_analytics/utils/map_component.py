"""
India Tourism Explorer - Interactive Hierarchical Leaflet GIS Map
Provides seamless 3-level navigation:
India (States) ➔ State (Districts, e.g. Karnataka) ➔ District (Tourist Places View)
"""

import json
import os
import pandas as pd

# Canonical mapping for destination to district
DESTINATION_DISTRICT_MAP = {
    "Munnar": "Idukki",
    "Rann of Kutch": "Kutch",
    "Konark Sun Temple": "Puri",
    "Charminar": "Hyderabad",
    "Taj Mahal": "Agra",
    "Gangtok": "East Sikkim",
    "Gateway of India": "Mumbai City",
    "Mysore Palace": "Mysuru",
    "Radhanagar Beach": "South Andaman",
    "Jaisalmer Fort": "Jaisalmer",
    "Alleppey Backwaters": "Alappuzha",
    "Ooty": "Nilgiris",
    "Hampi": "Vijayanagara",
    "India Gate": "New Delhi",
    "Baga Beach": "North Goa",
    "Rishikesh": "Dehradun",
    "Manali": "Kullu",
    "Darjeeling": "Darjeeling",
    "Jaipur City Palace": "Jaipur",
    "Coorg": "Kodagu"
}

def load_geojson_file(filename):
    """Safely load local GeoJSON file from data/geojson/."""
    candidates = [
        os.path.join("data", "geojson", filename),
        os.path.join("india_tourism_analytics", "data", "geojson", filename),
        os.path.join(os.path.dirname(__file__), "..", "data", "geojson", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None

def extract_tourism_destinations(df):
    """Extract clean, unique tourist destination records from DataFrame."""
    dest_list = []
    grouped = df.groupby(["Place", "State"]).agg(
        District=("District", "first") if "District" in df.columns else ("Place", lambda p: DESTINATION_DISTRICT_MAP.get(p.iloc[0], "")),
        Address=("Address", "first"),
        Category=("Category", "first"),
        Location_Type=("Location_Type", "first"),
        Best_Time=("Best_Time_to_Visit", "first"),
        Avg_Rating=("Rating", "mean"),
        Avg_Cost=("Estimated_Cost_INR", "mean"),
        Total_Visitors=("Visitors_Count", "sum"),
        Avg_Popularity=("Popularity_Score", "mean"),
        Latitude=("Latitude", "first"),
        Longitude=("Longitude", "first"),
        Record_Count=("Visitor_ID", "count")
    ).reset_index()

    for _, row in grouped.iterrows():
        place = str(row["Place"])
        district = str(row.get("District", "")) if str(row.get("District", "")).strip() else DESTINATION_DISTRICT_MAP.get(place, "")
        dest_list.append({
            "Place": place,
            "State": str(row["State"]),
            "District": district,
            "Address": str(row["Address"]),
            "Category": str(row["Category"]),
            "Location_Type": str(row["Location_Type"]),
            "Best_Time": str(row["Best_Time"]),
            "Rating": round(float(row["Avg_Rating"]), 2),
            "Estimated_Cost": int(round(float(row["Avg_Cost"]))),
            "Visitors": int(row["Total_Visitors"]),
            "Popularity": round(float(row["Avg_Popularity"]), 1),
            "Latitude": float(row["Latitude"]) if pd.notna(row["Latitude"]) else None,
            "Longitude": float(row["Longitude"]) if pd.notna(row["Longitude"]) else None,
            "Records": int(row["Record_Count"])
        })
    return dest_list

def generate_hierarchical_map_html(df):
    """
    Generate fully self-contained HTML/CSS/JavaScript string
    matching the user's India Tourism Explorer implementation:
    - Large, properly fitted map with no excessive empty space.
    - Level 1: India State boundaries only.
    - Level 2: State District boundaries (e.g. Karnataka).
    - Level 3: District Tourist Places view with Summary Cards, Destination List, and Map.
    """
    destinations = extract_tourism_destinations(df)
    destinations_json = json.dumps(destinations)
    
    india_geojson = load_geojson_file("india_states.geojson") or {"type": "FeatureCollection", "features": []}
    karnataka_geojson = load_geojson_file("karnataka_districts.geojson") or {"type": "FeatureCollection", "features": []}
    
    india_geojson_str = json.dumps(india_geojson)
    karnataka_geojson_str = json.dumps(karnataka_geojson)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>India Interactive Tourism Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background: #f8fafc;
            color: #0f172a;
            padding: 12px;
        }}
        .explorer-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            width: 100%;
        }}
        /* Header & Navigation Bar */
        .explorer-header {{
            background: #0f172a;
            color: #ffffff;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            border-bottom: 2px solid #38bdf8;
        }}
        .header-title-box h1 {{
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .header-title-box p {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 2px;
        }}
        .breadcrumb-trail {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13.5px;
            font-weight: 600;
        }}
        .breadcrumb-step {{
            color: #94a3b8;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.2s;
        }}
        .breadcrumb-step:hover {{
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.15);
        }}
        .breadcrumb-step.active {{
            color: #ffffff;
            font-weight: 700;
            cursor: default;
        }}
        .breadcrumb-arrow {{
            color: #64748b;
            font-size: 11px;
        }}
        .header-btn-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .nav-button {{
            background: #1e293b;
            color: #ffffff;
            border: 1px solid #334155;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .nav-button:hover {{
            background: #2563eb;
            border-color: #3b82f6;
        }}
        .nav-button.primary {{
            background: #0284c7;
            border-color: #38bdf8;
        }}
        .nav-button.primary:hover {{
            background: #0369a1;
        }}

        /* Full Map Container (Level 1 & Level 2) */
        #map-container-main {{
            width: 100%;
            height: 640px;
            position: relative;
            background: #f1f5f9;
        }}
        #map {{
            width: 100%;
            height: 100%;
        }}

        /* Bottom Status Info Strip */
        .status-strip {{
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            padding: 8px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #475569;
        }}
        .status-badge {{
            font-weight: 700;
            color: #0284c7;
        }}

        /* LEVEL 3: DISTRICT TOURIST PLACES VIEW */
        #district-places-view {{
            display: none;
            flex-direction: column;
            padding: 16px;
            background: #ffffff;
            gap: 14px;
        }}
        .district-heading-box {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .district-heading-title {{
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .district-heading-subtitle {{
            font-size: 13px;
            color: #64748b;
        }}

        /* 3 Summary KPI Cards */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            border-top: 3px solid #0284c7;
        }}
        .kpi-card.green {{ border-top-color: #10b981; }}
        .kpi-card.amber {{ border-top-color: #f59e0b; }}
        .kpi-label {{
            font-size: 11.5px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .kpi-val {{
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 2px;
        }}

        /* Split Workspace in District View: Map + Cards List */
        .district-split {{
            display: flex;
            gap: 14px;
            height: 480px;
        }}
        .district-map-box {{
            flex: 1.2;
            height: 100%;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
            position: relative;
        }}
        #district-sub-map {{
            width: 100%;
            height: 100%;
        }}
        .district-cards-box {{
            flex: 0.9;
            height: 100%;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding-right: 4px;
        }}

        /* Tourist Place Item Card */
        .tourist-place-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px;
            border-left: 4px solid #0284c7;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            transition: all 0.2s;
            cursor: pointer;
        }}
        .tourist-place-card:hover {{
            border-color: #38bdf8;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
            transform: translateY(-1px);
        }}
        .place-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .p-name {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
        }}
        .category-tag {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            color: #ffffff;
            text-transform: uppercase;
        }}
        .cat-Nature {{ background: #10b981; }}
        .cat-Cultural {{ background: #f97316; }}
        .cat-Historical {{ background: #6366f1; }}
        .cat-Beach {{ background: #06b6d4; }}
        .cat-Adventure {{ background: #e11d48; }}

        .place-addr {{
            font-size: 12px;
            color: #64748b;
            margin-bottom: 8px;
        }}
        .place-stats-table {{
            width: 100%;
            font-size: 12px;
            color: #334155;
            border-collapse: collapse;
        }}
        .place-stats-table td {{
            padding: 3px 0;
        }}
        .place-stats-table td.label {{
            color: #64748b;
            width: 45%;
        }}
        .place-stats-table td.val {{
            font-weight: 600;
            text-align: right;
        }}

        /* Empty Result Alert Box (e.g. Mandya) */
        .empty-district-alert {{
            background: #fffbeb;
            border: 1px solid #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 16px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .empty-alert-title {{
            font-size: 14.5px;
            font-weight: 700;
            color: #92400e;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }}
        .empty-alert-message {{
            font-size: 13px;
            color: #b45309;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 12px;
        }}
        .empty-alert-note {{
            font-size: 11.5px;
            color: #78350f;
            line-height: 1.6;
            border-top: 1px dashed #fde68a;
            padding-top: 10px;
        }}
        .empty-alert-note ul {{
            margin: 6px 0 6px 20px;
        }}

        /* Tooltips & Popups */
        .leaflet-tooltip.custom-tip {{
            background: #0f172a;
            color: #ffffff;
            border: 1px solid #38bdf8;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            padding: 4px 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        .leaflet-popup-content-wrapper {{
            border-radius: 8px;
            font-family: inherit;
        }}
    </style>
</head>
<body>

<div class="explorer-card">
    <!-- Header with Dynamic Breadcrumb -->
    <div class="explorer-header">
        <div class="header-title-box">
            <h1 id="main-header-title">🗺️ India Tourism Explorer</h1>
            <p id="map-description">Click a state to explore its districts.</p>
        </div>

        <div class="breadcrumb-trail" id="breadcrumb-box">
            <span class="breadcrumb-step active" onclick="showIndia()">India</span>
        </div>

        <div class="header-btn-group">
            <button class="nav-button" id="btn-back-india" style="display:none;" onclick="showIndia()">
                ← Back to India
            </button>
            <button class="nav-button primary" id="btn-back-state" style="display:none;" onclick="showState(selectedState)">
                ← Back to State
            </button>
        </div>
    </div>

    <!-- MAIN MAP CONTAINER (Used for Level 1: India and Level 2: State Districts) -->
    <div id="map-container-main">
        <div id="map"></div>
    </div>

    <!-- LEVEL 3: DISTRICT TOURIST PLACES VIEW -->
    <div id="district-places-view">
        <div class="district-heading-box">
            <div>
                <div class="district-heading-title" id="district-view-title">Mandya, Karnataka</div>
                <div class="district-heading-subtitle">Verified tourist attractions and travel intelligence</div>
            </div>
            <div>
                <button class="nav-button primary" onclick="showState(selectedState)">
                    ← Back to Districts
                </button>
            </div>
        </div>

        <!-- Summary KPI Cards -->
        <div class="kpi-row">
            <div class="kpi-card">
                <span class="kpi-label">Tourist Places Found</span>
                <span class="kpi-val" id="kpi-places-count">0</span>
            </div>
            <div class="kpi-card green">
                <span class="kpi-label">Average Destination Rating</span>
                <span class="kpi-val" id="kpi-avg-rating">N/A</span>
            </div>
            <div class="kpi-card amber">
                <span class="kpi-label">Average Estimated Cost</span>
                <span class="kpi-val" id="kpi-avg-cost">N/A</span>
            </div>
        </div>

        <!-- Split Map + Destination List -->
        <div class="district-split">
            <div class="district-map-box">
                <div id="district-sub-map"></div>
            </div>
            <div class="district-cards-box" id="district-cards-list">
                <!-- Injected via JS -->
            </div>
        </div>
    </div>

    <!-- Bottom Status Strip -->
    <div class="status-strip">
        <div>
            Selected: <span class="status-badge" id="selected-name">India</span>
        </div>
        <div id="status-hint">
            Click any state polygon to zoom into district boundaries.
        </div>
    </div>
</div>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<script>
// ============================================
// EMBEDDED DATA & DATA SOURCES
// ============================================
const TOURISM_DATA = {destinations_json};
const BUILTIN_INDIA_GEOJSON = {india_geojson_str};
const BUILTIN_KARNATAKA_GEOJSON = {karnataka_geojson_str};

const INDIA_URL = "https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/india.geojson";

// Global Map References
let map = null;
let districtSubMap = null;
let currentLayer = null;
let districtMarkersLayer = null;
let currentLevel = "india"; // "india", "state", "district"
let selectedState = "";
let selectedDistrict = "";
let selectedDistrictFeature = null;
let requestId = 0;

// ============================================
// STYLES
// ============================================
function normalStyle() {{
    return {{
        fillColor: "#3498db",
        color: "#ffffff",
        weight: 1.5,
        fillOpacity: 0.75
    }};
}}

function hoverStyle(event) {{
    event.target.setStyle({{
        fillColor: "#f39c12",
        color: "#ffffff",
        weight: 3,
        fillOpacity: 0.95
    }});
    event.target.bringToFront();
}}

function resetStyle(event) {{
    if (currentLayer) {{
        currentLayer.resetStyle(event.target);
    }}
}}

// ============================================
// HELPERS
// ============================================
function getName(feature) {{
    const p = feature.properties || {{}};
    return (
        p.st_nm ||
        p.ST_NM ||
        p.STATE ||
        p.State_Name ||
        p.state ||
        p.name ||
        p.NAME_1 ||
        p.NAME ||
        "Unknown"
    );
}}

function getDistrictName(feature) {{
    const p = feature.properties || {{}};
    return (
        p.district ||
        p.DISTRICT ||
        p.DTNAME ||
        p.dtname ||
        p.Dist_Name ||
        p.name ||
        p.NAME_2 ||
        "Unknown District"
    );
}}

function normalizeName(name) {{
    return String(name || "").toLowerCase().replace(/[^a-z0-9]/g, "");
}}

function getStateFileName(name) {{
    const specialNames = {{
        "Andaman and Nicobar Islands": "andaman-and-nicobar-islands",
        "Andaman and Nicobar": "andaman-and-nicobar-islands",
        "Jammu and Kashmir": "jammu-and-kashmir",
        "Delhi": "nct-of-delhi",
        "NCT of Delhi": "nct-of-delhi",
        "Tamil Nadu": "tamil-nadu",
        "Uttar Pradesh": "uttar-pradesh",
        "Himachal Pradesh": "himachal-pradesh",
        "West Bengal": "west-bengal"
    }};

    return specialNames[name] ||
        name.toLowerCase()
            .replace(/&/g, "and")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
}}

function removeCurrentLayer() {{
    if (currentLayer && map) {{
        map.removeLayer(currentLayer);
        currentLayer = null;
    }}
}}

function updateBreadcrumbs() {{
    const box = document.getElementById("breadcrumb-box");
    if (currentLevel === "india") {{
        box.innerHTML = `<span class="breadcrumb-step active" onclick="showIndia()">India</span>`;
    }} else if (currentLevel === "state") {{
        box.innerHTML = `
            <span class="breadcrumb-step" onclick="showIndia()">India</span>
            <span class="breadcrumb-arrow">❯</span>
            <span class="breadcrumb-step active">${{selectedState}}</span>
        `;
    }} else if (currentLevel === "district") {{
        box.innerHTML = `
            <span class="breadcrumb-step" onclick="showIndia()">India</span>
            <span class="breadcrumb-arrow">❯</span>
            <span class="breadcrumb-step" onclick="showState(selectedState)">${{selectedState}}</span>
            <span class="breadcrumb-arrow">❯</span>
            <span class="breadcrumb-step active">${{selectedDistrict}}</span>
        `;
    }}
}}

// ============================================
// 1. INDIA MAP (LEVEL 1)
// ============================================
async function showIndia() {{
    const thisRequest = ++requestId;
    currentLevel = "india";
    selectedState = "";
    selectedDistrict = "";

    // Switch view containers
    document.getElementById("map-container-main").style.display = "block";
    document.getElementById("district-places-view").style.display = "none";

    document.getElementById("btn-back-india").style.display = "none";
    document.getElementById("btn-back-state").style.display = "none";
    document.getElementById("selected-name").textContent = "India";
    document.getElementById("map-description").textContent = "Click a state to explore its districts.";
    document.getElementById("status-hint").textContent = "Click any state polygon to zoom into district boundaries.";

    updateBreadcrumbs();
    removeCurrentLayer();

    // Ensure Leaflet map is created and properly sized
    if (!map) {{
        map = L.map("map", {{
            zoomControl: true,
            minZoom: 4,
            maxZoom: 14
        }});

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
    }}

    setTimeout(() => {{
        map.invalidateSize();
    }}, 100);

    let geoData = null;
    try {{
        const response = await fetch(INDIA_URL);
        if (response.ok) {{
            geoData = await response.json();
        }} else {{
            throw new Error("CDN response not ok");
        }}
    }} catch (e) {{
        console.warn("Using fallback India GeoJSON", e);
        geoData = BUILTIN_INDIA_GEOJSON;
    }}

    if (thisRequest !== requestId || !geoData) return;

    currentLayer = L.geoJSON(geoData, {{
        style: normalStyle,
        onEachFeature: function(feature, layer) {{
            const stateName = getName(feature);
            layer.bindTooltip(`<b>${{stateName}}</b>`, {{
                className: "custom-tip",
                sticky: true
            }});

            layer.on({{
                mouseover: hoverStyle,
                mouseout: resetStyle,
                click: function(event) {{
                    L.DomEvent.stopPropagation(event);
                    showState(stateName);
                }}
            }});
        }}
    }}).addTo(map);

    setTimeout(() => {{
        map.invalidateSize();
        try {{
            map.fitBounds(currentLayer.getBounds(), {{ padding: [15, 15] }});
        }} catch(e) {{
            map.setView([22.5, 79], 5);
        }}
    }}, 120);
}}

// ============================================
// 2. STATE MAP (LEVEL 2)
// ============================================
async function showState(stateName) {{
    const thisRequest = ++requestId;
    currentLevel = "state";
    selectedState = stateName;
    selectedDistrict = "";

    // Switch view containers
    document.getElementById("map-container-main").style.display = "block";
    document.getElementById("district-places-view").style.display = "none";

    document.getElementById("btn-back-india").style.display = "inline-flex";
    document.getElementById("btn-back-state").style.display = "none";
    document.getElementById("selected-name").textContent = `${{stateName}} (Districts)`;
    document.getElementById("map-description").textContent = "Hover over a district to see its name. Click a district to view tourist places.";
    document.getElementById("status-hint").textContent = "Click any district to filter tourist places from the dataset.";

    updateBreadcrumbs();
    removeCurrentLayer();

    setTimeout(() => {{
        map.invalidateSize();
    }}, 100);

    const fileName = getStateFileName(stateName);
    const districtURL = `https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/states/${{fileName}}.geojson`;

    let geoData = null;
    try {{
        const response = await fetch(districtURL);
        if (response.ok) {{
            geoData = await response.json();
        }} else {{
            throw new Error("State district GeoJSON fetch failed");
        }}
    }} catch(e) {{
        console.warn("Using fallback for state districts:", stateName, e);
        if (normalizeName(stateName) === "karnataka") {{
            geoData = BUILTIN_KARNATAKA_GEOJSON;
        }}
    }}

    if (thisRequest !== requestId) return;

    if (!geoData || !geoData.features || geoData.features.length === 0) {{
        alert("District boundaries are not available for " + stateName);
        showIndia();
        return;
    }}

    currentLayer = L.geoJSON(geoData, {{
        style: normalStyle,
        onEachFeature: function(feature, layer) {{
            const districtName = getDistrictName(feature);
            layer.bindTooltip(`<b>${{districtName}} District</b>`, {{
                className: "custom-tip",
                sticky: true
            }});

            layer.on({{
                mouseover: hoverStyle,
                mouseout: resetStyle,
                click: function(event) {{
                    L.DomEvent.stopPropagation(event);
                    showDistrictPlaces(stateName, districtName, feature);
                }}
            }});
        }}
    }}).addTo(map);

    setTimeout(() => {{
        map.invalidateSize();
        try {{
            map.fitBounds(currentLayer.getBounds(), {{ padding: [20, 20] }});
        }} catch(e) {{}}
    }}, 120);
}}

// ============================================
// 3. DISTRICT TOURIST PLACES VIEW (LEVEL 3)
// ============================================
function showDistrictPlaces(stateName, districtName, districtFeature) {{
    currentLevel = "district";
    selectedState = stateName;
    selectedDistrict = districtName;
    selectedDistrictFeature = districtFeature;

    // Switch view containers
    document.getElementById("map-container-main").style.display = "none";
    document.getElementById("district-places-view").style.display = "flex";

    document.getElementById("btn-back-india").style.display = "inline-flex";
    document.getElementById("btn-back-state").style.display = "inline-flex";
    document.getElementById("btn-back-state").textContent = `← Back to ${{stateName}}`;

    document.getElementById("selected-name").textContent = `${{districtName}}, ${{stateName}}`;
    document.getElementById("district-view-title").textContent = `${{districtName}}, ${{stateName}}`;
    document.getElementById("map-description").textContent = `Tourist places belonging strictly to ${{districtName}} District.`;
    document.getElementById("status-hint").textContent = `Showing tourist destination records filtered from dataset for ${{districtName}}.`;

    updateBreadcrumbs();

    // ---------------------------------------------------------
    // FILTER RECORDS STRICTLY BY STATE & DISTRICT
    // ---------------------------------------------------------
    const matchingPlaces = filterDestinations(stateName, districtName);

    // Update 3 KPI Summary Cards
    const count = matchingPlaces.length;
    document.getElementById("kpi-places-count").textContent = count;

    if (count > 0) {{
        const avgRating = (matchingPlaces.reduce((sum, p) => sum + (p.Rating || 0), 0) / count).toFixed(2);
        const avgCost = Math.round(matchingPlaces.reduce((sum, p) => sum + (p.Estimated_Cost || 0), 0) / count);
        document.getElementById("kpi-avg-rating").textContent = `⭐ ${{avgRating}} / 5.0`;
        document.getElementById("kpi-avg-cost").textContent = `₹${{avgCost.toLocaleString()}}`;
    }} else {{
        document.getElementById("kpi-avg-rating").textContent = "N/A";
        document.getElementById("kpi-avg-cost").textContent = "N/A";
    }}

    // Render Destination List or Empty Result
    const cardsContainer = document.getElementById("district-cards-list");
    if (count === 0) {{
        // REQUIRED EMPTY RESULT: Mandya, etc.
        cardsContainer.innerHTML = `
            <div class="empty-district-alert">
                <div class="empty-alert-title">⚠️ District Notice</div>
                <div class="empty-alert-message">
                    "No tourist places are currently available for this district in the dataset."
                </div>
                <div class="empty-alert-note">
                    <b>Verified Landmark Locations in ${{stateName}}:</b><br>
                    The dataset contains records for:
                    <ul>
                        <li><b>Mysuru:</b> Mysore Palace (Historical)</li>
                        <li><b>Kodagu:</b> Coorg (Nature)</li>
                        <li><b>Vijayanagara:</b> Hampi (Historical)</li>
                    </ul>
                    No tourist destination records exist for <b>${{districtName}}</b> in the dataset.
                </div>
                <div style="margin-top: 14px;">
                    <button class="nav-button primary" onclick="showState(selectedState)">
                        ← Return to ${{stateName}} District Map
                    </button>
                </div>
            </div>
        `;
    }} else {{
        let cardsHtml = "";
        matchingPlaces.forEach((p, idx) => {{
            cardsHtml += `
                <div class="tourist-place-card" onclick="focusDistrictMarker(${{p.Latitude}}, ${{p.Longitude}}, '${{p.Place}}')">
                    <div class="place-head">
                        <span class="p-name">${{p.Place}}</span>
                        <span class="category-tag cat-${{p.Category}}">${{p.Category}}</span>
                    </div>
                    <div class="place-addr">📍 ${{p.Address}}</div>
                    <table class="place-stats-table">
                        <tr><td class="label">Rating:</td><td class="val">⭐ ${{p.Rating}} / 5.0</td></tr>
                        <tr><td class="label">Estimated Cost:</td><td class="val">₹${{p.Estimated_Cost.toLocaleString()}}</td></tr>
                        <tr><td class="label">Best Time to Visit:</td><td class="val">${{p.Best_Time}}</td></tr>
                        <tr><td class="label">Location Type:</td><td class="val">${{p.Location_Type}}</td></tr>
                        <tr><td class="label">Visitors Count:</td><td class="val">${{p.Visitors.toLocaleString()}}</td></tr>
                        <tr><td class="label">Popularity Score:</td><td class="val">${{p.Popularity}} / 100</td></tr>
                    </table>
                </div>
            `;
        }});
        cardsContainer.innerHTML = cardsHtml;
    }}

    // Render Sub-Map for this District
    renderDistrictSubMap(districtFeature, matchingPlaces);
}}

// Filter strictly by State and District using normalization
function filterDestinations(stateName, districtName) {{
    const sNorm = normalizeName(stateName);
    const dNorm = normalizeName(districtName);

    return TOURISM_DATA.filter(dest => {{
        const destState = normalizeName(dest.State);
        if (destState !== sNorm && !destState.includes(sNorm) && !sNorm.includes(destState)) {{
            return false;
        }}

        // Strict District Match with alias support (Mysuru/Mysore, Kodagu/Coorg, Vijayanagara/Ballari/Bellary)
        const destDist = normalizeName(dest.District);
        if (destDist) {{
            if (destDist === dNorm || destDist.includes(dNorm) || dNorm.includes(destDist)) {{
                return true;
            }}
            if ((dNorm.includes("mysur") || dNorm.includes("mysor")) && (destDist.includes("mysur") || destDist.includes("mysor"))) return true;
            if ((dNorm.includes("kodagu") || dNorm.includes("coorg")) && (destDist.includes("kodagu") || destDist.includes("coorg"))) return true;
            if ((dNorm.includes("vijayanagar") || dNorm.includes("ballari") || dNorm.includes("bellary")) && 
                (destDist.includes("vijayanagar") || destDist.includes("ballari") || destDist.includes("bellary"))) return true;
        }}

        // Check verified address column
        if (dest.Address) {{
            const aNorm = normalizeName(dest.Address);
            if (aNorm.includes(dNorm)) return true;
        }}

        return false;
    }});
}}

// Initialize and render the district sub-map
function renderDistrictSubMap(districtFeature, places) {{
    if (!districtSubMap) {{
        districtSubMap = L.map("district-sub-map", {{
            zoomControl: true
        }});

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(districtSubMap);

        districtMarkersLayer = L.layerGroup().addTo(districtSubMap);
    }}

    districtMarkersLayer.clearLayers();

    setTimeout(() => {{
        districtSubMap.invalidateSize();
    }}, 100);

    let districtBounds = null;

    // Draw district boundary polygon if available
    if (districtFeature) {{
        const distPolygon = L.geoJSON(districtFeature, {{
            style: {{
                fillColor: places.length > 0 ? "#10b981" : "#f59e0b",
                color: "#0f172a",
                weight: 2,
                fillOpacity: 0.25
            }}
        }}).addTo(districtMarkersLayer);

        try {{
            districtBounds = distPolygon.getBounds();
        }} catch(e) {{}}
    }}

    // Place markers for matching destinations
    const markerBounds = [];
    places.forEach(p => {{
        if (p.Latitude && p.Longitude) {{
            const latLng = [p.Latitude, p.Longitude];
            markerBounds.push(latLng);

            const catColors = {{
                "Nature": "#10b981",
                "Cultural": "#f97316",
                "Historical": "#6366f1",
                "Beach": "#06b6d4",
                "Adventure": "#e11d48"
            }};
            const color = catColors[p.Category] || "#0284c7";

            const pinHtml = `
                <div style="background:${{color}}; width:28px; height:28px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 2px 6px rgba(0,0,0,0.35); display:flex; align-items:center; justify-content:center; color:#fff; font-size:13px; font-weight:bold;">
                    📍
                </div>
            `;
            const icon = L.divIcon({{
                className: "custom-marker-icon",
                html: pinHtml,
                iconSize: [28, 28],
                iconAnchor: [14, 14],
                popupAnchor: [0, -14]
            }});

            const popupContent = `
                <div style="font-size:12px; min-width:200px;">
                    <div style="font-size:14px; font-weight:bold; color:#0f172a; margin-bottom:4px;">${{p.Place}}</div>
                    <div style="margin-bottom:6px;"><span class="category-tag cat-${{p.Category}}">${{p.Category}}</span></div>
                    <div style="color:#64748b; font-size:11.5px; margin-bottom:6px;">📍 ${{p.Address}}</div>
                    <hr style="border:0; border-top:1px solid #e2e8f0; margin:4px 0;">
                    <div><b>Rating:</b> ⭐ ${{p.Rating}} / 5.0</div>
                    <div><b>Estimated Cost:</b> ₹${{p.Estimated_Cost.toLocaleString()}}</div>
                    <div><b>Best Time:</b> ${{p.Best_Time}}</div>
                </div>
            `;

            const m = L.marker(latLng, {{ icon: icon }}).addTo(districtMarkersLayer);
            m.bindPopup(popupContent);
        }}
    }});

    // Fit bounds appropriately
    setTimeout(() => {{
        districtSubMap.invalidateSize();
        if (markerBounds.length > 0) {{
            districtSubMap.fitBounds(markerBounds, {{ maxZoom: 12, padding: [40, 40] }});
            // Automatically open popup if only 1 place
            if (markerBounds.length === 1) {{
                districtMarkersLayer.eachLayer(layer => {{
                    if (layer.openPopup) layer.openPopup();
                }});
            }}
        }} else if (districtBounds && districtBounds.isValid()) {{
            districtSubMap.fitBounds(districtBounds, {{ padding: [30, 30] }});
        }} else {{
            // Default center if no geometry
            districtSubMap.setView([12.5, 76.9], 9);
        }}
    }}, 150);
}}

function focusDistrictMarker(lat, lon, placeName) {{
    if (districtSubMap && lat && lon) {{
        districtSubMap.setView([lat, lon], 12);
        districtMarkersLayer.eachLayer(layer => {{
            if (layer.getLatLng && layer.getLatLng().lat === lat && layer.getLatLng().lng === lon) {{
                layer.openPopup();
            }}
        }});
    }}
}}

// Initialize on window load
window.onload = showIndia;
</script>

</body>
</html>
"""
    return html_content
