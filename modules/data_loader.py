# import pandas as pd
# import numpy as np
# import os
# import streamlit as st

# def load_dataset(file_source=None):
#     """
#     Final Data Loader: Handles CSV/Excel, fixes naming, and merges Lat/Lon.
#     """
#     try:
#         # --- 1. LOAD MAIN DATASET ---
#         if file_source is not None:
#             # Handle user uploads
#             df = pd.read_excel(file_source) if file_source.name.endswith('.xlsx') else pd.read_csv(file_source)
#         else:
#             # Load from the local data folder
#             file_path = os.path.join("data", "datasets-uidai.csv")
#             if os.path.exists(file_path):
#                 df = pd.read_csv(file_path)
#             else:
#                 st.warning("Main dataset not found in /data. Loading mock data.")
#                 return generate_mock_data()

#         # --- 2. CLEAN HEADERS (The 'KeyError' Fix) ---
#         # Convert to lowercase and replace spaces with underscores
#         df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

#         # --- 3. MERGE LAT/LON MAPPING ---
#         mapping_path = os.path.join("data", "pincode-mapping.csv.csv")
#         if os.path.exists(mapping_path):
#             geo_df = pd.read_csv(mapping_path)
            
#             # Normalize mapping headers
#             geo_df.columns = geo_df.columns.str.strip().str.lower()
            
#             # Map 'latitude' or 'lattitude' to 'lat'
#             rename_map = {
#                 'latitude': 'lat', 
#                 'lattitude': 'lat', 
#                 'longitude': 'lon'
#             }
#             geo_df = geo_df.rename(columns=rename_map)

#             # Match pincode types (convert both to strings to be safe)
#             df['pincode'] = df['pincode'].astype(str).str.strip()
#             geo_df['pincode'] = geo_df['pincode'].astype(str).str.strip()
            
#             # Merge coordinates into main data
#             df = pd.merge(df, geo_df[['pincode', 'lat', 'lon']], on='pincode', how='left')
#         else:
#             st.error("Pincode-mapping.csv missing! Map markers will not show.")

#         # --- 4. DATA TYPE ENFORCEMENT ---
#         age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
#         for col in age_cols:
#             if col in df.columns:
#                 df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

#         return df

#     except Exception as e:
#         st.error(f"Critical Engine Error: {e}")
#         return generate_mock_data()

# def generate_mock_data():
#     """Fallback to keep the app running if files are missing."""
#     data = {
#         'state': ['Karnataka', 'Bihar'],
#         'pincode': ['560001', '800001'],
#         'lat': [12.97, 25.59],
#         'lon': [77.59, 85.13],
#         'age_0_5': [100, 200],
#         'age_5_17': [300, 400],
#         'age_18_greater': [500, 600]
#     }
#     return pd.DataFrame(data)


# Version 2

import pandas as pd
import numpy as np
import os
import streamlit as st

def get_smart_path(filename):
    """Checks the root and data folders to find files regardless of script location."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    paths = [
        filename,                                     # Current Dir
        os.path.join("data", filename),               # /data/ folder
        os.path.join(project_root, filename),         # Root folder
        os.path.join(project_root, "data", filename)  # Root/data/ folder
    ]
    for path in paths:
        if os.path.exists(path): return path
    return None

@st.cache_data(show_spinner="Booting Data Engine...")
def load_dataset():
    """
    Safely loads UIDAI data and merges geospatial coordinates.
    Fixes the 'Mangled String' TypeError and CSV formatting issues.
    """
    # --- 1. LOAD MAIN PARQUET FILE ---
    parquet_path = get_smart_path("uidai_data.parquet")
    if not parquet_path:
        st.error("❌ 'uidai_data.parquet' not found. Please run 'convert_data.py' first.")
        return pd.DataFrame()

    df = pd.read_parquet(parquet_path)
    # Clean headers (lowercase, no spaces)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # --- 2. LOAD & MERGE COORDINATES (The Anti-Crash Fix) ---
    mapping_path = get_smart_path("pincode-mapping.csv")
    
    if mapping_path:
        try:
            # PROTECTION: We read as 'str' first. This prevents Pandas from 
            # smushing rows together when it sees messy 'NA' or extra commas.
            geo_df = pd.read_csv(
                mapping_path, 
                usecols=[0, 1, 2], 
                dtype=str,               # Force string to avoid TypeError
                na_values=['NA', 'nan'], 
                on_bad_lines='skip',     # Skips rows that would cause a crash
                engine='python'          # More robust for messy CSVs
            )
            
            # Standardize names
            geo_df.columns = geo_df.columns.str.strip().str.lower()
            geo_df = geo_df.rename(columns={'latitude': 'lat', 'lattitude': 'lat', 'longitude': 'lon'})

            # SAFE CONVERSION: Only convert to numbers now that file is in memory
            # Any 'mangled' strings are turned into NaN (empty) instead of crashing
            geo_df['lat'] = pd.to_numeric(geo_df['lat'], errors='coerce')
            geo_df['lon'] = pd.to_numeric(geo_df['lon'], errors='coerce')
            
            # Remove rows where coordinates are missing/broken
            geo_df = geo_df.dropna(subset=['lat', 'lon'])

            # CLEAN PINCODES: Handle format differences (e.g., 504299.0 vs 504299)
            df['pincode'] = df['pincode'].astype(str).str.split('.').str[0].str.strip()
            geo_df['pincode'] = geo_df['pincode'].astype(str).str.split('.').str[0].str.strip()
            
            # Deduplicate mapping and Merge
            geo_df = geo_df.drop_duplicates(subset=['pincode'])
            df = pd.merge(df, geo_df[['pincode', 'lat', 'lon']], on='pincode', how='left')
            
        except Exception as e:
            st.warning(f"⚠️ Map Loading Issue: {e}")
    else:
        st.info("💡 Note: Geospatial mapping file not found. Map features disabled.")

    # --- 3. FINAL DATA TYPE ENFORCEMENT ---
    # Convert Date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Convert Age Columns to Clean Integers
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    for col in age_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    return df
