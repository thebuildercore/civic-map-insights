import streamlit as st
import pandas as pd
import re
from modules.data_loader import load_dataset

def clean_coordinate(coord):
    if pd.isna(coord) or coord == "": return 0.0
    if isinstance(coord, (int, float)): return float(coord)
    numeric_part = re.search(r"[-+]?\d*\.\d+|\d+", str(coord))
    if not numeric_part: return 0.0
    val = float(numeric_part.group())
    if any(char in str(coord).upper() for char in ['S', 'W']): val = -val
    return val

@st.cache_data(ttl=3600)
def get_engine_data():
    df = load_dataset()
    if df is None or df.empty:
        return pd.DataFrame()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if 'lat' in df.columns: 
        df['lat'] = df['lat'].apply(clean_coordinate)
    if 'lon' in df.columns: 
        df['lon'] = df['lon'].apply(clean_coordinate)
    return df
