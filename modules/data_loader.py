import pandas as pd
import numpy as np
import os
import streamlit as st

def load_dataset(file_source=None):
    """
    Final Data Loader: Handles CSV/Excel, fixes naming, and merges Lat/Lon.
    """
    try:
        # --- 1. LOAD MAIN DATASET ---
        if file_source is not None:
            # Handle user uploads
            df = pd.read_excel(file_source) if file_source.name.endswith('.xlsx') else pd.read_csv(file_source)
        else:
            # Load from the local data folder
            file_path = os.path.join("data", "datasets-uidai.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
            else:
                st.warning("Main dataset not found in /data. Loading mock data.")
                return generate_mock_data()

        # --- 2. CLEAN HEADERS (The 'KeyError' Fix) ---
        # Convert to lowercase and replace spaces with underscores
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # --- 3. MERGE LAT/LON MAPPING ---
        mapping_path = os.path.join("data", "pincode-mapping.csv.csv")
        if os.path.exists(mapping_path):
            geo_df = pd.read_csv(mapping_path)
            
            # Normalize mapping headers
            geo_df.columns = geo_df.columns.str.strip().str.lower()
            
            # Map 'latitude' or 'lattitude' to 'lat'
            rename_map = {
                'latitude': 'lat', 
                'lattitude': 'lat', 
                'longitude': 'lon'
            }
            geo_df = geo_df.rename(columns=rename_map)

            # Match pincode types (convert both to strings to be safe)
            df['pincode'] = df['pincode'].astype(str).str.strip()
            geo_df['pincode'] = geo_df['pincode'].astype(str).str.strip()
            
            # Merge coordinates into main data
            df = pd.merge(df, geo_df[['pincode', 'lat', 'lon']], on='pincode', how='left')
        else:
            st.error("Pincode-mapping.csv missing! Map markers will not show.")

        # --- 4. DATA TYPE ENFORCEMENT ---
        age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        for col in age_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        return df

    except Exception as e:
        st.error(f"Critical Engine Error: {e}")
        return generate_mock_data()

def generate_mock_data():
    """Fallback to keep the app running if files are missing."""
    data = {
        'state': ['Karnataka', 'Bihar'],
        'pincode': ['560001', '800001'],
        'lat': [12.97, 25.59],
        'lon': [77.59, 85.13],
        'age_0_5': [100, 200],
        'age_5_17': [300, 400],
        'age_18_greater': [500, 600]
    }
    return pd.DataFrame(data)
