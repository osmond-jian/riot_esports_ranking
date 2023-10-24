import pandas as pd

# Load your Parquet file
df = pd.read_parquet('df_for_modelling.parquet')

#remove 'region' column
df = df.drop(columns=['region'])
print('Finished chopping off region')

#remove microseconds and timezone
df['date'] = df['date'].dt.floor('s')
df['date'] = df['date'].dt.tz_localize(None)
print('removed microseconds and timezones')

# Sort the dataframe by 'date' and 'team'
df_sorted = df.sort_values(by=['team', 'date'], ascending=[True, False])
print('sorted dataframe by date and team')

# Drop duplicate teams, keeping only the latest stats for each team
latest_stats = df_sorted.drop_duplicates(subset='team', keep='first')
print('dropping duplicate teams')

# Create all possible pairings of teams
from itertools import combinations

team_combinations = list(combinations(latest_stats['team'], 2))

# Create a dataset for each team pairing
datasets = []

print('we starting to cook')
for team1, team2 in team_combinations:
    team1_data = latest_stats[latest_stats['team'] == team1].copy()
    team2_data = latest_stats[latest_stats['team'] == team2].copy()
    
    # Rename columns for clarity
    team1_data.columns = [f"team1_{col}" if col not in ["team", "date"] else (f"team1_name" if col == "team" else f"team1_{col}") for col in team1_data.columns]
    team2_data.columns = [f"team2_{col}" if col not in ["team", "date"] else (f"team2_name" if col == "team" else f"team2_{col}") for col in team2_data.columns]

    # Now concatenate as before
    combined_data = pd.concat([team1_data.reset_index(drop=True), team2_data.reset_index(drop=True)], axis=1)
    datasets.append(combined_data)

# Concatenate all datasets to form the final dataset for scoring
final_dataset = pd.concat(datasets, axis=0).reset_index(drop=True)

# final_dataset.head()

#delete and print duplicate columns
dup_cols = final_dataset.columns[final_dataset.columns.duplicated()].tolist()
print(dup_cols)

final_dataset = final_dataset.loc[:,~final_dataset.columns.duplicated()]



# Save the updated DataFrame as Parquet 
final_dataset.to_parquet('updated_df_for_modelling.parquet', index=False)

