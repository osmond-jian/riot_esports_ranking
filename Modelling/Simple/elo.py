import numpy as np
import pandas as pd
import json
import sys

import logging
sys.path.append("../")

def initialize_elo_ratings(teams:list, slug ={} ,initial_elo=1000,use_custom=True):
    #todo update to initialize_elo based off region or previous tournament ranking

    """
    Initialize Elo ratings for each team.
    
    Parameters:
        teams (list): List of unique team IDs.
        initial_elo (int): Initial Elo rating to be assigned to each team.
    
    Returns:
        dict: Dictionary mapping team IDs to their initial Elo ratings.
    """
    out = {team: initial_elo for team in teams}
    if use_custom:
        df = pd.read_excel("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/teamid_elo.xlsx")
        elos = dict(df.set_index('team_id')['elo'])
        # Update the 'out' dictionary with values from the CSV
        for team in elos:
            if team in out:
                out[team] = elos[team]

    return out


def update_elo(rating1, rating2, result, k1, k2):
    """
    Update Elo ratings after a match.
    
    Parameters:
        rating1, rating2 (float): Current Elo ratings of team 1 and team 2.
        result (float): Result of the match (1 if team 1 wins, 0 if team 2 wins, 0.5 for a draw).
        k1, k2 (float): K-factors for team 1 and team 2.
    
    Returns:
        tuple: New Elo ratings for team 1 and team 2.
    """
    expected1 = 1 / (1 + 10**((rating2 - rating1) / 400))
    expected2 = 1 - expected1
    
    new_rating1 = rating1 + k1 * (result - expected1)
    new_rating2 = rating2 + k2 * (1 - result - expected2)
    
    return new_rating1, new_rating2


def elo_ratings_over_time(matches, elo_ratings, k_value=32, k_adjustment_game_num=3, weight=0.5):
    """
    Calculate Elo ratings over time given match results, with a soft reset
    at the start of each new tournament for a team.
    
    Parameters:
        matches (DataFrame): DataFrame containing match results.
        elo_ratings (dict): Initial Elo ratings for each team.
        k_value (float): K-factor for Elo rating updates.
        k_adjustment_game_num (int): Game number at which to adjust the K-factor.
        weight (float): Weight for the soft reset of Elo ratings.
    
    Returns:
        DataFrame: DataFrame with Elo ratings after each match.
    """
    # Placeholder for Elo ratings over time
    elo_ratings_over_time = []
    
    # Tracker for the last tournament each team participated in
    last_tournament = {team: None for team in elo_ratings.keys()}
    
    for _, row in matches.iterrows():
        # Extract relevant information
        team1, team2 = row['team1_id'], row['team2_id']
        result = 1 if row['team1_result'] == 'win' else 0
        game_num = row['game_number']
        game_id = row['game_id']
        tournament = row['tournament_id']
        
        # Soft reset if a team is in a new tournament
        # update this for when I have team region included
        for team in [team1, team2]:
            if last_tournament[team] != tournament:
                baseline_elo = sum(elo_ratings.values()) / len(elo_ratings)  # Average Elo of all teams
                elo_ratings[team] = weight * elo_ratings[team] + (1 - weight) * baseline_elo
                
                last_tournament[team] = tournament  # Update the last tournament tracker
        
        # Adjust K-value if game number is 3 or higher
        k1 = k2 = k_value * 1.5 if game_num >= k_adjustment_game_num else k_value
        
        # Update Elo ratings
        new_rating1, new_rating2 = update_elo(elo_ratings[team1], elo_ratings[team2], result, k1, k2)
        
        # Update Elo ratings in the dictionary
        elo_ratings[team1], elo_ratings[team2] = new_rating1, new_rating2
        
        # Log the updated Elo ratings
        elo_ratings_over_time.append((tournament,game_id,game_num,team1, team2, new_rating1, new_rating2))
        
    # Convert to DataFrame for easier analysis and visualization
    elo_df = pd.DataFrame(elo_ratings_over_time, columns=['tournamentid','game_id','game_num','team1', 'team2', 'elo_team1', 'elo_team2'])
    
    return elo_df


if __name__ == "__main__":
    df = pd.read_parquet("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/combined_data.parquet")
    teams_list = pd.concat([df['team1_id'], df['team2_id']]).unique()
    
    # initialize elo ratings
    elo_ratings = initialize_elo_ratings(teams_list)

    # calculate Elo ratings over time
    elo_df = elo_ratings_over_time(df.sort_values(['startDate']),elo_ratings)

    elo_df.to_csv('combined_data_uncleaned_v1.csv')


    # # Initialize Elo ratings for all teams
    # teams = pd.concat([cleaned_data['team1_id'], cleaned_data['team2_id']]).unique()
    # elo_ratings = initialize_elo_ratings(teams)

    # # Calculate Elo ratings over time
    # elo_df = elo_ratings_over_time(cleaned_data, elo_ratings)

    # # Display updated Elo ratings after each match
    # elo_df.tail()
    
    # # Extracting the final Elo ratings for each team
    # final_elo_ratings = elo_df.groupby(['team1', 'team2']).last().reset_index()[['team1', 'elo1']].rename(columns={'team1': 'team', 'elo1': 'elo'})
    # final_elo_ratings = final_elo_ratings.append(elo_df.groupby(['team1', 'team2']).last().reset_index()[['team2', 'elo2']].rename(columns={'team2': 'team', 'elo2': 'elo'}))
    # final_elo_ratings = final_elo_ratings.groupby('team').mean().reset_index()

    # # Getting the top 10 teams based on their final Elo ratings
    # top_teams = final_elo_ratings.nlargest(10, 'elo')

    # # Extracting Elo history for the top 10 teams
    # elo_history = elo_df.melt(id_vars=['elo1', 'elo2'], value_vars=['team1', 'team2'], var_name='team_type', value_name='team')
    # elo_history['elo'] = elo_history.apply(lambda x: x['elo1'] if x['team_type'] == 'team1' else x['elo2'], axis=1)
    # elo_history_top_teams = elo_history[elo_history['team'].isin(top_teams['team'])]

    # # Visualization
    # plt.figure(figsize=(14, 6))
    # sns.lineplot(data=elo_history_top_teams, x=elo_history_top_teams.index, y='elo', hue='team', palette='tab10', lw=2)
    # plt.title('Elo Ratings Over Time for the Top 10 Teams', fontsize=16)
    # plt.xlabel('Match Index', fontsize=12)
    # plt.ylabel('Elo Rating', fontsize=12)
    # plt.legend(title='Team ID', bbox_to_anchor=(1.05, 1), loc='upper left')
    # plt.grid(axis='y')
    # plt.tight_layout()
    # plt.show()

    # (top_teams, final_elo_ratings.describe())
