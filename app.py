# # import streamlit as st
# # import pandas as pd
# # import plotly.express as px
# # from streamlit_folium import st_folium
# # from modules.data_loader import load_dataset
# # from modules.map_utils import create_base_map, add_state_boundaries, add_signals

# # # --- 1. SET PAGE CONFIG ---
# # st.set_page_config(layout="wide", page_title="UIDAI Demographic Analytics")

# # # --- 2. LOAD DATA ---
# # @st.cache_data
# # def get_data():
# #     return load_dataset() 

# # df = get_data()

# # # --- 3. SIDEBAR FILTERS ---
# # # st.sidebar.title("🇮🇳 UIDAI Filters")
# # # all_states = ["All India"] + sorted(df['state'].unique().tolist())
# # # selected_state = st.sidebar.selectbox("Select Target State", all_states)

# # # age_options = {
# # #     "Ages 0-5": "age_0_5",
# # #     "Ages 5-17": "age_5_17",
# # #     "Ages 18+": "age_18_greater"
# # # }
# # # age_label = st.sidebar.selectbox("Show Signal Concentration for:", list(age_options.keys()))
# # # age_filter = age_options[age_label]

# # # --- 3. SIDEBAR FILTERS ---
# # st.sidebar.title("🇮🇳 UIDAI Control Center")

# # # Filter 1: Age Group Selection ( DEFINES age_filter)
# # age_options = {
# #     "Infants (0-5)": "age_0_5",
# #     "Youth (5-17)": "age_5_17",
# #     "Adults (18+)": "age_18_greater"
# # }
# # age_label = st.sidebar.selectbox("Target Age Group:", list(age_options.keys()))
# # age_filter = age_options[age_label] # Variables are now defined!

# # # Filter 2: State Selection
# # all_states = ["All India"] + sorted(df['state'].unique().tolist())
# # selected_state = st.sidebar.selectbox("Select State:", all_states)

# # # Filter 3: Date Range (The Timeline)
# # if 'date' in df.columns:
   
# #     df['date'] = pd.to_datetime(df['date'])
# #     min_date = df['date'].min().date()
# #     max_date = df['date'].max().date()
    
# #     # Date slider
# #     date_range = st.sidebar.date_input(
# #         "Select Timeline:",
# #         value=[min_date, max_date],
# #         min_value=min_date,
# #         max_value=max_date
# #     )
    
# #     # Handle the "Funnel" Filtering
# #     # 1. Start with everything
# #     filtered_df = df.copy()

# #     # 2. Apply Date Filter (check if user selected a range)
# #     if isinstance(date_range, list) or isinstance(date_range, tuple):
# #         if len(date_range) == 2:
# #             start_date, end_date = date_range
# #             filtered_df = filtered_df[
# #                 (filtered_df['date'].dt.date >= start_date) & 
# #                 (filtered_df['date'].dt.date <= end_date)
# #             ]

# #     # 3. Apply State Filter
# #     if selected_state != "All India":
# #         filtered_df = filtered_df[filtered_df['state'] == selected_state]

# # # --- 4. ERROR PREVENTION CHECK ---
# # if filtered_df.empty:
# #     st.error("No data found for this date range or state. Please adjust filters.")
# #     st.stop() # Stops the app from running map code on empty data

# # # --- 4. DATA FILTERING & CENTER LOGIC ---
# # if selected_state == "All India":
# #     filtered_df = df
# #     map_center = [22.0, 78.0]
# #     map_zoom = 5
# # else:
# #     filtered_df = df[df['state'] == selected_state]
# #     if 'lat' in filtered_df.columns and not filtered_df['lat'].isnull().all():
# #         map_center = [filtered_df['lat'].mean(), filtered_df['lon'].mean()]
# #     else:
# #         centers = {"Karnataka": [15.3, 75.7], "Meghalaya": [25.5, 91.3], "Bihar": [25.1, 85.3]}
# #         map_center = centers.get(selected_state, [22.0, 78.0])
# #     map_zoom = 7

# # # --- 5. TOP METRICS ---
# # st.title(f"📊 UIDAI Analytics: {selected_state}")

# # total_kids = filtered_df['age_0_5'].sum()
# # total_teens = filtered_df['age_5_17'].sum()
# # total_adults = filtered_df['age_18_greater'].sum()

# # m1, m2, m3 = st.columns(3)
# # m1.metric("Total Infants (0-5)", f"{total_kids:,}")
# # m2.metric("Total Youth (5-17)", f"{total_teens:,}")
# # m3.metric("Total Adults (18+)", f"{total_adults:,}")

# # st.divider()

# # # --- 6. NAVIGATION TABS ---

# # tab_map, tab_analytics, tab_raw_data = st.tabs(["🌍 Geospatial Map", "📈 Advanced Insights", "📑 Detailed Records"])

