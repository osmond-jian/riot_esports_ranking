import pandas as pd

# Read the Parquet file into a DataFrame
df = pd.read_parquet('updated_df_for_modelling.parquet')

# Write the DataFrame to a CSV file
df.to_csv('updated_df_for_modelling.csv', index=False)
