import pandas as pd 

def feature_averages(data:pd.DataFrame, cols_avg:list,
                     date_order:str, num_rolling:int,team_id:str)->pd.DataFrame:
    """This function will take in a list of column names and take the rolling average of each of those columns.
    The rolling average will be based on num_rolling and the data will be ordered chronologically.  We want
    the average stats for each team so the rolling games will require the team_id column name to keep track.
    It should return a new dataframe that has the original columns in the data - cols_avg and instead return the
    rolling average columns as the original col name with _avg as the suffix

    Args:
        data (pd.DataFrame): _description_
        cols_avg (list): _description_
        date_order (str): _description_
        num_rolling (int): _description_
        team_id (str): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # Sort the dataframe by team and date
    data_sorted = data.sort_values(by=[team_id, date_order])
    
    # Group by team and compute rolling averages for specified columns
    rolling_avg_df = data_sorted.groupby(team_id)[cols_avg].rolling(window=num_rolling, min_periods=1).mean().round(2).reset_index()
    rolling_avg_df = rolling_avg_df.drop(columns=team_id)  # Drop the team column as it's duplicated
    
    # Rename columns to add the _avg_{n} suffix
    rolling_avg_df = rolling_avg_df.rename(columns={col: f"{col}_avg_{num_rolling}" for col in cols_avg})
    
    # Merge the rolling average dataframe with the original dataframe
    merged_df = pd.concat([data_sorted.reset_index(drop=True), rolling_avg_df], axis=1)
    
    # Drop the original columns that we averaged
    merged_df = merged_df.drop(columns=cols_avg)

    return merged_df

def compute_win_streak(series):
    """Compute the win streak for a given series of wins/losses."""
    streak = 0
    streak_list = []
    for value in series:
        if value == 1:
            streak += 1
        else:
            streak = 0
        streak_list.append(streak)
    return streak_list

def compute_win_stats(df,n):
    # Sort the dataframe by team and game_id
    df_sorted = df.sort_values(by=['team', 'game_id'])

    # Calculate win streak for each team
    df_sorted['win_streak_game'] = df_sorted.groupby('team')['result'].transform(compute_win_streak)

    # Convert the 'result' column to numeric values: 1 for 'win' and 0 for 'loss'
    df_sorted['result'] = df_sorted['result'].apply(lambda x: 1 if x == 'win' else 0)

    # Recompute the cumulative win rate for each team
    df_sorted['cumulative_win_rate_game'] = (df_sorted.groupby('team')['result'].transform('cumsum') / 
                                            (df_sorted.groupby('team').cumcount() + 1)).fillna(0)
    
    # Compute the cumulative win rate for each team when playing on the Red side
    df_sorted['cumulative_win_rate_red'] = (df_sorted[df_sorted['side'] == 'red'].groupby('team')['result'].transform('cumsum') / 
                                            (df_sorted[df_sorted['side'] == 'red'].groupby('team').cumcount() + 1)).fillna(0)

    # Compute the cumulative win rate for each team when playing on the Blue side
    df_sorted['cumulative_win_rate_blue'] = (df_sorted[df_sorted['side'] == 'blue'].groupby('team')['result'].transform('cumsum') / 
                                            (df_sorted[df_sorted['side'] == 'blue'].groupby('team').cumcount() + 1)).fillna(0)
    
    # Compute the cumulative sum of game time for wins and the count of wins, then divide to get the average game time for wins
    df_sorted['cumulative_game_time_wins'] = (df_sorted[df_sorted['result'] == 1].groupby('team')['game_time'].transform('cumsum') / 
                                            df_sorted[df_sorted['result'] == 1].groupby('team')['result'].transform('cumsum')).fillna(0)

    # Compute the cumulative sum of game time for losses and the count of losses, then divide to get the average game time for losses
    df_sorted['cumulative_game_time_losses'] = (df_sorted[df_sorted['result'] == 0].groupby('team')['game_time'].transform('cumsum') / 
                                                (df_sorted[df_sorted['result'] == 0].groupby('team').cumcount() + 1)).fillna(0)
    
    # Convert the 'kda' column to numeric
    df_sorted['kda'] = pd.to_numeric(df_sorted['kda'], errors='coerce')

    # Compute the cumulative average of KDA for wins
    df_sorted['cumulative_kda_wins'] = (df_sorted[df_sorted['result'] == 1].groupby('team')['kda'].transform('cumsum') / 
                                        df_sorted[df_sorted['result'] == 1].groupby('team')['result'].transform('cumsum')).fillna(0)

    # Compute the cumulative average of KDA for losses
    df_sorted['cumulative_kda_losses'] = (df_sorted[df_sorted['result'] == 0].groupby('team')['kda'].transform('cumsum') / 
                                        (df_sorted[df_sorted['result'] == 0].groupby('team').cumcount() + 1)).fillna(0)

    # Calculate win streak for each team based on match_id
    df_sorted['win_streak_match'] = df_sorted.groupby(['team', 'match_id'])['result'].transform(compute_win_streak)

    # Compute the cumulative win rate for each team based on match_id
    df_sorted['cumulative_win_rate_match'] = (df_sorted.groupby(['team', 'match_id'])['result'].transform('cumsum') / 
                                            (df_sorted.groupby(['team', 'match_id']).cumcount() + 1)).fillna(0)
    
    # First, create a mapping of game_id to the teams and their elos in that game
    game_elo_mapping = df.set_index(['game_id', 'team'])['elo'].to_dict()

    # Create a function to get the opponent's elo for a given row
    def get_opponent_elo(row):
        game_id = row['game_id']
        team = row['team']
        for (gid, t), elo in game_elo_mapping.items():
            if gid == game_id and t != team:
                return elo
        return None
    
    df_modified = df.copy()
    # Apply the function to get opponent_elo for each row
    df_modified['opponent_elo'] = df_modified.apply(get_opponent_elo, axis=1)

    df_modified['avg_opponent_elo_last_n'] = df_modified.groupby('team')['opponent_elo'].rolling(window=n).mean().reset_index(level=0, drop=True)

    return df_modified


