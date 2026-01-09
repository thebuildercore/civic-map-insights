import folium
import pandas as pd
from folium.plugins import HeatMap

def create_base_map(center, zoom):
    return folium.Map(location=center, zoom_start=zoom, tiles='CartoDB Positron')



# Revised function to load local GeoJSON file for state boundaries
import os
import json

def add_state_boundaries(m, selected_state):
    """
    Loads local GeoJSON and highlights the selected state.
    """
    # 1. Path to your local file
    file_path = os.path.join("data", "india_states.json")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    # 2. Load the data manually
    with open(file_path, 'r', encoding='utf-8') as f:
        geo_data = json.load(f)

    # 3. Standard Key for this specific file is 'ST_NM' 
    # (Note: Most official files use Uppercase ST_NM)
    state_field = 'ST_NM' 

    folium.GeoJson(
        geo_data,
        name="State Boundaries",
        style_function=lambda x: {
            'fillColor': '#22c55e' if x['properties'].get(state_field) == selected_state else 'transparent',
            'color': 'blue' if x['properties'].get(state_field) == selected_state else '#808080',
            'weight': 3 if x['properties'].get(state_field) == selected_state else 0.5,
            'fillOpacity': 0.2 if x['properties'].get(state_field) == selected_state else 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[state_field], 
            aliases=['State:'], 
            localize=True
        )
    ).add_to(m)


def add_heatmap(m, data, age_col):
    """
    Creates a density heatmap.
    'data' must have 'lat', 'lon', and the age column.
    """
    # 1. Drop rows without coordinates to prevent errors
    heat_df = data.dropna(subset=['lat', 'lon'])
    
    # 2. Format: [[lat, lon, weight], [lat, lon, weight]...]
    heat_data = heat_df[['lat', 'lon', age_col]].values.tolist()
    
    # 3. Add HeatMap layer
    if heat_data:
        HeatMap(
            heat_data,
            radius=15, 
            blur=10, 
            min_opacity=0.4,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'} # Blue=Low, Red=High
        ).add_to(m)
        

def add_signals(m, data, age_column):
    # Guard clause: Exit if lat/lon are missing from the dataframe
    if 'lat' not in data.columns or 'lon' not in data.columns:
        return 

    for _, row in data.iterrows():
        # Check if the specific row has valid coordinates
        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=float(row[age_column]) / 20 if row[age_column] > 0 else 2,
                color='red',
                fill=True,
                fill_opacity=0.6,
                popup=f"Count: {row[age_column]}"
            ).add_to(m)
