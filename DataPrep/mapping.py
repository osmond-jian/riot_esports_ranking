import ast
import pandas as pd
import sys
import json
sys.path.append("..")

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

def team_mapping(df:pd.DataFrame,filepath:str,file:str = 'teams.json')->pd.DataFrame:
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

    # Create a mapping dictionary from player_id to handle
    team_id_to_slug = {team['team_id']: team['slug'] for team in data}
    # Create new columns in the original DataFrame
    df[f'team_100'] = df[f'teammapping_100'].map(team_id_to_slug)
    df[f'team_200'] = df[f'teammapping_100'].map(team_id_to_slug)

    return df

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



if __name__ == "__main__":
    
    filepath = f"C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/"

    map_data = game_mapping(filepath=filepath)
    map_data = player_mapping(map_data,filepath)
    map_data = team_mapping(map_data,filepath)
    map_data.to_parquet("mapping_data.parquet")

    league_data = league_mapping(filepath)
    league_data.to_parquet("league_data.parquet")


 

