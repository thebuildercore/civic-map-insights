import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

def predict_traffic(df, days_to_predict=7):
    """
    Predicts future transaction volume based on past history.
    Returns: A dataframe containing future dates and predicted counts.
    """
    # 1. Prepare Data
    daily_counts = df.groupby('Date').size().reset_index(name='Counts')
    daily_counts['Date_Ordinal'] = daily_counts['Date'].map(datetime.datetime.toordinal)

    # 2. Train Model
    model = LinearRegression()
    X = daily_counts[['Date_Ordinal']]
    y = daily_counts['Counts']
    model.fit(X, y)

    # 3. Predict Future
    last_date = daily_counts['Date'].max()
    future_dates = [last_date + datetime.timedelta(days=x) for x in range(1, days_to_predict + 1)]
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    
    predictions = model.predict(future_ordinals)
    
    return pd.DataFrame({
        'Date': future_dates,
        'Predicted_Traffic': predictions.astype(int)
    })
