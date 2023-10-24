import pandas as pd
from sklearn.datasets import dump_svmlight_file
from sklearn.model_selection import train_test_split

columns_to_drop = [
    'game_state', 'game_number', 'match_id', 'match_state', 
    'match_strategy', 'match_count', 'tournament_id', 'leagueId',
    'endDate', 'slug_x', 'esportsGameId', 'platformGameId', 
    'slug_y', 'sport', 'region', 'platformgameid_x', 'earliest_eventtime',
    'platformgameid_y', 'max_gametime', 'platformgameid', 'game_time', 
    'id', 'side', 'result', 'record_wins', 'record_losses', 'record_ties', 
    'gamewins', 'region_type'
]

def convert_data_for_xgboost(df,cols):
    data = df.copy()
    c = data['result'].map({'loss': 0, 'win': 1, 'forfeit' : 0})
    data = df.drop(columns=cols)
    numerical_features = data.select_dtypes(include=['float64', 'int64']).columns
    data[numerical_features] = data[numerical_features].fillna(data[numerical_features].mean())
    data['target'] = c
    data['team'] = data['team'].fillna('other_team')


    data.drop(columns=['data_split']).to_csv("total_v6.csv",header=False,index=False)
    data[data['data_split']=='train'].drop(columns=['data_split']).to_csv("train_v6.csv")
    data[data['data_split']!='train'].drop(columns=['data_split']).to_csv("test_v6.csv")

def convert_preds_for_xgboost(df,cols):
    cols.remove('region')
    cols.remove('date')
    data = df.copy()
    data = df.drop(columns=cols)
    numerical_features = data.select_dtypes(include=['float64', 'int64']).columns
    data[numerical_features] = data[numerical_features].fillna(data[numerical_features].mean())
    data['team'] = data['team'].fillna('other_team')
    data.to_csv('for_predictions.csv')

def get_tournament_rankings(data):

    # Group the data by 'tournament_name' and 'team' without filtering by date
    grouped_data = data.groupby(['tournament_name', 'team'])

    # For each group, get the maximum 'opponent_elo'
    max_opponent_elo = grouped_data['opponent_elo'].max()

    # Rank the teams within each tournament based on this maximum 'opponent_elo'
    rankings = max_opponent_elo.groupby('tournament_name').rank(ascending=False, method='min')

    # Convert the rankings to a nested dictionary format
    ranking_dict_unfiltered = rankings.unstack().to_dict(orient='index')

    # Filter out teams based on their participation in the respective tournaments
    participating_teams = data.groupby('tournament_name')['team'].unique()

    # Create a nested dictionary with rankings only for teams that participated in the specific tournament
    filtered_ranking_dict = {}
    for tournament, teams in participating_teams.items():
        filtered_ranking_dict[tournament] = {team: ranking_dict_unfiltered[tournament].get(team, np.nan) 
                                            for team in teams if not np.isnan(ranking_dict_unfiltered[tournament].get(team))}

    return filtered_ranking_dict




df = pd.read_parquet("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/df_for_modelling.parquet")

convert_data_for_xgboost(df,columns_to_drop)

#df_preds = pd.read_parquet("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/Modelling/updated_df_for_modelling_v2.parquet")
#print(df_preds.shape)
#convert_preds_for_xgboost(df_preds,columns_to_drop)