# # with tab_map:
# #     st.subheader(f"📍 Location Signals for {age_label}")
# #     m = create_base_map(map_center, map_zoom)
# #     add_state_boundaries(m, selected_state)
# #     add_signals(m, filtered_df, age_filter)
# #     st_folium(m, width="100%", height=550, key="uidai_map")

# # with tab_analytics:
# #     st.header(f"Statistical Breakdown: {selected_state}")
    
# #     col1, col2 = st.columns(2)
    
# #     with col1:
# #         # Ranking Districts
# #         st.subheader(f"Top 10 Districts ({age_label})")
# #         top_10 = filtered_df.nlargest(10, age_filter)
# #         fig_rank = px.bar(
# #             top_10, 
# #             x=age_filter, 
# #             y='district', 
# #             orientation='h',
# #             color=age_filter,
# #             color_continuous_scale='Viridis',
# #             labels={age_filter: 'Registrations', 'district': 'District'}
# #         )
# #         fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
# #         st.plotly_chart(fig_rank, use_container_width=True)

# #     with col2:
# #         # Age Group Proportions
# #         st.subheader("Age Group Composition")
# #         pie_data = pd.DataFrame({
# #             'Category': ['0-5', '5-17', '18+'],
# #             'Total': [total_kids, total_teens, total_adults]
# #         })
# #         fig_pie = px.pie(
# #             pie_data, 
# #             values='Total', 
# #             names='Category', 
# #             hole=0.4,
# #             color_discrete_sequence=px.colors.qualitative.Pastel
# #         )
# #         st.plotly_chart(fig_pie, use_container_width=True)

# #     # Hierarchical View
# #     st.divider()
# #     st.subheader("District Hierarchy Treemap")
# #     fig_tree = px.treemap(
# #         filtered_df, 
# #         path=['state', 'district'], 
# #         values=age_filter,
# #         color=age_filter,
# #         color_continuous_scale='Blues'
# #     )
# #     st.plotly_chart(fig_tree, use_container_width=True)

# # with tab_raw_data:
# #     st.subheader(f"Data Explorer: {selected_state}")
# #     display_cols = ['state', 'district', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater']
# #     st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
    
# #     # Download Button
# #     csv = filtered_df.to_csv(index=False).encode('utf-8')
# #     st.download_button(
# #         label="📥 Download Filtered CSV",
# #         data=csv,
# #         file_name=f"uidai_{selected_state.lower().replace(' ', '_')}.csv",
# #         mime='text/csv',
# #     )


# # Version 2 


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import re
# import os
# from streamlit_folium import st_folium
# from modules.data_loader import load_dataset
# from modules.map_utils import create_base_map, add_signals

# # --- 1. PAGE CONFIG ---
# st.set_page_config(layout="wide", page_title="UIDAI 2026 Analytics Control Center")

# # # 2. IMMEDIATE TITLE (Fixes LCP: The title shows BEFORE data loads)
# # main_title = st.empty()
# # main_title.title("📊 UIDAI Analytics: Loading...")

# # # 3. RESERVE SPACE FOR METRICS (Fixes CLS)
# # metric_placeholder = st.empty()
# # with metric_placeholder.container():
# #     m1, m2, m3 = st.columns(3)
# #     # Put "ghost" values so the page doesn't jump later
# #     m1.metric("Total Infants", "Loading...")
# #     m2.metric("Total Youth", "Loading...")
# #     m3.metric("Total Adults", "Loading...")

# # Custom CSS for UI Stability
# st.markdown("""
#     <style>
#     .main > div { padding-top: 2rem; }
#     div[data-testid="stExpander"] { border: none; }
#     footer {visibility: hidden;}
#     </style>
# """, unsafe_allow_html=True)

# # --- 2. DATA UTILITIES ---
# def clean_coordinate(coord):
#     if pd.isna(coord) or coord == "": return 0.0
#     if isinstance(coord, (int, float)): return float(coord)
#     numeric_part = re.search(r"[-+]?\d*\.\d+|\d+", str(coord))
#     if not numeric_part: return 0.0
#     val = float(numeric_part.group())
#     if any(char in str(coord).upper() for char in ['S', 'W']): val = -val
#     return val

# @st.cache_data(ttl=3600)
# def get_cleaned_data():
#     df = load_dataset()
#     if df is None or df.empty:
#         return pd.DataFrame()
        
#     # Standardize column names
#     df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
#     # 1. Force Date Type
#     if 'date' in df.columns:
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
#     # 2. Fix Lat/Lon (REMOVED the premature return bug)
#     if 'lat' in df.columns: 
#         df['lat'] = df['lat'].apply(clean_coordinate)
#     if 'lon' in df.columns: 
#         df['lon'] = df['lon'].apply(clean_coordinate)
    
#     # 3. Filter Ocean/Invalid coordinates
#     if 'lat' in df.columns and 'lon' in df.columns:
#         df = df[(df['lat'] != 0.0) & (df['lon'] != 0.0)]
        
#     return df

# # --- 3. LOADING & INITIAL SIDEBAR ---
# df = get_cleaned_data()

