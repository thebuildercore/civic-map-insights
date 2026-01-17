
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from modules.data_processor import get_engine_data

# --- 1. UI STYLING & SETTINGS ---
st.markdown("""
    <style>
    .main > div { padding-top: 1rem; }
    footer {visibility: hidden;}
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4259; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING ---
df = get_engine_data()

if df.empty:
    st.error("❌ Data Engine Error: Could not load 'uidai_data.parquet'.")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.title("🇮🇳 UIDAI Dashboard")
st.sidebar.info("Operational Overview")

age_options = {"Infants (0-5)": "age_0_5", "Youth (5-17)": "age_5_17", "Adults (18+)": "age_18_greater"}
age_label = st.sidebar.selectbox("Target Age Group:", list(age_options.keys()), key="main_age")
age_filter = age_options[age_label]

all_states = ["All India"] + sorted(df['state'].unique().tolist())
selected_state = st.sidebar.selectbox("Select State:", all_states, key="main_state")

# Timeline Logic
filtered_df = df.copy()
if 'date' in df.columns:
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    date_range = st.sidebar.date_input("Timeline:", [min_date, max_date], key="main_date")
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & 
                                  (filtered_df['date'].dt.date <= end_date)]

if selected_state != "All India":
    filtered_df = filtered_df[filtered_df['state'] == selected_state]

# --- 4. TOP METRICS ---
st.title(f"📊 Analytics Control Center: {selected_state}")
m1, m2, m3 = st.columns(3)
m1.metric("Total Infants", f"{int(filtered_df['age_0_5'].sum()):,}")
m2.metric("Total Youth", f"{int(filtered_df['age_5_17'].sum()):,}")
m3.metric("Total Adults", f"{int(filtered_df['age_18_greater'].sum()):,}")

st.divider()

# --- 5. VISUALIZATION TABS ---
tab_map, tab_analytics, tab_raw_data = st.tabs([" Geospatial Map", " Graph Pulse", " Detailed Records"])

# with tab_map: this worked..as 3d map
#     col_t1, col_t2 = st.columns([3, 1])
#     with col_t1:
#         st.subheader(f" Enrollment Density: {age_label}")
#     with col_t2:
#         mode_3d = st.toggle(" 3D Intelligence Mode", help="Towers represent local volume density.")

#     # Data Prep for Map
#     map_data = filtered_df.copy()
#     map_data['lat'] = pd.to_numeric(map_data['lat'], errors='coerce')
#     map_data['lon'] = pd.to_numeric(map_data['lon'], errors='coerce')
#     map_data['weight'] = pd.to_numeric(map_data[age_filter], errors='coerce').fillna(0)
#     map_data = map_data.dropna(subset=['lat', 'lon'])

#     if not map_data.empty:
#         view_state = pdk.ViewState(
#             latitude=map_data['lat'].median(),
#             longitude=map_data['lon'].median(),
#             zoom=5,
#             pitch=45 if mode_3d else 0,
#             bearing=0
#         )

#         if mode_3d:
#             # 3D TOWER VIEW (ColumnLayer)
#             layer = pdk.Layer(
#                 "ColumnLayer",
#                 data=map_data,
#                 get_position='[lon, lat]',
#                 get_elevation='weight',
#                 elevation_scale=200, 
#                 radius=3000,
#                 get_fill_color='[weight * 2, 100, 255, 180]',
#                 pickable=True,
#                 extruded=True,
#             )
#             st.info(" **Insights:** Taller towers indicate high-pressure enrollment zones.")
#         else:
#             # FAST HEATMAP VIEW
#             layer = pdk.Layer(
#                 "HeatmapLayer",
#                 data=map_data,
#                 get_position='[lon, lat]',
#                 get_weight='weight',
#                 radius_pixels=30,
#                 intensity=1,
#                 threshold=0.05
#             )

#         st.pydeck_chart(pdk.Deck(
#             layers=[layer],
#             initial_view_state=view_state,
#             map_style='dark',
#             tooltip={"text": "Enrollment Count: {weight}"} if mode_3d else None
#         ), width="stretch")
#         st.info(f" Visualizing {len(map_data):,} operational points.")
#     else:
#         st.warning("⚠️ No valid geographic data found for this selection.")
        
with tab_map:
    # 1. Header & Toggle
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader(f" Enrollment Density: {age_label}")
    with col_t2:
        mode_3d = st.toggle(" 3D Intelligence Mode", help="Towers represent local volume density.")

    # 2. Data Prep
    map_data = filtered_df.copy()
    map_data['lat'] = pd.to_numeric(map_data['lat'], errors='coerce')
    map_data['lon'] = pd.to_numeric(map_data['lon'], errors='coerce')
    map_data['weight'] = pd.to_numeric(map_data[age_filter], errors='coerce').fillna(0)
    map_data = map_data.dropna(subset=['lat', 'lon'])

    # 3. Visualization Logic
    if not map_data.empty:
        view_state = pdk.ViewState(
            latitude=map_data['lat'].median(),
            longitude=map_data['lon'].median(),
            zoom=5,
            pitch=45 if mode_3d else 0,
            bearing=0
        )

        if mode_3d:
            layer = pdk.Layer(
                "ColumnLayer",
                data=map_data,
                get_position='[lon, lat]',
                get_elevation='weight',
                elevation_scale=200, 
                radius=3000,
                get_fill_color='[weight * 2, 100, 255, 180]',
                pickable=True,
                extruded=True,
            )
            st.info("💡 **Insights:** Taller towers indicate high-pressure enrollment zones.")
        else:
            layer = pdk.Layer(
                "HeatmapLayer",
                data=map_data,
                get_position='[lon, lat]',
                get_weight='weight',
                radius_pixels=30,
                intensity=1,
                threshold=0.05
            )

        # Render Map
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style='dark',
            tooltip={"text": "Enrollment Count: {weight}"} if mode_3d else None
        ), use_container_width=True) # Changed from width="stretch" for better stability

        # --- 4. INSIGHTS LEGEND (FIXED POSITION) ---
        st.divider() # Visual separation
        
        legend_col1, legend_col2 = st.columns(2)
        
        with legend_col1:
            if mode_3d:
                st.markdown("""
                ###  3D Tower Interpretation
                - **Height:** Represents the **Volume** of enrollments at that exact location.
                - **Color Peaks:** Brighter towers identify 'High-Pressure' zones or 'Super Centers'.
                - **Admin Action:** Identify where infrastructure is most stressed and requires support.
                - **Intensity :** Represents the concentration of operational centers in the area.
                """)
            else:
                st.markdown("""
                ###  Coverage Intelligence
                - **Glow Intensity:** Represents the concentration of operational centers in the area.
                - **Service Deserts:** Dark areas with no signal indicate gaps where citizens lack access.
                - **Admin Action:** Target these 'blind spots' for mobile van deployment.
                """)

        with legend_col2:
            st.markdown(f"""
            ###  View Analytics
            - **Max Volume at Point:** `{int(map_data['weight'].max()):,}`
            - **Median Activity:** `{int(map_data['weight'].median()):,}`
            - **Operational Signals:** `{len(map_data):,}` points
            """)
            st.caption(f"Currently filtering for: {age_label}")

    else:
        st.warning("⚠️ No valid geographic data found for this selection. Please adjust your filters.")    

    with tab_analytics:
        # --- Market Pulse Chart ---
        if 'date' in filtered_df.columns:
            st.subheader("📈 Enrolment Velocity & Trends")
        df_trend = filtered_df.groupby('date')[age_filter].sum().reset_index()
        df_trend['7D_MA'] = df_trend[age_filter].rolling(window=7).mean()
        
        fig_pulse = px.line(df_trend, x='date', y=[age_filter, '7D_MA'],
                           title=f"Daily Pulse: {age_label}",
                           labels={"value": "Enrolments", "variable": "Metric"},
                           color_discrete_map={age_filter: "#5c5c5c", "7D_MA": "#00FFCC"},
                           template="plotly_dark")
        fig_pulse.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_pulse, width="stretch")
    
    st.divider()
    
    # --- District Ranking Chart ---
    if 'district' in filtered_df.columns:
        st.subheader(f" Top 10 Districts: {age_label}")
        top_10 = filtered_df.groupby('district')[age_filter].sum().nlargest(10).reset_index()
        fig_rank = px.bar(top_10, x=age_filter, y='district', orientation='h',
                         color=age_filter, color_continuous_scale='Viridis',
                         template="plotly_dark")
        fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_rank, width="stretch")

with tab_raw_data:
    st.subheader(" Data Preview")
    st.dataframe(filtered_df.head(1000), width="stretch", hide_index=True)

# --- 6. DIAGNOSTICS ---
with st.expander(" System Diagnostics"):
    st.write(f"Total rows in view: {len(filtered_df)}")
    st.write(f"Active Filtering Column: {age_filter}")
    st.code(f"Selected State: {selected_state}")
