"""
Data Cleaning and Preprocessing Pipeline
Part of India Tourism Analytics and Business Intelligence Dashboard (Flask Web App)
"""

import os
import pandas as pd
import numpy as np

DESTINATION_COORDINATES = {
    "Ajanta Caves": {
        "lat": 20.5519,
        "lon": 75.7033,
        "region": "West",
        "district": "Aurangabad"
    },
    "Alleppey Backwaters": {
        "lat": 9.4981,
        "lon": 76.3388,
        "region": "South",
        "district": "Alappuzha"
    },
    "Amber Fort": {
        "lat": 26.9855,
        "lon": 75.8513,
        "region": "North",
        "district": "Jaipur"
    },
    "Badami Cave Temples": {
        "lat": 15.9189,
        "lon": 75.6766,
        "region": "South",
        "district": "Bagalkote"
    },
    "Baga Beach": {
        "lat": 15.5553,
        "lon": 73.7517,
        "region": "West",
        "district": "North Goa"
    },
    "Bangalore Palace": {
        "lat": 12.9988,
        "lon": 77.5921,
        "region": "South",
        "district": "Bengaluru Urban"
    },
    "Bara Imambara": {
        "lat": 26.869,
        "lon": 80.913,
        "region": "North",
        "district": "Lucknow"
    },
    "Belavadi Veeranarayana Temple": {
        "lat": 13.2842,
        "lon": 75.9863,
        "region": "South",
        "district": "Chikkamagaluru"
    },
    "Belgaum Fort": {
        "lat": 15.8617,
        "lon": 74.5208,
        "region": "South",
        "district": "Belagavi"
    },
    "Bellary Fort": {
        "lat": 15.1444,
        "lon": 76.9214,
        "region": "South",
        "district": "Ballari"
    },
    "Belur Chennakeshava Temple": {
        "lat": 13.1625,
        "lon": 75.8596,
        "region": "South",
        "district": "Hassan"
    },
    "Bethur Shiva Temple": {
        "lat": 14.4921,
        "lon": 75.9524,
        "region": "South",
        "district": "Davanagere"
    },
    "Bhoga Nandeeshwara Temple": {
        "lat": 13.3854,
        "lon": 77.6974,
        "region": "South",
        "district": "Chikkaballapura"
    },
    "Bidar Fort": {
        "lat": 17.9234,
        "lon": 77.5199,
        "region": "South",
        "district": "Bidar"
    },
    "Brihadisvara Temple": {
        "lat": 10.7828,
        "lon": 79.1318,
        "region": "South",
        "district": "Thanjavur"
    },
    "Cellular Jail": {
        "lat": 11.6739,
        "lon": 92.7478,
        "region": "Islands",
        "district": "South Andaman"
    },
    "Chandramouleshwara Temple": {
        "lat": 15.3725,
        "lon": 75.1245,
        "region": "South",
        "district": "Dharwad"
    },
    "Charminar": {
        "lat": 17.3616,
        "lon": 78.4747,
        "region": "South",
        "district": "Hyderabad"
    },
    "Chitradurga Fort": {
        "lat": 14.2183,
        "lon": 76.3986,
        "region": "South",
        "district": "Chitradurga"
    },
    "City Palace Udaipur": {
        "lat": 24.5764,
        "lon": 73.6835,
        "region": "North",
        "district": "Udaipur"
    },
    "Coorg": {
        "lat": 12.3375,
        "lon": 75.8069,
        "region": "South",
        "district": "Kodagu"
    },
    "Darjeeling": {
        "lat": 27.041,
        "lon": 88.2663,
        "region": "East",
        "district": "Darjeeling"
    },
    "Devanahalli Fort": {
        "lat": 13.2483,
        "lon": 77.7126,
        "region": "South",
        "district": "Bengaluru Rural"
    },
    "Fatehpur Sikri": {
        "lat": 27.0945,
        "lon": 77.6679,
        "region": "North",
        "district": "Agra"
    },
    "Gangtok": {
        "lat": 27.3389,
        "lon": 88.6065,
        "region": "North East",
        "district": "East Sikkim"
    },
    "Gateway of India": {
        "lat": 18.922,
        "lon": 72.8347,
        "region": "West",
        "district": "Mumbai City"
    },
    "Gol Gumbaz": {
        "lat": 16.8306,
        "lon": 75.7364,
        "region": "South",
        "district": "Vijayapura"
    },
    "Golconda Fort": {
        "lat": 17.3833,
        "lon": 78.4011,
        "region": "South",
        "district": "Hyderabad"
    },
    "Gulbarga Fort": {
        "lat": 17.3435,
        "lon": 76.8282,
        "region": "South",
        "district": "Kalaburagi"
    },
    "Hampi": {
        "lat": 15.335,
        "lon": 76.46,
        "region": "South",
        "district": "Vijayanagara"
    },
    "Himavad Gopalaswamy Betta": {
        "lat": 11.7214,
        "lon": 76.6022,
        "region": "South",
        "district": "Chamarajanagara"
    },
    "India Gate": {
        "lat": 28.6129,
        "lon": 77.2295,
        "region": "North",
        "district": "New Delhi"
    },
    "Jaipur City Palace": {
        "lat": 26.9258,
        "lon": 75.8237,
        "region": "North",
        "district": "Jaipur"
    },
    "Jaisalmer Fort": {
        "lat": 26.9124,
        "lon": 70.9127,
        "region": "North",
        "district": "Jaisalmer"
    },
    "Kashi Vishwanath Temple": {
        "lat": 25.3109,
        "lon": 83.0107,
        "region": "North",
        "district": "Varanasi"
    },
    "Keladi Rameshwara Temple": {
        "lat": 14.2189,
        "lon": 75.0125,
        "region": "South",
        "district": "Shivamogga"
    },
    "Konark Sun Temple": {
        "lat": 19.8876,
        "lon": 86.0945,
        "region": "East",
        "district": "Puri"
    },
    "Madhugiri Fort": {
        "lat": 13.6631,
        "lon": 77.2114,
        "region": "South",
        "district": "Tumakuru"
    },
    "Madikeri Fort": {
        "lat": 12.4244,
        "lon": 75.7382,
        "region": "South",
        "district": "Kodagu"
    },
    "Mahadeva Temple Itagi": {
        "lat": 15.4673,
        "lon": 75.9892,
        "region": "South",
        "district": "Koppal"
    },
    "Manali": {
        "lat": 32.2432,
        "lon": 77.1892,
        "region": "North",
        "district": "Kullu"
    },
    "Mangaladevi Temple": {
        "lat": 12.8524,
        "lon": 74.8488,
        "region": "South",
        "district": "Dakshina Kannada"
    },
    "Meenakshi Amman Temple": {
        "lat": 9.9195,
        "lon": 78.1193,
        "region": "South",
        "district": "Madurai"
    },
    "Mehrangarh Fort": {
        "lat": 26.298,
        "lon": 73.0189,
        "region": "North",
        "district": "Jodhpur"
    },
    "Mirjan Fort": {
        "lat": 14.4925,
        "lon": 74.4219,
        "region": "South",
        "district": "Uttara Kannada"
    },
    "Munnar": {
        "lat": 10.0889,
        "lon": 77.0595,
        "region": "South",
        "district": "Idukki"
    },
    "Mysore Palace": {
        "lat": 12.3052,
        "lon": 76.6552,
        "region": "South",
        "district": "Mysuru"
    },
    "Ooty": {
        "lat": 11.4102,
        "lon": 76.695,
        "region": "South",
        "district": "Nilgiris"
    },
    "Qutub Minar": {
        "lat": 28.5244,
        "lon": 77.1855,
        "region": "North",
        "district": "South Delhi"
    },
    "Radhanagar Beach": {
        "lat": 11.984,
        "lon": 92.9515,
        "region": "Islands",
        "district": "South Andaman"
    },
    "Raichur Fort": {
        "lat": 16.2076,
        "lon": 77.3556,
        "region": "South",
        "district": "Raichur"
    },
    "Ramadevara Betta": {
        "lat": 12.7483,
        "lon": 77.2917,
        "region": "South",
        "district": "Ramanagara"
    },
    "Rann of Kutch": {
        "lat": 23.8344,
        "lon": 69.8329,
        "region": "West",
        "district": "Kutch"
    },
    "Red Fort": {
        "lat": 28.6562,
        "lon": 77.241,
        "region": "North",
        "district": "North Delhi"
    },
    "Rishikesh": {
        "lat": 30.0869,
        "lon": 78.2676,
        "region": "North",
        "district": "Dehradun"
    },
    "Sabarmati Ashram": {
        "lat": 23.0605,
        "lon": 72.5802,
        "region": "West",
        "district": "Ahmedabad"
    },
    "Shaniwar Wada": {
        "lat": 18.5196,
        "lon": 73.8553,
        "region": "West",
        "district": "Pune"
    },
    "Siddheshwara Temple": {
        "lat": 14.7958,
        "lon": 75.4012,
        "region": "South",
        "district": "Haveri"
    },
    "Someshwara Temple Kolar": {
        "lat": 13.1367,
        "lon": 78.1342,
        "region": "South",
        "district": "Kolar"
    },
    "Sri Krishna Temple Udupi": {
        "lat": 13.3409,
        "lon": 74.7421,
        "region": "South",
        "district": "Udupi"
    },
    "Srirangapatna Fort & Temple": {
        "lat": 12.4228,
        "lon": 76.6853,
        "region": "South",
        "district": "Mandya"
    },
    "Taj Mahal": {
        "lat": 27.1751,
        "lon": 78.0421,
        "region": "North",
        "district": "Agra"
    },
    "Trikuteshwara Temple": {
        "lat": 15.4262,
        "lon": 75.6321,
        "region": "South",
        "district": "Gadag"
    },
    "Victoria Memorial": {
        "lat": 22.5448,
        "lon": 88.3426,
        "region": "East",
        "district": "Kolkata"
    },
    "Yadgir Fort": {
        "lat": 16.7644,
        "lon": 77.1389,
        "region": "South",
        "district": "Yadgir"
    },
    "Kunti Betta": {
        "lat": 12.5028,
        "lon": 76.6806,
        "region": "South",
        "district": "Mandya"
    },
    "Chamundi Betta": {
        "lat": 12.2750,
        "lon": 76.6714,
        "region": "South",
        "district": "Mysuru"
    },
    "Nanjungudu": {
        "lat": 12.1194,
        "lon": 76.6806,
        "region": "South",
        "district": "Mysuru"
    },
    "Nanjangud": {
        "lat": 12.1194,
        "lon": 76.6806,
        "region": "South",
        "district": "Mysuru"
    },
    "Dharmasthala": {
        "lat": 12.9575,
        "lon": 75.3817,
        "region": "South",
        "district": "Dakshina Kannada"
    },
    "Murudeshwara": {
        "lat": 14.0942,
        "lon": 74.4847,
        "region": "South",
        "district": "Uttara Kannada"
    },
    "Gokarna Beach": {
        "lat": 14.5436,
        "lon": 74.3181,
        "region": "South",
        "district": "Uttara Kannada"
    },
    "Om Beach": {
        "lat": 14.5167,
        "lon": 74.3167,
        "region": "South",
        "district": "Uttara Kannada"
    },
    "Kukke Subramanya": {
        "lat": 12.6667,
        "lon": 75.6167,
        "region": "South",
        "district": "Dakshina Kannada"
    },
    "Horanadu": {
        "lat": 13.2750,
        "lon": 75.3417,
        "region": "South",
        "district": "Chikkamagaluru"
    },
    "Kemmangundi": {
        "lat": 13.5472,
        "lon": 75.7583,
        "region": "South",
        "district": "Chikkamagaluru"
    },
    "Mandalpatti": {
        "lat": 12.5167,
        "lon": 75.7000,
        "region": "South",
        "district": "Kodagu"
    },
    "Maravanthe Beach": {
        "lat": 13.7083,
        "lon": 74.6417,
        "region": "South",
        "district": "Udupi"
    },
    "Sigandur": {
        "lat": 14.1833,
        "lon": 74.8833,
        "region": "South",
        "district": "Shivamogga"
    },
    "Agumbe": {
        "lat": 13.5028,
        "lon": 75.0931,
        "region": "South",
        "district": "Shivamogga"
    },
    "Talakad": {
        "lat": 12.1889,
        "lon": 77.0319,
        "region": "South",
        "district": "Mysuru"
    },
    "Melukote": {
        "lat": 12.6689,
        "lon": 76.6528,
        "region": "South",
        "district": "Mandya"
    }
}

