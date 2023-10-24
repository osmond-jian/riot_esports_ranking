import numpy as np
import pandas as pd
import json
import sys
import mapping as mp
import logging
sys.path.append("./")

import Modelling.Simple.elo as elo
from FeatureEng import feature_eng
import FeatAggs as fea

def stack_teams(data:pd.DataFrame)->pd.DataFrame:

    # Shared columns
    not_shared = ['team1',"team2","participant","player","team_","t100","t200"]
    shared_columns = [col for col in df.columns if all(u not in col for u in not_shared)]

    # Create mappings for t100 -> team1 and t200 -> team2
    initial_rename_dict = {col: col.replace('t100', 'team1').replace('t200', 'team2') for col in data.columns if 't100' in col or 't200' in col}
    data = data.rename(columns=initial_rename_dict)

    # Dynamically create column mappings for team100 and team200
    team100_columns = {col: col.replace('_team1', '').replace('team1_', '') for col in data.columns if 'team1' in col}
    team200_columns = {col: col.replace('_team2', '').replace('team2_', '') for col in data.columns if 'team2' in col}

    # Adjust mappings for team names
    team100_columns["team_100"] = "team"
    team200_columns["team_200"] = "team"

    team100_data = data.rename(columns=team100_columns)[shared_columns + list(team100_columns.values())]
    team200_data = data.rename(columns=team200_columns)[shared_columns + list(team200_columns.values())]

    # Combine team100 and team200 data
    combined_data = pd.concat([team100_data, team200_data], ignore_index=True)
    return combined_data

def pivot_and_rename(df, column):
    # Pivot the data
    pivoted = df.pivot(index='platformgameid', columns='player_id', values=column)
    # Rename columns
    pivoted.columns = [f"{column}_participant{col}" for col in pivoted.columns]
    return pivoted
    # Function to compute win streaks


