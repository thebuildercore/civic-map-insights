import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
from modules.data_loader import load_dataset
from modules.map_utils import create_base_map, add_state_boundaries, add_signals

# --- 1. SET PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="UIDAI Demographic Analytics")

# --- 2. LOAD DATA ---
@st.cache_data
def get_data():
    return load_dataset() 

df = get_data()

# --- 3. SIDEBAR FILTERS ---
# st.sidebar.title("🇮🇳 UIDAI Filters")
# all_states = ["All India"] + sorted(df['state'].unique().tolist())
# selected_state = st.sidebar.selectbox("Select Target State", all_states)

# age_options = {
#     "Ages 0-5": "age_0_5",
#     "Ages 5-17": "age_5_17",
#     "Ages 18+": "age_18_greater"
# }
# age_label = st.sidebar.selectbox("Show Signal Concentration for:", list(age_options.keys()))
# age_filter = age_options[age_label]

# --- 3. SIDEBAR FILTERS ---
st.sidebar.title("🇮🇳 UIDAI Control Center")

# Filter 1: Age Group Selection ( DEFINES age_filter)
age_options = {
    "Infants (0-5)": "age_0_5",
    "Youth (5-17)": "age_5_17",
    "Adults (18+)": "age_18_greater"
}
age_label = st.sidebar.selectbox("Target Age Group:", list(age_options.keys()))
age_filter = age_options[age_label] # Variables are now defined!

# Filter 2: State Selection
all_states = ["All India"] + sorted(df['state'].unique().tolist())
selected_state = st.sidebar.selectbox("Select State:", all_states)

# Filter 3: Date Range (The Timeline)
if 'date' in df.columns:
   
    df['date'] = pd.to_datetime(df['date'])
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    # Date slider
    date_range = st.sidebar.date_input(
        "Select Timeline:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Handle the "Funnel" Filtering
    # 1. Start with everything
    filtered_df = df.copy()

    # 2. Apply Date Filter (check if user selected a range)
    if isinstance(date_range, list) or isinstance(date_range, tuple):
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= start_date) & 
                (filtered_df['date'].dt.date <= end_date)
            ]

    # 3. Apply State Filter
    if selected_state != "All India":
        filtered_df = filtered_df[filtered_df['state'] == selected_state]

# --- 4. ERROR PREVENTION CHECK ---
if filtered_df.empty:
    st.error("No data found for this date range or state. Please adjust filters.")
    st.stop() # Stops the app from running map code on empty data

# --- 4. DATA FILTERING & CENTER LOGIC ---
if selected_state == "All India":
    filtered_df = df
    map_center = [22.0, 78.0]
    map_zoom = 5
else:
    filtered_df = df[df['state'] == selected_state]
    if 'lat' in filtered_df.columns and not filtered_df['lat'].isnull().all():
        map_center = [filtered_df['lat'].mean(), filtered_df['lon'].mean()]
    else:
        centers = {"Karnataka": [15.3, 75.7], "Meghalaya": [25.5, 91.3], "Bihar": [25.1, 85.3]}
        map_center = centers.get(selected_state, [22.0, 78.0])
    map_zoom = 7

# --- 5. TOP METRICS ---
st.title(f"📊 UIDAI Analytics: {selected_state}")

total_kids = filtered_df['age_0_5'].sum()
total_teens = filtered_df['age_5_17'].sum()
total_adults = filtered_df['age_18_greater'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Total Infants (0-5)", f"{total_kids:,}")
m2.metric("Total Youth (5-17)", f"{total_teens:,}")
m3.metric("Total Adults (18+)", f"{total_adults:,}")

st.divider()

# --- 6. NAVIGATION TABS ---

tab_map, tab_analytics, tab_raw_data = st.tabs(["🌍 Geospatial Map", "📈 Advanced Insights", "📑 Detailed Records"])

with tab_map:
    st.subheader(f"📍 Location Signals for {age_label}")
    m = create_base_map(map_center, map_zoom)
    add_state_boundaries(m, selected_state)
    add_signals(m, filtered_df, age_filter)
    st_folium(m, width="100%", height=550, key="uidai_map")

with tab_analytics:
    st.header(f"Statistical Breakdown: {selected_state}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ranking Districts
        st.subheader(f"Top 10 Districts ({age_label})")
        top_10 = filtered_df.nlargest(10, age_filter)
        fig_rank = px.bar(
            top_10, 
            x=age_filter, 
            y='district', 
            orientation='h',
            color=age_filter,
            color_continuous_scale='Viridis',
            labels={age_filter: 'Registrations', 'district': 'District'}
        )
        fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_rank, use_container_width=True)

    with col2:
        # Age Group Proportions
        st.subheader("Age Group Composition")
        pie_data = pd.DataFrame({
            'Category': ['0-5', '5-17', '18+'],
            'Total': [total_kids, total_teens, total_adults]
        })
        fig_pie = px.pie(
            pie_data, 
            values='Total', 
            names='Category', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Hierarchical View
    st.divider()
    st.subheader("District Hierarchy Treemap")
    fig_tree = px.treemap(
        filtered_df, 
        path=['state', 'district'], 
        values=age_filter,
        color=age_filter,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_tree, use_container_width=True)

with tab_raw_data:
    st.subheader(f"Data Explorer: {selected_state}")
    display_cols = ['state', 'district', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater']
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
    
    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv,
        file_name=f"uidai_{selected_state.lower().replace(' ', '_')}.csv",
        mime='text/csv',
    )
