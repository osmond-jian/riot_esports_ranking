import ast
import pandas as pd
import sys
import json
sys.path.append("..")

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

def safe_append(target_list, data, key):
    try:
        target_list.append(data[key])
    except (TypeError, KeyError):
        target_list.append(None)


def game_mapping(filepath:str,file:str = 'mapping_data.json')->pd.DataFrame:
    """Flattens game mapping data for tabular format merge

    Args:
        filepath (str): path to directory with the data provided by the hackathon
        file (str, optional): _description_. Defaults to 'mapping_data.json'.

    Returns:
        pd.DataFrame: Game mapping data in tabular format
    """
    with open(filepath+file, 'r') as f:
        data = json.load(f)
    
    # Flatten the data and create the DataFrame

    # Initialize lists to store flattened data
    flat_data = []

    # Iterate through the data and flatten it
    for item in data:
        flattened = {
            'esportsGameId': item['esportsGameId'],
            'platformGameId': item['platformGameId'],
            **{f'teammapping_{k}': v for k, v in item['teamMapping'].items()},
            **{f'participantmapping_{k}': v for k, v in item['participantMapping'].items()}
        }
        flat_data.append(flattened)

    # Create a DataFrame
    df = pd.DataFrame(flat_data)
    return df

def player_mapping(df:pd.DataFrame,filepath:str,file:str = 'players.json')->pd.DataFrame:
    """Creates a dict to map player data to game_data

    Args:
        df (pd.DataFrame): game_mapping data
        filepath (str): path to directory with the data provided by the hackathon
        file (str, optional): _description_. Defaults to 'mapping_data.json'.

    Returns:
        pd.DataFrame: game mapping data in tabular format with player names included
    """
    with open(filepath+file, 'r') as f:
        data = json.load(f)

    # Create a mapping dictionary from player_id to handle
    player_id_to_handle = {player['player_id']: player['handle'] for player in data}

    # Create new columns in the original DataFrame
    for i in range(1,11):
        df[f'player_{i}'] = df[f'participantmapping_{i}'].map(player_id_to_handle)
    return df

def team_mapping(df:pd.DataFrame,filepath:str,file:str = 'teams.json',
                 extra_teams_path:str = "C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/DataPrep/Data_for_Merging/missing_team_mapping.csv")->pd.DataFrame:
    """Creates a dict to map team data to game_data

    Args:
        df (pd.DataFrame): game_mapping data
        filepath (str): path to directory with the data provided by the hackathon
        file (str, optional): _description_. Defaults to 'mapping_data.json'.

    Returns:
        pd.DataFrame: game mapping data in tabular format with player names included
    """
    with open(filepath+file, 'r') as f:
        data = json.load(f)
    
    data_2 = pd.read_csv(extra_teams_path)
    missing_dict = data_2.set_index('team_id')['slug'].to_dict()

    # Create a mapping dictionary from player_id to handle
    team_id_to_slug = {team['team_id']: team['slug'] for team in data}
    team_id_to_slug.update(missing_dict)
    # Create new columns in the original DataFrame
    df[f'team_100'] = df[f'teammapping_100'].map(team_id_to_slug)
    df[f'team_200'] = df[f'teammapping_200'].map(team_id_to_slug)

    return df, team_id_to_slug

def league_mapping(filepath:str,file:str = 'leagues.json')->pd.DataFrame:
    """Flattens league data so it can be combined with tournament data

    Args:
        filepath (str): path to directory with the data provided by the hackathon
        file (str, optional): _description_. Defaults to 'mapping_data.json'.

    Returns:
        pd.DataFrame: game mapping data in tabular format with player names included
    """
    with open(filepath+file, 'r') as f:
        data = json.load(f)

    data = pd.DataFrame(data)

    # Explode the tournaments column
    leagues_exploded_df = data.explode('tournaments')

    # Extract the tournament id from the dictionaries
    leagues_exploded_df['tournament_id'] = leagues_exploded_df['tournaments'].apply(lambda x: x['id'] if pd.notna(x) else None)

    # Drop the original tournaments column
    leagues_exploded_df = leagues_exploded_df.drop(columns='tournaments')
    return leagues_exploded_df

