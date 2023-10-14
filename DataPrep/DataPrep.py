import numpy as np
import pandas as pd
import json
import sys

def create_map(data:list,id:str,name:str)-> dict:
    """Function to create a mapping from id to name.  Will be utilized to create a mapping for
    teams, players, tournament names, league names

    Args:
        data (list): list of dictionaries containing the id as the key
        id (str): key for id
        name (str): key for associated name

    Returns:
        dict: key-value pairs such that id:name.  Will be used in various data structures to map the correct names
    """
    id_map = {entry[id]: entry[name] for entry in data}
    return id_map

def id_to_handle(indices, player_id_map):
    return {index: player_id_map[player_id] for index, player_id in indices.items() if player_id in player_id_map}



        

if __name__ == "__main__":
    ### Creating player mapping tables for reference
    sys.path.append("..")
    with open(f'C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/players.json', 'r') as f:
        player_data = json.load(f)

    player_map = create_map(player_data,'player_id','handle')

    ### Creating Team mapping table
    with open(f'C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/teams.json', 'r') as f:
        team_data = json.load(f)

    team_map = create_map(team_data,'team_id','slug')


    ### Creating a tournament df by making tables of the nested data
    with open(f'C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/tournaments.json', 'r') as f:
        data = json.load(f)


    # Adjusted extraction to handle potential None values in team_info['record']

    flattened_data_games = []
    flattened_data_with_teams = []

    # Loop through each tournament
    for tournament in data:
        # Extract tournament information
        tournament_info = {key: tournament[key] for key in ['id', 'leagueId', 'slug', 'startDate', 'endDate']}
        
        # Loop through each stage in the tournament
        for stage in tournament.get('stages', []):
            stage_info = {key: stage[key] for key in ['slug']}
            
            # Loop through each section in the stage
            for section in stage.get('sections', []):
                # Loop through each match in the section
                for match in section.get('matches', []):
                    match_id = match['id']
                    match_state = match['state']
                    match_strategy = match['strategy']['type']
                    match_count = match['strategy']['count']
                    team_info = match.get('teams', [])
                    
                    # Extract game information and include match_id
                    for game in match.get('games', []):
                        game_team_info = game.get('teams',[])
                        flattened_data_games.append({
                            'game_id' : game['id'],
                            'game_state' : game['state'],
                            'game_number' : game['number'],
                            'team1_id' : game_team_info[0]['id'] if len(game_team_info) > 0 else None,
                            'team1_side' : game_team_info[0]['side'] if len(game_team_info) > 0 else None,
                            'team1_result' : game_team_info[0]['result']['outcome'] if game_team_info[0]['result'] is not None else None,
                            'team2_id' : game_team_info[1]['id'] if len(game_team_info) > 1 else None,
                            'team2_side' : game_team_info[1]['side'] if len(game_team_info) > 1 else None,
                            'team2_result' : game_team_info[1]['result']['outcome'] if game_team_info[1]['result'] is not None else None,
                            # 'match_id': match_id,
                            # 'match_state': match_state,
                            # "match_strategy" : match_strategy,
                            # 'match_count':match_count,


                            **tournament_info,
                            **stage_info
                        })


    # Convert the flattened data to DataFrames
    df_games_with_match_id = pd.DataFrame(flattened_data_games)
    #df_teams_info_with_match_id = pd.DataFrame(flattened_data_with_teams)

    # Ensuring the 'tournament_id' column is correctly labeled in both DataFrames
    df_games_with_match_id.rename(columns={'id': 'tournament_id'}, inplace=True)
    #df_teams_info_with_match_id.rename(columns={'id': 'tournament_id'}, inplace=True)

    # Merge the two dataframes based on only the match_id column
    #df_simplified_merge = pd.merge(df_games_with_match_id, df_teams_info_with_match_id, on='match_id', how='inner')

    # Display the merged dataframe
    df_games_with_match_id.to_csv("df_simplified.csv")


