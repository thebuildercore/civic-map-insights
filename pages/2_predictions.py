
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import datetime
from modules.data_processor import get_engine_data
from modules.prediction import predict_saturation_date, get_burn_trend

# 1. Page Setup
st.set_page_config(layout="wide", page_title="Predictive Forecasting")
st.title(" Saturation Forecasting Engine")
st.markdown("---")

# 2. Load Data from Shared Processor
df = get_engine_data()

if df.empty:
    st.error("❌ Data Engine Error: Could not load dataset.")
    st.stop()

# 3. Sidebar Configuration
st.sidebar.header(" Simulation Settings")

age_options = {
    "Infants (0-5)": "age_0_5", 
    "Youth (5-17)": "age_5_17", 
    "Adults (18+)": "age_18_greater"
}

target_label = st.sidebar.selectbox(
    "Demographic Group:", 
    list(age_options.keys()), 
    key="pred_age_select"
)
age_col = age_options[target_label]

# District Selection
districts = sorted(df['district'].unique())
selected_district = st.sidebar.selectbox("Target District:", districts)

# Filter Data for Model
district_df = df[df['district'] == selected_district].copy()

# 4. Scenario Simulation Input
current_enrolled = district_df[age_col].sum()
# AI Logic: Estimate a ceiling if user hasn't provided one (Assumption: 75% coverage achieved)
default_pop = int(current_enrolled * 1.3) 

st.sidebar.subheader(" Saturation Target")
target_pop = st.sidebar.number_input(
    "Estimated Total Population:", 
    min_value=int(current_enrolled), 
    value=int(default_pop),
    help="The total number of people in this age group living in the district."
)

st.sidebar.subheader(" 'What-If' Simulation")
boost = st.sidebar.slider(
    "Operational Efficiency Boost:", 
    0.5, 3.0, 1.0, 
    format="%.1fx Speed",
    help="Simulate adding more enrollment centers or staff."
)

# 5. Run Prediction Model
completion_date, velocity = predict_saturation_date(district_df, age_col, target_pop, boost_factor=boost)
# Calculate baseline (1.0x speed) to find the difference
original_date, _ = predict_saturation_date(district_df, age_col, target_pop, boost_factor=1.0)

# Calculate days saved
if isinstance(completion_date, datetime.date) and isinstance(original_date, datetime.date):
    days_saved = (original_date - completion_date).days
else:
    days_saved = 0

# --- 6. Display Executive Summary ---
st.subheader(f" Forecasting Report: {selected_district}")

# Calculate % of target reached
saturation_pc = (current_enrolled / target_pop) * 100 if target_pop > 0 else 0
to_go_pc = 100 - saturation_pc

# Create 4 clean columns for the dashboard
m1, m2, m3, m4 = st.columns(4)

# Column 1: Current State
m1.metric(
    label="Current Enrolled", 
    value=f"{int(current_enrolled):,}",
    help="Total enrollments found in the database for this district/age group."
)

# Column 2: Progress vs Goal
m2.metric(
    label="Saturation Level", 
    value=f"{saturation_pc:.1f}%", 
    delta=f"{to_go_pc:.1f}% Remaining",
    delta_color="inverse"  # Red if high percentage remaining
)

# Column 3: The Forecast Date
if isinstance(completion_date, (datetime.date, datetime.datetime)):
    m3.metric(
        label="Est. 100% Saturation", 
        value=completion_date.strftime('%d %b %Y'),
        help="The date this district will hit the target population based on current speed."
    )
else:
    m3.metric("Forecast Status", str(completion_date))

# Column 4: The Impact of the Boost
if 'days_saved' in locals() and days_saved > 0:
    m4.metric(
        label="⏳ Efficiency Gain", 
        value=f"{days_saved} Days Saved", 
        delta=f"Boost active: {boost}x",
        help="Number of days shaved off the timeline due to the operational boost."
    )
else:
    m4.metric(
        label="⏳ Efficiency Gain", 
        value="0 Days",
        help="Slide the 'Operational Efficiency Boost' in the sidebar to see time saved."
    )

# Additional context just below the metrics
st.caption(f"**Growth Velocity:** Analyzing trends at **{int(velocity)} enrollments per day**.")

# 7. Visualization: The Burn-Up Chart
st.divider()
trend = get_burn_trend(district_df, age_col)

if not trend.empty:
    trend['cumulative'] = trend[age_col].cumsum()

    fig = go.Figure()

    # Actual Progress
    fig.add_trace(go.Scatter(
        x=trend['date'], 
        y=trend['cumulative'], 
        mode='lines+markers', 
        name='Historical Growth', 
        line=dict(color='#00FFCC', width=3)
    ))

    # Target Horizontal Line
    fig.add_hline(
        y=target_pop, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Saturation Ceiling (100%)", 
        annotation_position="top left"
    )

    fig.update_layout(
        title=f"Saturation Trajectory: {target_label}",
        xaxis_title="Date Range",
        yaxis_title="Cumulative Enrolments",
        hovermode="x unified",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Insufficient historical data to generate a trend chart for this district.")

# 8. Model Interpretation (Caption)
with st.expander("📝 Technical Model Analysis"):
    st.write(f"""
    **Algorithm:** Ordinary Least Squares (OLS) Linear Regression.
    
    **How it works:** This engine calculates the 'Enrollment Velocity' by finding the line of best fit through your daily cumulative totals. 
    By extending this line (linear extrapolation) until it intersects with the **{target_pop:,}** population ceiling, we determine the completion date.
    
    **Boost Impact:** A boost factor of **{boost}x** increases the slope of the projection, simulating increased operational capacity.
    The Boost slider multiplies your enrollment velocity (speed), which steepens the slope of the trajectory line and pulls the predicted 100% saturation date closer to today.
    """)