def tournament_mapping(filepath:str,file:str = 'tournaments.json')->pd.DataFrame:
    """Flattens league data so it can be combined with tournament data

    Args:
        filepath (str): path to directory with the data provided by the hackathon
        file (str, optional): _description_. Defaults to 'mapping_data.json'.

    Returns:
        pd.DataFrame: game mapping data in tabular format with player names included
    """
    ### Creating a tournament df by making tables of the nested data
    with open(filepath+file, 'r') as f:
        data = json.load(f)
    
    # Adjusted extraction to handle potential None values in team_info['record']

    flattened_data_games = []
    i = 0
    # Loop through each tournament
    for tournament in data:
        # Extract tournament information
        tournament_info = {key: tournament[key] for key in ['id', 'leagueId', 'slug', 'startDate', 'endDate']}
        tournament_info['tournament_name'] = tournament_info['slug']
        del tournament_info['slug']
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

                    team_wins, team_loss, team_tie, match_outcome, match_gamewins = [], [], [], [], []

                    for team in match.get('teams',[]):
                        team_record = team.get('record',[])
                        team_result = team.get('result',[])

                        safe_append(team_wins, team_record, 'wins')
                        safe_append(team_loss, team_record, 'losses')
                        safe_append(team_tie, team_record, 'ties')
                        safe_append(match_outcome, team_result, 'outcome')
                        safe_append(match_gamewins, team_result, 'gameWins')
                                                
                    # Extract game information and include match_id
                    for game in match.get('games', []):
                        game_team_info = game.get('teams',[])
                        
                        # some extra logic for team records

                        flattened_data_games.append({

                            'game_id' : game['id'],
                            'game_state' : game['state'],
                            'game_number' : game['number'],

                            'team1_id' : game_team_info[0]['id'] if len(game_team_info) > 0 else None,
                            'team1_side' : game_team_info[0]['side'] if len(game_team_info) > 0 else None,
                            'team1_result' : game_team_info[0]['result']['outcome'] if game_team_info[0]['result'] is not None else None,
                            'team1_record_wins' : team_wins[0] if team_wins[0] is not None else None,
                            'team1_record_losses' : team_loss[0] if team_loss[0] is not None else None,
                            'team1_record_ties' : team_tie[0] if team_tie[0] is not None else None,
                            'team1_gamewins' : match_gamewins[0] if match_gamewins[0] is not None else None,

                            'team2_id' : game_team_info[1]['id'] if len(game_team_info) > 1 else None,
                            'team2_side' : game_team_info[1]['side'] if len(game_team_info) > 1 else None,
                            'team2_result' : game_team_info[1]['result']['outcome'] if game_team_info[1]['result'] is not None else None,
                            'team2_record_wins' : team_wins[1] if team_wins[1] is not None else None,
                            'team2_record_losses' : team_loss[1] if team_loss[1] is not None else None,
                            'team2_record_ties' : team_tie[1] if team_tie[1] is not None else None,
                            'team2_gamewins' : match_gamewins[1] if match_gamewins[1] is not None else None,

                            'match_id': match_id,
                            'match_state': match_state,
                            'match_strategy' : match_strategy,
                            'match_count':match_count,
                            'match_result_team_1': match_outcome[0],
                            'match_result_team_2': match_outcome[1],

                            **tournament_info,
                            **stage_info
                        })
                # for rankings in section.get('rankings', []):
                # we can get the rankings data later for validation purposes


    # Convert the flattened data to DataFrames
    df_games = pd.DataFrame(flattened_data_games)

    # Ensuring the 'tournament_id' column is correctly labeled in both DataFrames
    df_games.rename(columns={'id': 'tournament_id'}, inplace=True)

    return df_games


if __name__ == "__main__":
    
    filepath = f"C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/"

    map_data = game_mapping(filepath=filepath)
    map_data = player_mapping(map_data,filepath)
    map_data = team_mapping(map_data,filepath)
    #map_data.to_parquet("mapping_data.parquet")

    league_data = league_mapping(filepath)
    #league_data.to_parquet("league_data.parquet")

    tournament_data = tournament_mapping(filepath)
    #tournament_data.to_parquet("tournament_data.parquet")
    print(tournament_data.head())
 

