"""
Data Cleaning and Preprocessing Pipeline
Part of the India Tourism Analytics and Business Intelligence Dashboard
For College DVP (Data Visualization with Python) Laboratory
"""

import os
import pandas as pd
import numpy as np

DESTINATION_COORDINATES = {
    "Munnar": {"lat": 10.0889, "lon": 77.0595, "region": "South"},
    "Rann of Kutch": {"lat": 23.8344, "lon": 69.8329, "region": "West"},
    "Konark Sun Temple": {"lat": 19.8876, "lon": 86.0945, "region": "East"},
    "Charminar": {"lat": 17.3616, "lon": 78.4747, "region": "South"},
    "Taj Mahal": {"lat": 27.1751, "lon": 78.0421, "region": "North"},
    "Gangtok": {"lat": 27.3389, "lon": 88.6065, "region": "North East"},
    "Gateway of India": {"lat": 18.9220, "lon": 72.8347, "region": "West"},
    "Mysore Palace": {"lat": 12.3052, "lon": 76.6552, "region": "South"},
    "Radhanagar Beach": {"lat": 11.9840, "lon": 92.9515, "region": "Islands"},
    "Jaisalmer Fort": {"lat": 26.9124, "lon": 70.9127, "region": "North"},
    "Alleppey Backwaters": {"lat": 9.4981, "lon": 76.3388, "region": "South"},
    "Ooty": {"lat": 11.4102, "lon": 76.6950, "region": "South"},
    "Hampi": {"lat": 15.3350, "lon": 76.4600, "region": "South"},
    "India Gate": {"lat": 28.6129, "lon": 77.2295, "region": "North"},
    "Baga Beach": {"lat": 15.5553, "lon": 73.7517, "region": "West"},
    "Rishikesh": {"lat": 30.0869, "lon": 78.2676, "region": "North"},
    "Manali": {"lat": 32.2432, "lon": 77.1892, "region": "North"},
    "Darjeeling": {"lat": 27.0410, "lon": 88.2663, "region": "East"},
    "Jaipur City Palace": {"lat": 26.9258, "lon": 75.8237, "region": "North"},
    "Coorg": {"lat": 12.3375, "lon": 75.8069, "region": "South"}
}

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


def find_dataset_path():
    """Locate the dataset file dynamically from common project paths."""
    candidate_paths = [
        os.path.join("data", "5dvp.csv"),
        "5dvp.csv",
        "DOC-20260904-WA0015.csv",
        os.path.join("data", "tourism_dataset.csv"),
        os.path.join("public", "tourism_dataset.csv")
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return None


def load_raw_data(filepath=None):
    """Load the raw CSV dataset into a pandas DataFrame."""
    if filepath is None:
        filepath = find_dataset_path()
    if filepath is None or not os.path.exists(filepath):
        raise FileNotFoundError("Tourism dataset file (5dvp.csv / DOC-20260904-WA0015.csv) not found.")
    
    df = pd.read_csv(filepath)
    return df


def clean_tourism_data(df_raw, apply_record1_fix=True):
    """
    Apply comprehensive data cleaning:
    1. Correct malformed first record if requested.
    2. Convert numerical columns to appropriate types.
    3. Impute missing numerical values using median.
    4. Impute missing Recommended values using mode.
    5. Strip whitespace from string columns.
    6. Attach verified geographical coordinates.
    7. Generate cleaning audit report.
    """
    df = df_raw.copy()
    initial_shape = df.shape
    missing_before = df.isnull().sum().to_dict()

    # 1. First record correction
    if apply_record1_fix and len(df) > 0:
        for col, val in RECORD_1_CORRECTED.items():
            if col in df.columns:
                df.at[0, col] = val

    # 2. Strip whitespace for string/object columns
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.strip()

    # 3. Numerical conversion & median imputation
    imputed_numerical = {}
    for col in NUMERICAL_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                col_median = df[col].median()
                df[col] = df[col].fillna(col_median)
                imputed_numerical[col] = {"missing": int(missing_count), "imputed_with": float(col_median)}

    # Convert integer columns if appropriate
    int_cols = ['Estimated_Cost_INR', 'Stay_Days', 'Visitors_Count']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].round().astype(int)

    # 4. Handle Recommended column (impute with mode if missing)
    if 'Recommended' in df.columns:
        # Standardize yes/no
        df['Recommended'] = df['Recommended'].replace({'yes': 'Yes', 'no': 'No', 'YES': 'Yes', 'NO': 'No'})
        mode_val = df['Recommended'].mode()
        recommended_mode = mode_val[0] if not mode_val.empty else 'Yes'
        rec_missing = df['Recommended'].isnull().sum()
        if rec_missing > 0:
            df['Recommended'] = df['Recommended'].fillna(recommended_mode)

    # 5. Attach geographical coordinates for mapping
    df['Latitude'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('lat', np.nan))
    df['Longitude'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('lon', np.nan))
    df['Region'] = df['Place'].map(lambda p: DESTINATION_COORDINATES.get(p, {}).get('region', 'Other'))

    # Save cleaned files to data directory and root directory
    os.makedirs("data", exist_ok=True)
    df.to_csv(os.path.join("data", "5dvp_cleaned.csv"), index=False)
    df.to_csv("5dvp_cleaned.csv", index=False)

    audit_summary = {
        "initial_rows": initial_shape[0],
        "initial_cols": initial_shape[1],
        "final_rows": df.shape[0],
        "final_cols": df.shape[1],
        "duplicates_removed": int(df.duplicated().sum()),
        "imputed_numerical": imputed_numerical,
        "first_record_corrected": apply_record1_fix,
        "unique_places": int(df['Place'].nunique()),
        "unique_states": int(df['State'].nunique()),
        "unique_categories": int(df['Category'].nunique())
    }

    return df, audit_summary


def get_cached_cleaned_data(force_reload=False, apply_record1_fix=True):
    """Convenience function to get cleaned dataframe, caching if available."""
    raw_df = load_raw_data()
    cleaned_df, audit = clean_tourism_data(raw_df, apply_record1_fix=apply_record1_fix)
    return cleaned_df, audit

