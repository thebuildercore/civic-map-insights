# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import datetime

# def predict_traffic(df, days_to_predict=7):
#     """
#     Predicts future transaction volume based on past history.
#     Returns: A dataframe containing future dates and predicted counts.
#     """
#     # 1. Prepare Data
#     daily_counts = df.groupby('Date').size().reset_index(name='Counts')
#     daily_counts['Date_Ordinal'] = daily_counts['Date'].map(datetime.datetime.toordinal)

#     # 2. Train Model
#     model = LinearRegression()
#     X = daily_counts[['Date_Ordinal']]
#     y = daily_counts['Counts']
#     model.fit(X, y)

#     # 3. Predict Future
#     last_date = daily_counts['Date'].max()
#     future_dates = [last_date + datetime.timedelta(days=x) for x in range(1, days_to_predict + 1)]
#     future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    
#     predictions = model.predict(future_ordinals)
    
#     return pd.DataFrame({
#         'Date': future_dates,
#         'Predicted_Traffic': predictions.astype(int)
#     })

# Version 3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

def predict_traffic(df, days_to_predict=7):
    """
    Predicts future daily transaction volume based on past history.
    Useful for anticipating server load or staffing needs.
    """
    # Safety Check
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    # 1. Prepare Data
    # Ensure date is datetime type
    df['date'] = pd.to_datetime(df['date'])
    daily_counts = df.groupby('date').size().reset_index(name='Counts')
    
    # Create Ordinal Dates for Regression (Math friendly)
    daily_counts['Date_Ordinal'] = daily_counts['date'].map(datetime.datetime.toordinal)

    # 2. Train Model
    model = LinearRegression()
    X = daily_counts[['Date_Ordinal']]
    y = daily_counts['Counts']
    model.fit(X, y)

    # 3. Predict Future
    last_date = daily_counts['date'].max()
    future_dates = [last_date + datetime.timedelta(days=x) for x in range(1, days_to_predict + 1)]
    
    # Convert future dates to ordinals for the model
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    
    predictions = model.predict(future_ordinals)
    
    return pd.DataFrame({
        'Date': future_dates,
        'Predicted_Traffic': predictions.astype(int)
    })

def predict_saturation_date(df, age_col, target_population, boost_factor=1.0):
    """
    Predicts the exact date a district will hit 100% saturation.
    boost_factor: Multiplier for 'What-If' scenarios (e.g., 1.5x speed).
    """
    if df.empty or 'date' not in df.columns:
        return None, 0

    # 1. Prepare Time-Series Data
    # Group by date to get daily progress
    daily = df.groupby('date')[age_col].sum().reset_index()
    # Calculate Cumulative Sum (The "Burn-Up" Curve)
    daily['cumulative'] = daily[age_col].cumsum()
    
    # Convert dates to "Day Numbers" starting from 0 for Linear Regression
    daily['day_num'] = (daily['date'] - daily['date'].min()).dt.days
    
    # 2. Train Model
    X = daily[['day_num']]
    y = daily['cumulative']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 3. Calculate Velocity (Slope of the line)
    base_velocity = model.coef_[0] # Enrollments per day
    adjusted_velocity = base_velocity * boost_factor
    
    if adjusted_velocity <= 0:
        return "Stalled", 0
    
    # 4. Predict Future Intersection
    current_total = daily['cumulative'].max()
    remaining = target_population - current_total
    
    if remaining <= 0:
        return "Already Saturated", adjusted_velocity
        
    days_needed = remaining / adjusted_velocity
    last_date = daily['date'].max()
    
    # Add the predicted days to the last known date
    completion_date = last_date + datetime.timedelta(days=int(days_needed))
    
    return completion_date.date(), adjusted_velocity

def get_burn_trend(df, age_col):
    """
    Returns the daily trend for visualization (Burn-Up Chart).
    Aggregates data so the UI can just plot it.
    """
    if df.empty or age_col not in df.columns:
        return pd.DataFrame()
        
    trend = df.groupby('date')[age_col].sum().reset_index()
    return trend
