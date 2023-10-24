import pandas as pd

# Load the CSV file
data = pd.read_csv('added_features_part2.csv')

# Shared columns
shared_columns = ['startDate', 'game_id', 'match_id', 'tournament_id', 'tournament_name', 'final_game_time']

# Dynamically generate column mappings for team100 and team200
team100_columns = {col: col.replace('_team1', '').replace('team1_', '') for col in data.columns if 'team1' in col}
team200_columns = {col: col.replace('_team2', '').replace('team2_', '') for col in data.columns if 'team2' in col}

team100_data = data.rename(columns=team100_columns)[shared_columns + list(team100_columns.values())]
team200_data = data.rename(columns=team200_columns)[shared_columns + list(team200_columns.values())]

# Add the team names from `team100` and `team200` columns to both subsets
team100_data['team'] = data['team_100']
team200_data['team'] = data['team_200']

# Combine the two datasets
combined_data = pd.concat([team100_data, team200_data], ignore_index=True)

# Save to a new CSV file
combined_data.to_csv('added_features_team_merge.csv', index=False)





