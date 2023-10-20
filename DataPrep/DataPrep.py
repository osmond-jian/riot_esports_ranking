import numpy as np
import pandas as pd
import json
import sys
import mapping as mp
import logging
sys.path.append("./")

import Modelling.Simple.elo as elo

# Create a logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# Create a file handler
fh = logging.FileHandler('mylog.log')
fh.setLevel(logging.DEBUG)

# Create a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)       

if __name__ == "__main__":
    ### Run this to get data to upload to S3 bucket to continue analysis and modelling
    
    # Load all the data
    filepath = f"C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/"

    map_data = mp.game_mapping(filepath=filepath)
    map_data = mp.player_mapping(map_data,filepath)
    map_data = mp.team_mapping(map_data,filepath)

    league_data = mp.league_mapping(filepath)

    tournament_data = mp.tournament_mapping(filepath)

    # Merges
    tournament_data =  tournament_data.merge(map_data,how="left",left_on='game_id',right_on='esportsGameId')
    tournament_data = tournament_data.merge(league_data,how="left",on='tournament_id')
    #tournament_data.to_parquet("combined_data_raw.parquet")

    # Data Validation
    t_d_unique = set(tournament_data['game_id'])
    m_d_unique = set(map_data['esportsGameId'])
    t_d_diff = t_d_unique.difference(m_d_unique)
    m_d_diff = m_d_unique.difference(t_d_unique)

    logger.info(f"Game_id in Tournament Data not in Mapping Data: {t_d_diff}")
    logger.info(f"esportsGameId in Mapping Data not in Tournament Data: {m_d_diff}")

    t_d_unique_2 = set(tournament_data['tournament_id'])
    l_d_unique_2 = set(league_data['tournament_id'])
    t_d_diff_2 = t_d_unique_2.difference(l_d_unique_2)
    l_d_diff = l_d_unique_2.difference(t_d_unique_2)

    logger.info(f"Tournament_id in Tournament Data not in League Data: {t_d_diff_2}")
    logger.info(f"Tournament_id in League Data not in Tournament Data: {l_d_diff}")
    
    with open("tournament_unique.txt", "w") as output:
        output.write(str(t_d_diff))
    
    with open("map_unique.txt", "w") as output:
        output.write(str(m_d_diff))

    with open("tournament_unique2.txt", "w") as output:
        output.write(str(t_d_diff_2))
    
    with open("league_unique.txt", "w") as output:
        output.write(str(l_d_diff))
    
    # update logger to count how many unique games and how many are missing and the proportion
    # do some adhoc analysis
    # save the list of missing games for analysis in mapping
    # make the game record work
    #tournament_data.sample(20).to_csv("raw_data_sample.csv")

    # Clean Data

    col_list = [
    'teammapping_200',
    'teammapping_100',
    'participantmapping_3',
    'participantmapping_5',
    'participantmapping_10',
    'participantmapping_2',
    'participantmapping_1',
    'participantmapping_9',
    'participantmapping_7',
    'participantmapping_8',
    'participantmapping_6',
    'participantmapping_4',
    'id',
    'name',
    'image',
    'lightImage',
    'darkImage',
    'priority',
    'displayPriority']

    df = tournament_data.drop(columns=col_list)

    # rename and reorder data
    # check missing rows
    # need to do some work for LPL mapping

    df.to_parquet("combined_data.parquet")

    ## Scoring the data
    
    teams_list = pd.concat([df['team1_id'], df['team2_id']]).unique()
    
    # initialize elo ratings
    elo_ratings = elo.initialize_elo_ratings(teams_list)

    # calculate Elo ratings over time
    elo_df = elo.elo_ratings_over_time(df.sort_values(['startDate']),elo_ratings)

    elo_df.to_csv('combined_data_uncleaned_v1.csv')
