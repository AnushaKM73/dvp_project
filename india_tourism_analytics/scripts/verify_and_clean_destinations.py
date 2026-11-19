"""
Structural QA Script for the Destination Catalogue Prototype
Checks schema, coarse coordinate bounds, URL format, and district counts. It does not
verify that each named attraction, source URL, rating, cost, or exact location is authentic.
"""

import os
import json
import re
import pandas as pd
import numpy as np

def run_verification(csv_path="data/tourist_destinations_master.csv"):
    print(f"=== Running structural checks on: {csv_path} ===")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: File {csv_path} does not exist.")
        return False
        
    df = pd.read_csv(csv_path)
    print(f"1. Total Records Loaded: {len(df):,}")
    print(f"2. Total Columns: {len(df.columns)}")
    
    # Required columns check
    required_cols = [
        "Destination_ID", "State", "District", "Taluk_Tehsil", "Place",
        "Address", "Category", "Location_Type", "Best_Time_to_Visit",
        "Visit_Month", "Season", "Rating", "Estimated_Cost_INR",
        "Stay_Days", "Latitude", "Longitude", "Region",
        "Source_Organisation", "Source_URL", "Verification_Status"
    ]
    
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}")
        return False
    print("✓ All 20 required schema columns are present.")
    
    # Duplicate check
    dups = df.duplicated(subset=["State", "District", "Place"]).sum()
    print(f"✓ Duplicate (State, District, Place) records: {dups}")
    
    # Geographic bounds check
    lat_min, lat_max = df["Latitude"].min(), df["Latitude"].max()
    lon_min, lon_max = df["Longitude"].min(), df["Longitude"].max()
    print(f"✓ Latitude range: {lat_min:.4f} to {lat_max:.4f} (coarse India bounding box check)")
    print(f"✓ Longitude range: {lon_min:.4f} to {lon_max:.4f} (coarse India bounding box check)")
    assert 6.5 <= lat_min and lat_max <= 37.5, "Latitude out of bounds"
    assert 68.0 <= lon_min and lon_max <= 97.5, "Longitude out of bounds"
    
    # URL validation
    valid_urls = df["Source_URL"].str.startswith("http").all()
    print(f"✓ Source URL strings use http(s): {valid_urls}; destinations were not checked against those pages")
    
    # Official districts validation
    with open("scratch/official_districts.json", "r", encoding="utf-8") as f:
        official_districts = json.load(f)
        
    states_covered = df["State"].nunique()
    total_official_states = len(official_districts)
    print(f"✓ States & UTs Covered: {states_covered} / {total_official_states} ({states_covered/total_official_states*100:.1f}%)")
    
    # District coverage check
    total_official_districts = sum(len(d) for d in official_districts.values())
    covered_districts = df.groupby(["State", "District"]).ngroups
    dist_counts = df.groupby(["State", "District"]).size()
    multi_dest = (dist_counts > 1).sum()
    single_dest = (dist_counts == 1).sum()
    zero_dest = max(0, total_official_districts - covered_districts)
    
    print(f"✓ Directory district groups: {covered_districts}; official-name matching was not performed")
    print(f"✓ Directory groups with multiple entries: {multi_dest}")
    print(f"✓ Districts with single attraction: {single_dest}")
    print(f"✓ Districts with zero attractions: {zero_dest}")
    
    # Category and rating checks
    print(f"✓ Categories ({df['Category'].nunique()}): {list(df['Category'].unique())}")
    print(f"✓ Average Rating: {df['Rating'].mean():.2f} / 5.0 (Min: {df['Rating'].min()}, Max: {df['Rating'].max()})")
    print(f"✓ Average Estimated Cost: ₹{df['Estimated_Cost_INR'].mean():,.0f} (Min: ₹{df['Estimated_Cost_INR'].min()}, Max: ₹{df['Estimated_Cost_INR'].max()})")
    
    print("\n=== Structural checks completed; source authenticity was not verified. ===")
    return True

if __name__ == "__main__":
    run_verification()