DESTINATION_DISTRICT_MAP = {k: v["district"] for k, v in DESTINATION_COORDINATES.items()}

NUMERICAL_COLUMNS = [
    'Rating',
    'Estimated_Cost_INR',
    'Stay_Days',
    'Visitors_Count',
    'Popularity_Score',
    'Cleanliness_Rating',
    'Safety_Rating',
    'Accessibility_Rating'
]

CATEGORICAL_COLUMNS = [
    'State',
    'Place',
    'Category',
    'Location_Type',
    'Best_Time_to_Visit',
    'Visit_Month',
    'Season',
    'Age_Group',
    'Gender',
    'Travel_Group',
    'Recommended'
]

RECORD_1_CORRECTED = {
    'Visitor_ID': 'V0001',
    'State': 'Kerala',
    'Place': 'Munnar',
    'Address': 'Idukki, Kerala',
    'Category': 'Nature',
    'Location_Type': 'Hill Station',
    'Best_Time_to_Visit': 'September to March',
    'Visit_Month': 'March',
    'Season': 'Summer',
    'Age_Group': '36-50',
    'Gender': 'Male',
    'Travel_Group': 'Couple',
    'Review': 'Beautiful place with excellent views and memorable experience.',
    'Rating': 4.7,
    'Estimated_Cost_INR': 2913,
    'Stay_Days': 1,
    'Visitors_Count': 919,
    'Popularity_Score': 43.39,
    'Cleanliness_Rating': 3.1,
    'Safety_Rating': 3.4,
    'Accessibility_Rating': 3.8,
    'Recommended': 'Yes'
}

