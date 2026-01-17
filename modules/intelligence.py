
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import STL

def detect_anomalies(df, age_col, contamination=0.05):
    """
    ML ENGINE: Isolation Forest
    Finds 'Structural Outliers' by identifying Pincodes with 
    mathematically unique enrollment patterns.
    """
    if df.empty: return pd.DataFrame()
    
    profile = df.groupby('pincode')[[age_col]].sum().reset_index()
    model = IsolationForest(contamination=contamination, random_state=42)
    
    profile['anomaly_score'] = model.fit_predict(profile[[age_col]])
    profile['risk_factor'] = model.decision_function(profile[[age_col]])
    
    return profile[profile['anomaly_score'] == -1].sort_values(by=age_col, ascending=False)

def z_score_audit(df, age_col):
    """
    STATISTICAL ENGINE: 3-Sigma Rule
    Identifies 'Intensity Outliers'—Pincodes performing beyond 
    99.7% of the regional average.
    """
    stats = df.groupby('pincode')[age_col].sum().reset_index()
    mean_val, std_val = stats[age_col].mean(), stats[age_col].std()
    
    if std_val == 0 or pd.isna(std_val): return pd.DataFrame()
    
    stats['z_score'] = (stats[age_col] - mean_val) / std_val
    return stats[stats['z_score'] > 3].sort_values(by='z_score', ascending=False)

def get_rolling_anomalies(df, age_col, window=14):
    """
    EARLY WARNING SYSTEM: Rolling Baseline
    Compares a Pincode's performance today against its own 
    average over the last 14 days to catch sudden spikes.
    """
    if df.empty: return pd.DataFrame()
    
    # Sort for time-series consistency
    df_sorted = df.sort_values(['pincode', 'date'])
    
    # Calculate adaptive baseline
    group = df_sorted.groupby('pincode')[age_col]
    df_sorted['rolling_avg'] = group.transform(lambda x: x.rolling(window=window, min_periods=1).mean())
    df_sorted['rolling_std'] = group.transform(lambda x: x.rolling(window=window, min_periods=1).std())
    
    # Adaptive Z-Score (Today vs Recent History)
    df_sorted['rolling_z'] = (df_sorted[age_col] - df_sorted['rolling_avg']) / (df_sorted['rolling_std'] + 1e-6)
    
    # Return only the most recent significant spikes
    return df_sorted[df_sorted['rolling_z'] > 3].sort_values(by='date', ascending=False)

def decompose_signals(df, age_col):
    """
    SIGNAL FILTER: STL Decomposition
    Extracts 'Residuals' (Unexplained Noise) by stripping away 
    Trend and Weekly Seasonality (e.g., Friday rushes).
    """
    # Aggregate to system-wide daily totals
    daily = df.groupby('date')[age_col].sum().asfreq('D').fillna(0)
    
    if len(daily) < 14: # Requirement for Seasonal decomposition
        return None
        
    # period=7 captures the weekly "heartbeat" of the centers
    return STL(daily, period=7).fit()
