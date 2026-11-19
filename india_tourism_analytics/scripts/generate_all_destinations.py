"""
Complete Production Generator for India Tourist Destinations Master Dataset
Builds a destination catalogue prototype; generated entries use illustrative attributes and approximate coordinates.
Outputs:
1. data/tourist_destinations_master.csv
2. tourist_destinations_master.csv
3. data/destination_source_audit.csv
4. destination_source_audit.csv
5. data/district_coverage_report.md
6. scripts/verify_and_clean_destinations.py
"""

import os
import sys
import json
import re
import math
import random
import pandas as pd
import numpy as np

# Ensure determinism
random.seed(42)
np.random.seed(42)

SCRATCH_DIR = "scratch"
with open(os.path.join(SCRATCH_DIR, "official_districts.json"), "r", encoding="utf-8") as f:
    OFFICIAL_DISTRICTS = json.load(f)

with open(os.path.join(SCRATCH_DIR, "district_centroids.json"), "r", encoding="utf-8") as f:
    DISTRICT_CENTROIDS = json.load(f)

print(f"Loaded {len(OFFICIAL_DISTRICTS)} states and {len(DISTRICT_CENTROIDS)} district centroids.")

# Import or define the data builder functions
from data_sources.south_india import SOUTH_INDIA_DATA

# Create the master list
RECORDS = []
RECORD_KEYS = set()

def get_region(state):
    mapping = {
        "North": ["Delhi", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Ladakh", "Punjab", "Rajasthan", "Uttar Pradesh", "Uttarakhand", "Chandigarh"],
        "South": ["Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Telangana", "Puducherry", "Lakshadweep"],
        "West": ["Goa", "Gujarat", "Maharashtra", "Dadra and Nagar Haveli and Daman and Diu"],
        "Central": ["Madhya Pradesh", "Chhattisgarh"],
        "East": ["Bihar", "Jharkhand", "Odisha", "West Bengal", "Andaman and Nicobar Islands"],
        "North-East": ["Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Sikkim", "Tripura"]
    }
    for r, states in mapping.items():
        if state in states:
            return r
    return "Central"

STATE_PORTAL_MAP = {
    "Karnataka": ("Karnataka Tourism", "https://karnatakatourism.org/"),
    "Kerala": ("Kerala Tourism", "https://keralatourism.org/"),
    "Tamil Nadu": ("Tamil Nadu Tourism", "https://tamilnadutourism.tn.gov.in/"),
    "Maharashtra": ("Maharashtra Tourism (MTDC)", "https://maharashtratourism.gov.in/"),
    "Rajasthan": ("Rajasthan Tourism", "https://tourism.rajasthan.gov.in/"),
    "Uttar Pradesh": ("Uttar Pradesh Tourism", "https://uptourism.gov.in/"),
    "Madhya Pradesh": ("Madhya Pradesh Tourism", "https://mptourism.com/"),
    "Gujarat": ("Gujarat Tourism", "https://gujarattourism.com/"),
    "West Bengal": ("West Bengal Tourism", "https://wbtourism.gov.in/"),
    "Odisha": ("Odisha Tourism", "https://odishatourism.gov.in/"),
    "Himachal Pradesh": ("Himachal Tourism", "https://himachaltourism.gov.in/"),
    "Uttarakhand": ("Uttarakhand Tourism", "https://uttarakhandtourism.gov.in/"),
    "Jammu and Kashmir": ("J&K Tourism", "https://jktourism.jk.gov.in/"),
    "Ladakh": ("Ladakh Tourism", "https://ladakhtourism.gov.in/"),
    "Goa": ("Goa Tourism", "https://goatourism.gov.in/"),
    "Delhi": ("Delhi Tourism", "https://delhitourism.gov.in/"),
    "Punjab": ("Punjab Tourism", "https://punjabtourism.punjab.gov.in/"),
    "Haryana": ("Haryana Tourism", "https://haryanatourism.gov.in/"),
    "Bihar": ("Bihar Tourism", "https://tourism.bihar.gov.in/"),
    "Jharkhand": ("Jharkhand Tourism", "https://tourism.jharkhand.gov.in/"),
    "Chhattisgarh": ("Chhattisgarh Tourism", "https://chhattisgarhtourism.cg.gov.in/"),
    "Assam": ("Assam Tourism", "https://assamtourism.gov.in/"),
    "Arunachal Pradesh": ("Arunachal Tourism", "https://arunachaltourism.com/"),
    "Meghalaya": ("Meghalaya Tourism", "https://meghalayatourism.in/"),
    "Manipur": ("Manipur Tourism", "https://manipurtourism.gov.in/"),
    "Mizoram": ("Mizoram Tourism", "https://tourism.mizoram.gov.in/"),
    "Nagaland": ("Nagaland Tourism", "https://tourism.nagaland.gov.in/"),
    "Sikkim": ("Sikkim Tourism", "https://sikkimtourism.gov.in/"),
    "Tripura": ("Tripura Tourism", "https://tripuratourism.gov.in/"),
    "Andhra Pradesh": ("Andhra Pradesh Tourism", "https://tourism.ap.gov.in/"),
    "Telangana": ("Telangana Tourism", "https://telanganatourism.gov.in/"),
    "Puducherry": ("Pondicherry Tourism", "https://pondytourism.py.gov.in/"),
    "Chandigarh": ("Chandigarh Tourism", "https://chandigarhtourism.gov.in/"),
    "Andaman and Nicobar Islands": ("Andaman Tourism", "https://www.andamantourism.gov.in/"),
    "Dadra and Nagar Haveli and Daman and Diu": ("Daman & Diu Tourism", "https://ddd.gov.in/"),
    "Lakshadweep": ("Lakshadweep Tourism", "https://lakshadweep.gov.in/")
}

def get_district_portal(state, dist):
    clean = re.sub(r'[^a-z0-9]+', '', dist.lower())
    return (f"District Administration {dist}", f"https://{clean}.nic.in/")

def add_record(state, district, place, taluk, category, loc_type, best_time, month, season, rating, cost, stay, lat, lon, org, url, address=""):
    key = (state.lower().strip(), district.lower().strip(), place.lower().strip())
    if key in RECORD_KEYS:
        return
    RECORD_KEYS.add(key)
    
    # Boundary check for India latitude and longitude
    lat = max(6.5, min(37.2, float(lat)))
    lon = max(68.2, min(97.3, float(lon)))
    
    RECORDS.append({
        "State": state,
        "District": district,
        "Taluk_Tehsil": taluk,
        "Place": place,
        "Address": address or f"{taluk}, {district}, {state}",
        "Category": category,
        "Location_Type": loc_type,
        "Best_Time_to_Visit": best_time,
        "Visit_Month": month,
        "Season": season,
        "Rating": round(float(rating), 1),
        "Estimated_Cost_INR": int(cost),
        "Stay_Days": int(stay),
        "Latitude": round(float(lat), 5),
        "Longitude": round(float(lon), 5),
        "Region": get_region(state),
        "Source_Organisation": org,
        "Source_URL": url,
        "Verification_Status": "Portal reference listed; not individually verified"
    })

# Add base South India records
for r in SOUTH_INDIA_DATA:
    add_record(
        r["State"], r["District"], r["Place"], r["Taluk_Tehsil"],
        r["Category"], r["Location_Type"], r["Best_Time_to_Visit"],
        r["Visit_Month"], r["Season"], r["Rating"], r["Estimated_Cost_INR"],
        r["Stay_Days"], r["Latitude"], r["Longitude"],
        r["Source_Organisation"], r["Source_URL"], r["Address"]
    )

print(f"Base South India loaded: {len(RECORDS)} records.")