_CACHED_CLEANED_DF = None


def find_dataset_path():
    """Locate the dataset file dynamically."""
    candidate_paths = [
        os.path.join("data", "5dvp_cleaned.csv"),
        "5dvp_cleaned.csv",
        os.path.join("data", "5dvp.csv"),
        "5dvp.csv",
        "DOC-20260904-WA0015.csv"
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return None


def clean_tourism_data(df_raw, apply_record1_fix=True):
    """Apply data cleaning pipeline and attach verified coordinates."""
    df = df_raw.copy()

    # 1. First record correction if needed
    if apply_record1_fix and len(df) > 0:
        for col, val in RECORD_1_CORRECTED.items():
            if col in df.columns:
                df.at[0, col] = val

    # 2. Strip whitespace
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.strip()

    # 3. Numerical conversion & median imputation
    for col in NUMERICAL_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].median())

    int_cols = ['Estimated_Cost_INR', 'Stay_Days', 'Visitors_Count']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].round().astype(int)

    # 4. Standardize Recommended
    if 'Recommended' in df.columns:
        df['Recommended'] = df['Recommended'].replace({'yes': 'Yes', 'no': 'No', 'YES': 'Yes', 'NO': 'No'})
        mode_val = df['Recommended'].mode()
        recommended_mode = mode_val[0] if not mode_val.empty else 'Yes'
        df['Recommended'] = df['Recommended'].fillna(recommended_mode)

    # 5. Geocoding
    df['Latitude'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('lat', np.nan))
    df['Longitude'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('lon', np.nan))
    df['Region'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('region', 'Other'))
    df['District'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('district', ''))

    return df


