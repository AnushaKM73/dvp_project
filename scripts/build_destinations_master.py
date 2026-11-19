"""
Comprehensive Master Tourist Destinations Dataset Builder for India Tourism Analytics
Builds a destination catalogue prototype; generated entries are not individually verified.
Integrates official sources: ASI, Ministry of Tourism (Incredible India), State Tourism Portals, District NIC Portals.
"""

import os
import json
import re
import math
import random
import pandas as pd
import numpy as np

# Set deterministic seed for reproducibility
random.seed(42)
np.random.seed(42)

# Load official districts and centroids
SCRATCH_DIR = "scratch"
with open(os.path.join(SCRATCH_DIR, "official_districts.json"), "r", encoding="utf-8") as f:
    OFFICIAL_DISTRICTS = json.load(f)

with open(os.path.join(SCRATCH_DIR, "district_centroids.json"), "r", encoding="utf-8") as f:
    DISTRICT_CENTROIDS = json.load(f)

# Region mapping
REGION_MAP = {
    "Northern": ["Delhi", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Ladakh", "Punjab", "Rajasthan", "Uttar Pradesh", "Uttarakhand", "Chandigarh"],
    "Southern": ["Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Telangana", "Puducherry", "Lakshadweep"],
    "Western": ["Goa", "Gujarat", "Maharashtra", "Dadra and Nagar Haveli and Daman and Diu"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
    "Eastern": ["Bihar", "Jharkhand", "Odisha", "West Bengal", "Andaman and Nicobar Islands"],
    "North-Eastern": ["Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Sikkim", "Tripura"]
}

def get_region(state):
    for r, states in REGION_MAP.items():
        if state in states:
            return r
    return "Central"

# Official Portal Mapping
STATE_PORTALS = {
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

def clean_slug(text):
    return re.sub(r'[^a-z0-9]+', '', text.lower())

print("Loaded base configurations successfully.")

