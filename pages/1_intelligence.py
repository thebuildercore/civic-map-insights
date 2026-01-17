
import streamlit as st
import plotly.express as px
from modules.data_processor import get_engine_data
# Added new function imports here
from modules.intelligence import (
    detect_anomalies, 
    z_score_audit, 
    get_rolling_anomalies, 
    decompose_signals
)

st.set_page_config(layout="wide")
st.title("🕵️ Operational Intelligence & Audit")

df = get_engine_data()

# 1. Sidebar Controls
st.sidebar.header("Audit Configuration")
age_options = {"Infants (0-5)": "age_0_5", "Youth (5-17)": "age_5_17", "Adults (18+)": "age_18_greater"}
target_label = st.sidebar.selectbox("Audit Demographic:", list(age_options.keys()), key="intel_age")
age_col = age_options[target_label]
sensitivity = st.sidebar.slider("AI Sensitivity (Contamination):", 0.01, 0.10, 0.05)

# 2. Run Engines (The 4-Layer Audit)
anomalies = detect_anomalies(df, age_col, contamination=sensitivity)
z_outliers = z_score_audit(df, age_col)
rolling_spikes = get_rolling_anomalies(df, age_col)
stl_result = decompose_signals(df, age_col)

# 3. EXECUTIVE SUMMARY
st.subheader(" Critical Operational Alerts")
top_3 = anomalies.head(3)
if not top_3.empty:
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.error(f"**Pincode {int(row['pincode'])}**")
            st.metric("Total Volume", f"{int(row[age_col]):,}")
            st.caption("AI Priority: High Risk (Isolated Pattern)")
else:
    st.success("✅ No critical anomalies detected.")

st.divider()

# 4. VISUAL REPORT: Risk Matrix & Noise
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(" Risk Intensity Matrix")
    plot_df = anomalies.merge(z_outliers[['pincode', 'z_score']], on='pincode', how='left').fillna(0)
    fig = px.scatter(
        plot_df, x=age_col, y="z_score", size=age_col, color="z_score",
        hover_name="pincode", color_continuous_scale="Reds", template="plotly_dark"
    )
    st.plotly_chart(fig, width="stretch") # Updated to 2026 standard

with col_right:
    st.subheader(" System-Wide Noise")
    
    # 1. Check if the STL engine successfully ran
    if stl_result is not None:
        # 2. Extract and clean the residual (noise) data
        resid_data = stl_result.resid.dropna()
        
        # 3. Check if we actually have numbers to plot
        if not resid_data.empty:
            st.line_chart(resid_data, width="stretch")
            st.caption(" These peaks represent 'Unexplained Surges' that don't follow normal weekly rhythms.")
        else:
            st.info("The noise signal is perfectly flat (no deviation detected).")
    
    # 4. Handle cases with low historical data
    else:
        st.info("Insufficient historical data for Noise Decomposition.")
        st.caption("Note: We need at least 14 days of data to isolate seasonal patterns from noise.")

# 5. NEW: Early Warning System (Rolling Baseline)
with st.expander(" Sudden Activity Spikes (Last 14 Days)"):
    if not rolling_spikes.empty:
        st.warning(f"Detected {len(rolling_spikes)} Pincodes with sudden intensity shifts.")
        st.dataframe(rolling_spikes[['date', 'pincode', age_col, 'rolling_z']].head(10), width="stretch")
    else:
        st.write("No sudden spikes detected relative to local history.")

# 6. DETAILED DATA TABLE
with st.expander(f" View Full Audit Log ({len(z_outliers)} Flagged Pincodes)"):
    detailed_report = anomalies.merge(z_outliers[['pincode', 'z_score']], on='pincode', how='left')
    detailed_report = detailed_report.rename(columns={age_col: "Total Enrollments", "z_score": "Intensity (Sigma)", "pincode": "Pincode"})
    
    st.dataframe(
        detailed_report[["Pincode", "Total Enrollments", "Intensity (Sigma)"]].sort_values("Intensity (Sigma)", ascending=False),
        width="stretch", # Updated to 2026 standard
        hide_index=True
    )