def get_cached_cleaned_data(force_reload=False):
    """Get singleton cleaned DataFrame."""
    global _CACHED_CLEANED_DF
    if _CACHED_CLEANED_DF is not None and not force_reload:
        return _CACHED_CLEANED_DF

    path = find_dataset_path()
    if path is None:
        raise FileNotFoundError("Could not find tourism dataset (5dvp_cleaned.csv / 5dvp.csv).")

    df_raw = pd.read_csv(path)
    # If already cleaned with Latitude/Longitude and 26 cols, quick check
    if 'Latitude' in df_raw.columns and 'District' in df_raw.columns and not force_reload:
        _CACHED_CLEANED_DF = df_raw
    else:
        _CACHED_CLEANED_DF = clean_tourism_data(df_raw)

    return _CACHED_CLEANED_DF


def apply_filters(df, filters=None):
    """
    Apply global dashboard filters to DataFrame:
    filters = {
        'states': list or 'All',
        'categories': list or 'All',
        'seasons': list or 'All',
        'travel_groups': list or 'All',
        'min_rating': float,
        'max_budget': float
    }
    """
    if filters is None:
        return df

    filtered = df.copy()

    states = filters.get('states')
    if states and 'All' not in states and 'All States' not in states and len(states) > 0:
        filtered = filtered[filtered['State'].isin(states)]

    categories = filters.get('categories')
    if categories and 'All' not in categories and 'All Categories' not in categories and len(categories) > 0:
        filtered = filtered[filtered['Category'].isin(categories)]

    seasons = filters.get('seasons')
    if seasons and 'All' not in seasons and 'All Seasons' not in seasons and len(seasons) > 0:
        filtered = filtered[filtered['Season'].isin(seasons)]

    travel_groups = filters.get('travel_groups')
    if travel_groups and 'All' not in travel_groups and 'All Groups' not in travel_groups and len(travel_groups) > 0:
        filtered = filtered[filtered['Travel_Group'].isin(travel_groups)]

    min_rating = filters.get('min_rating')
    if min_rating is not None and min_rating > 0:
        filtered = filtered[filtered['Rating'] >= float(min_rating)]

    max_budget = filters.get('max_budget')
    if max_budget is not None and max_budget > 0:
        filtered = filtered[filtered['Estimated_Cost_INR'] <= float(max_budget)]

    return filtered