def compute_win_streak(series):
    streak = 0
    streak_list = []
    for s in series:
        if s == "win":
            streak += 1
        else:
            streak = 0
        streak_list.append(streak)
    return streak_list

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
    map_data, slug_dict = mp.team_mapping(map_data,filepath)

    league_data = mp.league_mapping(filepath)

    tournament_data = mp.tournament_mapping(filepath)

    # Merges
    tournament_data =  tournament_data.merge(map_data,how="left",left_on='game_id',right_on='esportsGameId')
    tournament_data = tournament_data.merge(league_data,how="left",on='tournament_id')

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


    # remove any unneeded columns
    df = df[df['game_state'] != "unneeded"]
    # we'll drop data without game mapping after the scoring is done


    ## Add starting time to data
    game_dates = pd.read_csv("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/DataPrep/Data_for_Merging/game_date.csv")
    df = df.merge(game_dates,left_on='platformGameId', right_on='platformgameid')
    df['date'] = pd.to_datetime(df['earliest_eventtime'], format='ISO8601')
    ### Scoring the data
    
    teams_list = pd.concat([df['team1_id'], df['team2_id']]).unique()
    
    # initialize elo ratings
    elo_ratings = elo.initialize_elo_ratings(teams_list,slug_dict)

    # calculate Elo ratings over time
    elo_df = elo.elo_ratings_over_time(df.sort_values(['date']),elo_ratings)

    #elo_df.to_csv('elo_df.csv')
    df = df.merge(elo_df[['game_id','elo_team1','elo_team2']],how ='left', on="game_id")

    ## Merge team data by esportsid
    team_agg = pd.read_csv('C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/DataPrep/Data_for_Merging/teamsaggregated.csv')
    df = df.merge(team_agg,how='inner',left_on='platformGameId', right_on='platformgameid')

    ## Prepare participants data for merging
    part_data = pd.read_csv("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/DataPrep/Data_for_Merging/participantsagg.csv")
    # List of columns to pivot excluding platformgameid and player_id
    columns_to_pivot = part_data.columns.difference(['platformgameid', 'player_id'])

    # Use the function to pivot and rename all columns and then merge them together
    merged_df = pd.concat([pivot_and_rename(part_data, col) for col in columns_to_pivot], axis=1).reset_index()
    df = df.merge(merged_df,left_on='platformGameId', right_on='platformgameid')
    #df.sample(1000).to_csv("elo_sample.csv")
    # Feature Engineering
    df = feature_eng(df)
    print(df.shape)

    #df.to_parquet("df_feateng.parquet")
    #df.sample(100).to_csv("df_feateng.csv")

    # Stack data
    df_stacked = stack_teams(df)
    #df_stacked.to_parquet("df_stacked.parquet")
    #df_stacked.sort_values(['date'])[:1000].to_csv("df_stacked_new.csv")
    print(df_stacked.shape)

    avg_cols = [
        'elo',
        'gold',
        'deaths',
        'kills',
        'assists',
        'inhibkills',
        'towerkills',
        'baronkills',
        'dragonkills',
        'kda',
        'kill_delta',
        'deaths_delta',
        'assists_delta',
        'gold_delta',
        'baron_delta',
        'dragon_delta',
        'tower_delta',
        'inhib_delta',
        'support_assists_delta',
        'jungle_assists_delta',
        'toplane_plate_dmg_delta',
        'jungle_obj_dmg_delta',
        'top_wards_killed',
        'jungle_wards_killed',
        'mid_wards_killed',
        'adc_wards_killed',
        'support_wards_killed',
        'wards_killed_delta',
        'top_wards_killed_delta',
        'jungle_wards_killed_delta',
        'mid_wards_killed_delta',
        'adc_wards_killed_delta',
        'support_wards_killed_delta',
        'vision_score_delta',
        'jungle_vision_score_delta',
        'support_vision_score_delta',
        'jungle_nmk_delta',
        'jungle_nmk_enemy_delta',
        'cc_delta',
        'cc',
        'jg_cc_delta',
        'support_cc_delta',
        'wards_placed',
        'wards_placed_delta',
        'support_wards_placed_delta',
        'jg_wards_placed_delta',
        'magic_dmg_dealt_delta',
        'jg_magic_dmg_dealt_delta',
        'top_magic_dmg_dealt_delta',
        'mid_magic_dmg_dealt_delta',
        'adc_magic_dmg_dealt_delta',
        'phys_dmg_dealt_delta',
        'jg_phys_dmg_dealt_delta',
        'top_phys_dmg_dealt_delta',
        'mid_phys_dmg_dealt_delta',
        'adc_phys_dmg_dealt_delta',
        'total_dmg_dealt',
        'top_total_dmg_dealt',
        'jg_total_dmg_dealt',
        'mid_total_dmg_dealt',
        'adc_total_dmg_dealt',
        'sup_total_dmg_dealt',
        'top_total_dmg_taken',
        'jg_total_dmg_taken',
        'mid_total_dmg_taken',
        'adc_total_dmg_taken',
        'sup_total_dmg_taken',
        'total_dmg_dealt_delta',
        'top_total_dmg_dealt_delta',
        'jg_total_dmg_dealt_delta',
        'mid_total_dmg_dealt_delta',
        'adc_total_dmg_dealt_delta',
        'total_dmg_taken',
        'top_total_dmg_taken_delta',
        'jg_total_dmg_taken_delta',
        'mid_total_dmg_taken_delta',
        'adc_total_dmg_taken_delta',
        'support_wards_killed_per_death',
        'support_wards_killed_per_death_delta',
        'jg_wards_killed_per_death',
        'jg_wards_killed_per_death_delta',
        'support_wards_placed_per_death',
        'support_wards_placed_per_death_delta',
        'jg_wards_placed_per_death',
        'jg_wards_placed_per_death_delta',
        'top_total_dmg_dealt_per_death',
        'top_total_dmg_dealt_per_death_delta',
        'jg_total_dmg_dealt_per_death',
        'jg_total_dmg_dealt_per_death_delta',
        'mid_total_dmg_dealt_per_death',
        'mid_total_dmg_dealt_per_death_delta',
        'adc_total_dmg_dealt_per_death',
        'adc_total_dmg_dealt_per_death_delta',
        'sup_total_dmg_dealt_per_death',
        'sup_total_dmg_dealt_per_death_delta',
        'top_total_dmg_taken_per_death',
        'jg_total_dmg_taken_per_death',
        'mid_total_dmg_taken_per_death',
        'adc_total_dmg_taken_per_death',
        'sup_total_dmg_taken_per_death',
        'top_total_dmg_taken_per_death_delta',
        'jg_total_dmg_taken_per_death_delta',
        'mid_total_dmg_taken_per_death_delta',
        'adc_total_dmg_taken_per_death_delta',
        'sup_total_dmg_taken_per_death_delta',
        'top_total_dmg_dealt_per_kill',
        'jg_total_dmg_dealt_per_kill',
        'mid_total_dmg_dealt_per_kill',
        'adc_total_dmg_dealt_per_kill',
        'sup_total_dmg_dealt_per_kill',
        'top_total_dmg_dealt_per_kill_delta',
        'jg_total_dmg_dealt_per_kill_delta',
        'mid_total_dmg_dealt_per_kill_delta',
        'adc_total_dmg_dealt_per_kill_delta',
        'sup_total_dmg_dealt_per_kill_delta',
        'top_kda',
        'jg_kda',
        'mid_kda',
        'adc_kda',
        'sup_kda',
        'top_kda_delta',
        'jg_kda_delta',
        'mid_kda_delta',
        'adc_kda_delta',
        'sup_kda_delta',
        'kill_assists_per_ward_placed',
        'kill_assists_per_ward_placed_delta',
        'kill_assists_per_cc_time',
        'kill_assists_per_cc_time_delta',
        'adc_kill_assists_per_cc_time',
        'adc_kill_per_cc_time',
        'mid_kill_assists_per_cc_time',
        'mid_kill_per_cc_time',
        'adc_kill_assists_per_cc_time_delta',
        'adc_kill_per_cc_time_delta',
        'mid_kill_assists_per_cc_time_delta',
        'mid_kill_per_cc_time_delta',
        'minions_killed',
        'minions_killed_delta',
        'top_minions_killed_delta',
        'jg_minions_killed_delta',
        'mid_minions_killed_delta',
        'adc_minions_killed_delta',
        'sup_minions_killed_delta',
        'top_minions_killed_per_death',
        'jg_minions_killed_per_death',
        'mid_minions_killed_per_death',
        'adc_minions_killed_per_death',
        'sup_minions_killed_per_death',
        'top_minions_killed_per_death_delta',
        'jg_minions_killed_per_death_delta',
        'mid_minions_killed_per_death_delta',
        'adc_minions_killed_per_death_delta',
        'sup_minions_killed_per_death_delta',
        'minions_killed_per_death',
        'minions_killed_per_death_delta',
        'adc_kill_pct',
        'top_kill_pct',
        'mid_kill_pct',
        'main_carries_kill_pct',
        'adc_kill_pct_delta',
        'top_kill_pct_delta',
        'mid_kill_pct_delta',
        'main_carries_kill_pct_delta',
        'adc_dmg_pct',
        'mid_dmg_pct',
        'top_dmg_pct',
        'adc_dmg_pct_delta',
        'mid_dmg_pct_delta',
        'top_dmg_pct_delta',
        'adc_dmg_taken_pct',
        'mid_dmg_taken_pct',
        'top_dmg_taken_pct',
        'jg_dmg_taken_pct',
        'sup_dmg_taken_pct',
        'noncarries_dmg_taken_pct',
        'adc_dmg_taken_pct_delta',
        'mid_dmg_taken_pct_delta',
        'top_dmg_taken_pct_delta',
        'jg_dmg_taken_pct_delta',
        'sup_dmg_taken_pct_delta',
        'noncarries_dmg_taken_pct_delta',
        'adc_death_participation',
        'top_death_participation',
        'jg_death_participation',
        'mid_death_participation',
        'sup_death_participation',
        'adc_death_participation_delta',
        'top_death_participation_delta',
        'mid_death_participation_delta',
        'jg_death_participation_delta',
        'sup_death_participation_delta',
        'elo_delta',

    ]

    # Aggregate data
    df_agg = fea.compute_win_stats(df_stacked,6)
    df_agg = fea.feature_averages(df_agg,avg_cols,'date',6,'team')

    # df for modelling
    df_agg['data_split'] = df_agg['date'].apply(lambda x: 'train' if x.year < 2023 else 'OOT')

    df_agg.to_parquet("df_for_modelling.parquet")
    df_agg[:1000].to_csv("df_for_modelling.csv")