# if df.empty:
#     st.error("❌ Data Engine Error: Could not load 'uidai_data.parquet'. Please check your project root.")
#     st.stop()

# st.sidebar.title("🇮🇳 UIDAI Control Center")
# st.sidebar.info("Data Engine: Apache Parquet v3.0")

# # Filters
# age_options = {"Infants (0-5)": "age_0_5", "Youth (5-17)": "age_5_17", "Adults (18+)": "age_18_greater"}
# age_label = st.sidebar.selectbox("Target Age Group:", list(age_options.keys()))
# age_filter = age_options[age_label]

# all_states = ["All India"] + sorted(df['state'].unique().tolist())
# selected_state = st.sidebar.selectbox("Select State:", all_states)

# # Timeline Logic
# filtered_df = df.copy()
# if 'date' in df.columns:
#     min_date = df['date'].min().date()
#     max_date = df['date'].max().date()
#     # Handle date_input carefully to prevent crashes during selection
#     date_range = st.sidebar.date_input("Timeline:", [min_date, max_date])
#     if isinstance(date_range, list) and len(date_range) == 2:
#         start_date, end_date = date_range
#         filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & 
#                                   (filtered_df['date'].dt.date <= end_date)]

# if selected_state != "All India":
#     filtered_df = filtered_df[filtered_df['state'] == selected_state]

# # --- 4. TOP METRICS ---
# st.title(f"📊 UIDAI Analytics: {selected_state}")
# m1, m2, m3 = st.columns(3)
# m1.metric("Total Infants", f"{filtered_df['age_0_5'].sum():,}")
# m2.metric("Total Youth", f"{filtered_df['age_5_17'].sum():,}")
# m3.metric("Total Adults", f"{filtered_df['age_18_greater'].sum():,}")

# st.divider()

# # --- 5. NAVIGATION TABS (Single definition to prevent duplicates) ---
# tab_map, tab_analytics, tab_raw_data = st.tabs(["🌍 Geospatial Map", "📈 Market Pulse", "📑 Detailed Records"])

# with tab_map:
#     st.subheader(f"📍 Location Signals: {age_label}")
#     if 'lat' in filtered_df.columns and 'lon' in filtered_df.columns:
#         map_df = filtered_df.dropna(subset=['lat', 'lon', age_filter])
#         if not map_df.empty:
#             # Aggregate for map signals
#             map_agg = map_df.groupby(['lat', 'lon'])[age_filter].sum().reset_index()
#             map_center = [map_agg['lat'].mean(), map_agg['lon'].mean()]
            
#             # Use your custom map modules
#             m = create_base_map(map_center, 6)
#             add_signals(m, map_agg, age_filter)
#             st_folium(m, width="100%", height=550, key="uidai_map")
#         else:
#             st.warning("No coordinate matches found for this filter.")
#     else:
#         st.error("Coordinate mapping unavailable.")

# with tab_analytics:
#     # --- Market Pulse Chart ---
#     if 'date' in filtered_df.columns:
#         st.subheader("📈 Enrolment Velocity & Trends")
#         df_trend = filtered_df.groupby('date')[age_filter].sum().reset_index()
#         df_trend['7D_MA'] = df_trend[age_filter].rolling(window=7).mean()
        
#         fig_pulse = px.line(df_trend, x='date', y=[age_filter, '7D_MA'],
#                            title=f"Daily Pulse: {age_label}",
#                            labels={"value": "Enrolments", "variable": "Metric"},
#                            color_discrete_map={age_filter: "#A0A0A0", "7D_MA": "#00FFCC"})
#         fig_pulse.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02))
#         st.plotly_chart(fig_pulse, use_container_width=True)
    
#     st.divider()
    
#     # --- District Ranking Chart ---
#     if 'district' in filtered_df.columns:
#         st.subheader(f"🏆 Top 10 Districts: {age_label}")
#         top_10 = filtered_df.groupby('district')[age_filter].sum().nlargest(10).reset_index()
#         fig_rank = px.bar(top_10, x=age_filter, y='district', orientation='h',
#                           color=age_filter, color_continuous_scale='Viridis')
#         fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
#         st.plotly_chart(fig_rank, use_container_width=True)

# with tab_raw_data:
#     st.subheader("📑 Data Preview")
#     st.dataframe(filtered_df.head(1000), use_container_width=True, hide_index=True)

# # Final Debug info (Optional - can be commented out)
# with st.expander("🔍 System Diagnostics"):
#     st.write(f"Rows processed: {len(filtered_df)}")
#     st.write(f"Active Columns: {filtered_df.columns.tolist()}")

# Version 3
import streamlit as st

pg = st.navigation([
    st.Page("main_dashboard.py", title="Analytics Overview", icon="📊", default=True),
    st.Page("pages/1_intelligence.py", title="Audit & Anomalies", icon="🕵️"),
    st.Page("pages/2_predictions.py", title="Saturation Forecast", icon="🔮"),
])

pg.run()
