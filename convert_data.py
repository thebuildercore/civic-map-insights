
import pandas as pd
import os

input_csv = "data/datasets-uidai.csv" 
output_parquet = "uidai_data.parquet"

# Based on your example: 20-03-2025,Assam,Marigaon,782104,20,58,10
# These are 7 columns. We MUST name all 7.
col_names = ['date', 'state', 'district', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater']

print("🔄 Forcing column names onto CSV...")

# header=0 assumes your CSV has a title row. 
# If your CSV starts directly with data, change header=0 to header=None
df = pd.read_csv(input_csv, names=col_names, header=0) 

# Force Date format so the Trend Chart works
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

# Clean up text
df['state'] = df['state'].astype(str).str.strip()
df['district'] = df['district'].astype(str).str.strip()

# Save it
df.to_parquet(output_parquet, engine='pyarrow')

print("✅ DONE! New Column List:", df.columns.tolist())
print("Check: Does the list above include 'date' and 'district' now?")
