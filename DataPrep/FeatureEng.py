#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 15:23:55 2023

@author: joe, akmar
"""

import pandas as pd
import numpy as np
import os

def feature_eng(data:pd.DataFrame)-> pd.DataFrame: 
    """Function to create new features in modelling data before we aggregate it

    Args:
        data (pd.DataFrame): df_unagg

    Returns:
        pd.DataFrame: data prior to aggregation and stacking
    """
    # to address performance warnings, I can just add all the data to dict or new df and then concat
    # New column to convert max_gametime to minutes and seconds for sanity check
    data['game_time'] = data['max_gametime'].apply(lambda x: x / 60000)

    # Create new columns for the type of region the team is for team1 and team2
    result = []
    for name, group in data.groupby('team1_id')['slug_y']:
        if any(group.str.contains(r'lck|lec|lpl|lc')):
            result.extend(['major_region'] * len(group))
        else:
            result.extend(['minor_region'] * len(group))
    data['region_type_team1'] = result

    result2 = []
    for name, group in data.groupby('team2_id')['slug_y']:
        if any(group.str.contains(r'lck|lec|lpl|lc')):
            result2.extend(['major_region'] * len(group))
        else:
            result2.extend(['minor_region'] * len(group))
    data['region_type_team2'] = result2

    # Create new columns for what region the team plays in

    def region_from_slug(slug):
        if 'lck' in slug:
            return "LCK"
        elif 'lpl' in slug:
            return "LPL"
        elif 'lcs' in slug:
            return "LCS"
        elif 'lec' in slug:
            return "LEC"
        elif 'cblol-brazil' in slug:
            return "CBL"
        elif 'ljl-japan' in slug:
            return "LJL"
        elif 'vcs' in slug:
            return "VCS"
        elif 'pcs' in slug:
            return "PCS"
        elif 'lla' in slug:
            return "LLA"
        elif 'lco' in slug:
            return "LCO"
        elif 'turkiye-sampiyonluk-ligi' in slug:
            return "TCL"
        else:
            return "OTH"

    def region_from_slugs(slugs):
        # Filter out any non-string values in slugs
        slugs = [slug for slug in slugs if isinstance(slug, str)]
        
        # List of priority regions in slug form
        priority_slugs = ['lck', 'lpl', 'lcs', 'lec', 'cblol-brazil', 'ljl-japan', 'vcs', 'pcs', 'lla', 'lco', 'turkiye-sampiyonluk-ligi']

        # Check if any priority slug is in the slugs for the team
        for priority_slug in priority_slugs:
            if any(priority_slug in slug for slug in slugs):
                return region_from_slug(priority_slug)
        
        # If no priority slug was found, label as minor_region
        return "OTH"

    # Gather all slugs for each team1_id and team2_id
    team1_slugs = data.groupby('team1_id')['slug_y'].unique()
    team2_slugs = data.groupby('team2_id')['slug_y'].unique()

    # Create the mapping based on precedence
    team1_region_mapping = team1_slugs.apply(region_from_slugs).to_dict()
    team2_region_mapping = team2_slugs.apply(region_from_slugs).to_dict()

    # Apply the mapping to the data
    data['Region_team1'] = data['team1_id'].map(team1_region_mapping)
    data['Region_team2'] = data['team2_id'].map(team2_region_mapping)


    # Calculate KDA for team1 and team2
    data['kda_team1'] = (data['t100_kills'] + data['t100_assists']
                        ) / data['t100_deaths'].replace(0, 1)
    data['kda_team2'] = (data['t200_kills'] + data['t200_assists']
                        ) / data['t200_deaths'].replace(0, 1)

    # Other calculations
    data['kill_delta_team1'] = data['t100_kills'] - data['t200_kills']
    data['kill_delta_team2'] = data['t200_kills'] - data['t100_kills']

    data['deaths_delta_team1'] = data['t100_deaths'] - data['t200_deaths']
    data['deaths_delta_team2'] = data['t200_deaths'] - data['t100_deaths']

    data['assists_delta_team1'] = data['t100_assists'] - data['t200_assists']
    data['assists_delta_team2'] = data['t200_assists'] - data['t100_assists']

    data['gold_delta_team1'] = data['t100_gold'] - data['t200_gold']
    data['gold_delta_team2'] = data['t200_gold'] - data['t100_gold']

    data['baron_delta_team1'] = data['t100_baronkills'] - data['t200_baronkills']
    data['baron_delta_team2'] = data['t200_baronkills'] - data['t100_baronkills']

    data['dragon_delta_team1'] = data['t100_dragonkills'] - \
        data['t200_dragonkills']
    data['dragon_delta_team2'] = data['t200_dragonkills'] - \
        data['t100_dragonkills']

    data['tower_delta_team1'] = data['t100_towerkills'] - data['t200_towerkills']
    data['tower_delta_team2'] = data['t200_towerkills'] - data['t100_towerkills']

    data['inhib_delta_team1'] = data['t100_inhibkills'] - data['t200_inhibkills']
    data['inhib_delta_team2'] = data['t200_inhibkills'] - data['t100_inhibkills']

    data['support_assists_delta_team1'] = data['assists_participant5'] - \
        data['assists_participant10']
    data['support_assists_delta_team2'] = data['assists_participant10'] - \
        data['assists_participant5']

    data['jungle_assists_delta_team1'] = data['assists_participant2'] - \
        data['assists_participant10']
    data['jungle_assists_delta_team2'] = data['assists_participant7'] - \
        data['assists_participant5']

    data['toplane_plate_dmg_delta_team1'] = data['damage_buildings_participant1'] - \
        data['damage_buildings_participant6']
    data['toplane_plate_dmg_delta_team2'] = data['damage_buildings_participant6'] - \
        data['damage_buildings_participant1']

    data['jungle_obj_dmg_delta_team1'] = data['damage_objectives_participant2'] - \
        data['damage_objectives_participant7']
    data['jungle_obj_dmg_delta_team2'] = data['damage_objectives_participant7'] - \
        data['damage_objectives_participant2']


    # Calculate ward stuff + renaming
    data['team1_top_wards_killed'] = data['ward_killed_participant1']
    data['team1_jungle_wards_killed'] = data['ward_killed_participant2']
    data['team1_mid_wards_killed'] = data['ward_killed_participant3']
    data['team1_adc_wards_killed'] = data['ward_killed_participant4']
    data['team1_support_wards_killed'] = data['ward_killed_participant5']
    data['team2_top_wards_killed'] = data['ward_killed_participant6']
    data['team2_jungle_wards_killed'] = data['ward_killed_participant7']
    data['team2_mid_wards_killed'] = data['ward_killed_participant8']
    data['team2_adc_wards_killed'] = data['ward_killed_participant9']
    data['team2_support_wards_killed'] = data['ward_killed_participant10']

    # delta in wards killed for teams
    team1_wards_killed = data[['ward_killed_participant1', 'ward_killed_participant2',
                            'ward_killed_participant3', 'ward_killed_participant4', 'ward_killed_participant5']].sum(axis=1)
    team2_wards_killed = data[['ward_killed_participant6', 'ward_killed_participant7',
                            'ward_killed_participant8', 'ward_killed_participant9', 'ward_killed_participant10']].sum(axis=1)
    data['wards_killed_delta_team1'] = team1_wards_killed - team2_wards_killed
    data['wards_killed_delta_team2'] = team2_wards_killed - team1_wards_killed

    # delta in wards killed between roles
    roles = ['top', 'jungle', 'mid', 'adc', 'support']
    for role in roles:
        data[f'{role}_wards_killed_delta_team1'] = data[f'team1_{role}_wards_killed'] - \
            data[f'team2_{role}_wards_killed']
        data[f'{role}_wards_killed_delta_team2'] = data[f'team2_{role}_wards_killed'] - \
            data[f'team1_{role}_wards_killed']

    # Vision score delta
    team1_vision_score = data[['vision_score_participant1', 'vision_score_participant2',
                            'vision_score_participant3', 'vision_score_participant4', 'vision_score_participant5']].sum(axis=1)
    team2_vision_score = data[['vision_score_participant6', 'vision_score_participant7',
                            'vision_score_participant8', 'vision_score_participant9', 'vision_score_participant10']].sum(axis=1)
    data['vision_score_delta_team1'] = team1_vision_score - team2_vision_score
    data['vision_score_delta_team2'] = team2_vision_score - team1_vision_score

    # Vision score delta for jungle and support
    data['jungle_vision_score_delta_team1'] = data['vision_score_participant2'] - \
        data['vision_score_participant7']
    data['jungle_vision_score_delta_team2'] = data['vision_score_participant7'] - \
        data['vision_score_participant2']
    data['support_vision_score_delta_team1'] = data['vision_score_participant5'] - \
        data['vision_score_participant10']
    data['support_vision_score_delta_team2'] = data['vision_score_participant10'] - \
        data['vision_score_participant5']

    # Neutral minions killed delta
    data['jungle_nmk_delta_team1'] = data['neutral_minions_killed_participant2'] - \
        data['neutral_minions_killed_participant7']
    data['jungle_nmk_delta_team2'] = data['neutral_minions_killed_participant7'] - \
        data['neutral_minions_killed_participant2']

    # Enemy neutral minions killed delta
    data['jungle_nmk_enemy_delta_team1'] = data['nmk_enemy_participant2'] - \
        data['nmk_enemy_participant7']
    data['jungle_nmk_enemy_delta_team2'] = data['nmk_enemy_participant7'] - \
        data['nmk_enemy_participant2']

    # Time CCing others
    team1_cc = data[['time_ccing_others_participant1', 'time_ccing_others_participant2',
                    'time_ccing_others_participant3', 'time_ccing_others_participant4', 'time_ccing_others_participant5']].sum(axis=1)
    team2_cc = data[['time_ccing_others_participant6', 'time_ccing_others_participant7',
                    'time_ccing_others_participant8', 'time_ccing_others_participant9', 'time_ccing_others_participant10']].sum(axis=1)

    data['cc_delta_team1'] = team1_cc - team2_cc
    data['cc_delta_team2'] = team2_cc - team1_cc
    data['cc_team1'] = team1_cc
    data['cc_team2'] = team2_cc

    # CC delta for jungle and support
    data['jg_cc_delta_team1'] = data['time_ccing_others_participant2'] - \
        data['time_ccing_others_participant7']
    data['jg_cc_delta_team2'] = data['time_ccing_others_participant7'] - \
        data['time_ccing_others_participant2']
    data['support_cc_delta_team1'] = data['time_ccing_others_participant5'] - \
        data['time_ccing_others_participant10']
    data['support_cc_delta_team2'] = data['time_ccing_others_participant10'] - \
        data['time_ccing_others_participant5']

    # Wards placed delta
    team1_wards_placed = data[['ward_placed_participant1', 'ward_placed_participant2',
                            'ward_placed_participant3', 'ward_placed_participant4', 'ward_placed_participant5']].sum(axis=1)
    team2_wards_placed = data[['ward_placed_participant6', 'ward_placed_participant7',
                            'ward_placed_participant8', 'ward_placed_participant9', 'ward_placed_participant10']].sum(axis=1)

    data['wards_placed_team1'] = team1_wards_placed
    data['wards_placed_team2'] = team2_wards_placed


    # Calculate wards placed deltas for both teams
    data['wards_placed_delta_team1'] = data['wards_placed_team1'] - \
        data['wards_placed_team2']
    data['wards_placed_delta_team2'] = data['wards_placed_team2'] - \
        data['wards_placed_team1']

    # Calculate support wards placed deltas for both teams
    data['support_wards_placed_delta_team1'] = data['ward_placed_participant5'] - \
        data['ward_placed_participant10']
    data['support_wards_placed_delta_team2'] = data['ward_placed_participant10'] - \
        data['ward_placed_participant5']

    # Calculate jungle wards placed deltas for both teams
    data['jg_wards_placed_delta_team1'] = data['ward_placed_participant2'] - \
        data['ward_placed_participant7']
    data['jg_wards_placed_delta_team2'] = data['ward_placed_participant7'] - \
        data['ward_placed_participant2']

    # Calculate magic damage dealt deltas for both teams
    magic_dmg_team1 = data[['magic_damage_dealt_participant1', 'magic_damage_dealt_participant2',
                            'magic_damage_dealt_participant3', 'magic_damage_dealt_participant4',
                            'magic_damage_dealt_participant5']].sum(axis=1)

    magic_dmg_team2 = data[['magic_damage_dealt_participant6', 'magic_damage_dealt_participant7',
                            'magic_damage_dealt_participant8', 'magic_damage_dealt_participant9',
                            'magic_damage_dealt_participant10']].sum(axis=1)

    data['magic_dmg_dealt_delta_team1'] = magic_dmg_team1 - magic_dmg_team2
    data['magic_dmg_dealt_delta_team2'] = magic_dmg_team2 - magic_dmg_team1

    # Calculate jungle magic damage dealt deltas for both teams
    data['jg_magic_dmg_dealt_delta_team1'] = data['magic_damage_dealt_participant2'] - \
        data['magic_damage_dealt_participant7']
    data['jg_magic_dmg_dealt_delta_team2'] = data['magic_damage_dealt_participant7'] - \
        data['magic_damage_dealt_participant2']

    # Calculate top magic damage dealt deltas for both teams
    data['top_magic_dmg_dealt_delta_team1'] = data['magic_damage_dealt_participant1'] - \
        data['magic_damage_dealt_participant6']
    data['top_magic_dmg_dealt_delta_team2'] = data['magic_damage_dealt_participant6'] - \
        data['magic_damage_dealt_participant1']

    # Calculate mid magic damage dealt deltas for both teams
    data['mid_magic_dmg_dealt_delta_team1'] = data['magic_damage_dealt_participant3'] - \
        data['magic_damage_dealt_participant8']
    data['mid_magic_dmg_dealt_delta_team2'] = data['magic_damage_dealt_participant8'] - \
        data['magic_damage_dealt_participant3']

    # Calculate ADC magic damage dealt deltas for both teams
    data['adc_magic_dmg_dealt_delta_team1'] = data['magic_damage_dealt_participant4'] - \
        data['magic_damage_dealt_participant9']
    data['adc_magic_dmg_dealt_delta_team2'] = data['magic_damage_dealt_participant9'] - \
        data['magic_damage_dealt_participant4']

    # Calculate physical damage dealt deltas for both teams
    phys_dmg_team1 = data[['phys_damage_dealt_participant1', 'phys_damage_dealt_participant2',
                        'phys_damage_dealt_participant3', 'phys_damage_dealt_participant4',
                        'phys_damage_dealt_participant5']].sum(axis=1)

    phys_dmg_team2 = data[['phys_damage_dealt_participant6', 'phys_damage_dealt_participant7',
                        'phys_damage_dealt_participant8', 'phys_damage_dealt_participant9',
                        'phys_damage_dealt_participant10']].sum(axis=1)

    data['phys_dmg_dealt_delta_team1'] = phys_dmg_team1 - phys_dmg_team2
    data['phys_dmg_dealt_delta_team2'] = phys_dmg_team2 - phys_dmg_team1

    # Calculate jungle physical damage dealt deltas for both teams
    data['jg_phys_dmg_dealt_delta_team1'] = data['phys_damage_dealt_participant2'] - \
        data['phys_damage_dealt_participant7']
    data['jg_phys_dmg_dealt_delta_team2'] = data['phys_damage_dealt_participant7'] - \
        data['phys_damage_dealt_participant2']

    # Calculate top physical damage dealt deltas for both teams
    data['top_phys_dmg_dealt_delta_team1'] = data['phys_damage_dealt_participant1'] - \
        data['phys_damage_dealt_participant6']
    data['top_phys_dmg_dealt_delta_team2'] = data['phys_damage_dealt_participant6'] - \
        data['phys_damage_dealt_participant1']

    # Calculate mid physical damage dealt deltas for both teams
    data['mid_phys_dmg_dealt_delta_team1'] = data['phys_damage_dealt_participant3'] - \
        data['phys_damage_dealt_participant8']
    data['mid_phys_dmg_dealt_delta_team2'] = data['phys_damage_dealt_participant8'] - \
        data['phys_damage_dealt_participant3']

    # Calculate ADC physical damage dealt deltas for both teams
    data['adc_phys_dmg_dealt_delta_team1'] = data['phys_damage_dealt_participant4'] - \
        data['phys_damage_dealt_participant9']
    data['adc_phys_dmg_dealt_delta_team2'] = data['phys_damage_dealt_participant9'] - \
        data['phys_damage_dealt_participant4']

    # Calculate total damage dealt for both teams
    data['total_dmg_dealt_team1'] = (magic_dmg_team1 + phys_dmg_team1)
    data['total_dmg_dealt_team2'] = (magic_dmg_team2 + phys_dmg_team2)

    # Calculate total damage dealt for each role within the teams
    data['top_total_dmg_dealt_team1'] = data['magic_damage_dealt_participant1'] + \
        data['phys_damage_dealt_participant1']
    data['jg_total_dmg_dealt_team1'] = data['magic_damage_dealt_participant2'] + \
        data['phys_damage_dealt_participant2']
    data['mid_total_dmg_dealt_team1'] = data['magic_damage_dealt_participant3'] + \
        data['phys_damage_dealt_participant3']
    data['adc_total_dmg_dealt_team1'] = data['magic_damage_dealt_participant4'] + \
        data['phys_damage_dealt_participant4']
    data['sup_total_dmg_dealt_team1'] = data['magic_damage_dealt_participant5'] + \
        data['phys_damage_dealt_participant5']

    data['top_total_dmg_dealt_team2'] = data['magic_damage_dealt_participant6'] + \
        data['phys_damage_dealt_participant6']
    data['jg_total_dmg_dealt_team2'] = data['magic_damage_dealt_participant7'] + \
        data['phys_damage_dealt_participant7']
    data['mid_total_dmg_dealt_team2'] = data['magic_damage_dealt_participant8'] + \
        data['phys_damage_dealt_participant8']
    data['adc_total_dmg_dealt_team2'] = data['magic_damage_dealt_participant9'] + \
        data['phys_damage_dealt_participant9']
    data['sup_total_dmg_dealt_team2'] = data['magic_damage_dealt_participant10'] + \
        data['phys_damage_dealt_participant10']


    data['top_total_dmg_taken_team1'] = data['phys_damage_taken_participant1'] + data['magic_damage_taken_participant1']
    data['jg_total_dmg_taken_team1'] = data['phys_damage_taken_participant2'] + data['magic_damage_taken_participant2']
    data['mid_total_dmg_taken_team1'] = data['phys_damage_taken_participant3'] + data['magic_damage_taken_participant3']
    data['adc_total_dmg_taken_team1'] = data['phys_damage_taken_participant4'] + data['magic_damage_taken_participant4']
    data['sup_total_dmg_taken_team1'] = data['phys_damage_taken_participant5'] + data['magic_damage_taken_participant5']

    data['top_total_dmg_taken_team2'] = data['phys_damage_taken_participant6'] + data['magic_damage_taken_participant6']
    data['jg_total_dmg_taken_team2'] = data['phys_damage_taken_participant7'] + data['magic_damage_taken_participant7']
    data['mid_total_dmg_taken_team2'] = data['phys_damage_taken_participant8'] + data['magic_damage_taken_participant8']
    data['adc_total_dmg_taken_team2'] = data['phys_damage_taken_participant9'] + data['magic_damage_taken_participant9']
    data['sup_total_dmg_taken_team2'] = data['phys_damage_taken_participant10'] + data['magic_damage_taken_participant10']

    # Calculate total damage dealt deltas for both teams
    data['total_dmg_dealt_delta_team1'] = data['total_dmg_dealt_team1'] - \
        data['total_dmg_dealt_team2']
    data['total_dmg_dealt_delta_team2'] = data['total_dmg_dealt_team2'] - \
        data['total_dmg_dealt_team1']


    # Calculate top total damage dealt deltas for both teams
    data['top_total_dmg_dealt_delta_team1'] = data['top_total_dmg_dealt_team1'] - \
        data['top_total_dmg_dealt_team2']
    data['top_total_dmg_dealt_delta_team2'] = data['top_total_dmg_dealt_team2'] - \
        data['top_total_dmg_dealt_team1']

    # Calculate jungle total damage dealt deltas for both teams
    data['jg_total_dmg_dealt_delta_team1'] = data['jg_total_dmg_dealt_team1'] - \
        data['jg_total_dmg_dealt_team2']
    data['jg_total_dmg_dealt_delta_team2'] = data['jg_total_dmg_dealt_team2'] - \
        data['jg_total_dmg_dealt_team1']

    # Calculate mid total damage dealt deltas for both teams
    data['mid_total_dmg_dealt_delta_team1'] = data['mid_total_dmg_dealt_team1'] - \
        data['mid_total_dmg_dealt_team2']
    data['mid_total_dmg_dealt_delta_team2'] = data['mid_total_dmg_dealt_team2'] - \
        data['mid_total_dmg_dealt_team1']

    # Calculate ADC total damage dealt deltas for both teams
    data['adc_total_dmg_dealt_delta_team1'] = data['adc_total_dmg_dealt_team1'] - \
        data['adc_total_dmg_dealt_team2']
    data['adc_total_dmg_dealt_delta_team2'] = data['adc_total_dmg_dealt_team2'] - \
        data['adc_total_dmg_dealt_team1']

    # Calculate total damage taken for both teams
    data['total_dmg_taken_team1'] = (
        data['phys_damage_taken_participant1'] + data['phys_damage_taken_participant2'] +
        data['phys_damage_taken_participant3'] + data['phys_damage_taken_participant4'] +
        data['phys_damage_taken_participant5'] + data['magic_damage_taken_participant1'] +
        data['magic_damage_taken_participant2'] + data['magic_damage_taken_participant3'] +
        data['magic_damage_taken_participant4'] +
        data['magic_damage_taken_participant5']
    )

    data['total_dmg_taken_team2'] = (
        data['phys_damage_taken_participant6'] + data['phys_damage_taken_participant7'] +
        data['phys_damage_taken_participant8'] + data['phys_damage_taken_participant9'] +
        data['phys_damage_taken_participant10'] + data['magic_damage_taken_participant6'] +
        data['magic_damage_taken_participant7'] + data['magic_damage_taken_participant8'] +
        data['magic_damage_taken_participant9'] +
        data['magic_damage_taken_participant10']
    )

    # Calculate top total damage taken deltas for both teams
    data['top_total_dmg_taken_delta_team1'] = data['top_total_dmg_taken_team1'] - \
        data['top_total_dmg_taken_team2']
    data['top_total_dmg_taken_delta_team2'] = data['top_total_dmg_taken_team2'] - \
        data['top_total_dmg_taken_team1']

    # Calculate jungle total damage taken deltas for both teams
    data['jg_total_dmg_taken_delta_team1'] = data['jg_total_dmg_taken_team1'] - \
        data['jg_total_dmg_taken_team2']
    data['jg_total_dmg_taken_delta_team2'] = data['jg_total_dmg_taken_team2'] - \
        data['jg_total_dmg_taken_team1']

    # Calculate mid total damage taken deltas for both teams
    data['mid_total_dmg_taken_delta_team1'] = data['mid_total_dmg_taken_team1'] - \
        data['mid_total_dmg_taken_team2']
    data['mid_total_dmg_taken_delta_team2'] = data['mid_total_dmg_taken_team2'] - \
        data['mid_total_dmg_taken_team1']

    # Calculate ADC total damage taken deltas for both teams
    data['adc_total_dmg_taken_delta_team1'] = data['adc_total_dmg_taken_team1'] - \
        data['adc_total_dmg_taken_team2']
    data['adc_total_dmg_taken_delta_team2'] = data['adc_total_dmg_taken_team2'] - \
        data['adc_total_dmg_taken_team1']

    # Calculate support wards killed per death deltas for both teams
    data['support_wards_killed_per_death_team1'] = data['team1_support_wards_killed'] / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)
    data['support_wards_killed_per_death_team2'] = data['team2_support_wards_killed'] / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)
    data['support_wards_killed_per_death_delta_team1'] = data['support_wards_killed_per_death_team1'] - \
        data['support_wards_killed_per_death_team2']
    data['support_wards_killed_per_death_delta_team2'] = data['support_wards_killed_per_death_team2'] - \
        data['support_wards_killed_per_death_team1']

    # Calculate jungle wards killed per death deltas for both teams
    data['jg_wards_killed_per_death_team1'] = data['team1_jungle_wards_killed'] / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['jg_wards_killed_per_death_team2'] = data['team2_jungle_wards_killed'] / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['jg_wards_killed_per_death_delta_team1'] = data['jg_wards_killed_per_death_team1'] - \
        data['jg_wards_killed_per_death_team2']
    data['jg_wards_killed_per_death_delta_team2'] = data['jg_wards_killed_per_death_team2'] - \
        data['jg_wards_killed_per_death_team1']

    # Calculate support wards placed per death deltas for both teams
    data['support_wards_placed_per_death_team1'] = data['ward_placed_participant5'] / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)
    data['support_wards_placed_per_death_team2'] = data['ward_placed_participant10'] / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)
    data['support_wards_placed_per_death_delta_team1'] = data['support_wards_placed_per_death_team1'] - \
        data['support_wards_placed_per_death_team2']
    data['support_wards_placed_per_death_delta_team2'] = data['support_wards_placed_per_death_team2'] - \
        data['support_wards_placed_per_death_team1']

    # Calculate jungle wards placed per death deltas for both teams
    data['jg_wards_placed_per_death_team1'] = data['ward_placed_participant2'] / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['jg_wards_placed_per_death_team2'] = data['ward_placed_participant7'] / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['jg_wards_placed_per_death_delta_team1'] = data['jg_wards_placed_per_death_team1'] - \
        data['jg_wards_placed_per_death_team2']
    data['jg_wards_placed_per_death_delta_team2'] = data['jg_wards_placed_per_death_team2'] - \
        data['jg_wards_placed_per_death_team1']

    # Calculate top total damage dealt per death for both teams
    data['top_total_dmg_dealt_per_death_team1'] = data['top_total_dmg_dealt_team1'] / \
        data['deaths_participant1'].apply(lambda x: 1 if x == 0 else x)
    data['top_total_dmg_dealt_per_death_team2'] = data['top_total_dmg_dealt_team2'] / \
        data['deaths_participant6'].apply(lambda x: 1 if x == 0 else x)
    data['top_total_dmg_dealt_per_death_delta_team1'] = data['top_total_dmg_dealt_per_death_team1'] - \
        data['top_total_dmg_dealt_per_death_team2']
    data['top_total_dmg_dealt_per_death_delta_team2'] = data['top_total_dmg_dealt_per_death_team2'] - \
        data['top_total_dmg_dealt_per_death_team1']

    # Calculate jungle total damage dealt per death for both teams
    data['jg_total_dmg_dealt_per_death_team1'] = data['jg_total_dmg_dealt_team1'] / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_dealt_per_death_team2'] = data['jg_total_dmg_dealt_team2'] / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_dealt_per_death_delta_team1'] = data['jg_total_dmg_dealt_per_death_team1'] - \
        data['jg_total_dmg_dealt_per_death_team2']
    data['jg_total_dmg_dealt_per_death_delta_team2'] = data['jg_total_dmg_dealt_per_death_team2'] - \
        data['jg_total_dmg_dealt_per_death_team1']

    # Calculate mid total damage dealt per death for both teams
    data['mid_total_dmg_dealt_per_death_team1'] = data['mid_total_dmg_dealt_team1'] / \
        data['deaths_participant3'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_dealt_per_death_team2'] = data['mid_total_dmg_dealt_team2'] / \
        data['deaths_participant8'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_dealt_per_death_delta_team1'] = data['mid_total_dmg_dealt_per_death_team1'] - \
        data['mid_total_dmg_dealt_per_death_team2']
    data['mid_total_dmg_dealt_per_death_delta_team2'] = data['mid_total_dmg_dealt_per_death_team2'] - \
        data['mid_total_dmg_dealt_per_death_team1']

    # Calculate ADC total damage dealt per death for both teams
    data['adc_total_dmg_dealt_per_death_team1'] = data['adc_total_dmg_dealt_team1'] / \
        data['deaths_participant4'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_dealt_per_death_team2'] = data['adc_total_dmg_dealt_team2'] / \
        data['deaths_participant9'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_dealt_per_death_delta_team1'] = data['adc_total_dmg_dealt_per_death_team1'] - \
        data['adc_total_dmg_dealt_per_death_team2']
    data['adc_total_dmg_dealt_per_death_delta_team2'] = data['adc_total_dmg_dealt_per_death_team2'] - \
        data['adc_total_dmg_dealt_per_death_team1']

    # Calculate support total damage dealt per death for both teams
    data['sup_total_dmg_dealt_per_death_team1'] = data['sup_total_dmg_dealt_team1'] / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_dealt_per_death_team2'] = data['sup_total_dmg_dealt_team2'] / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_dealt_per_death_delta_team1'] = data['sup_total_dmg_dealt_per_death_team1'] - \
        data['sup_total_dmg_dealt_per_death_team2']
    data['sup_total_dmg_dealt_per_death_delta_team2'] = data['sup_total_dmg_dealt_per_death_team2'] - \
        data['sup_total_dmg_dealt_per_death_team1']

    # Total damage taken per death
    data['top_total_dmg_taken_per_death_team1'] = data['top_total_dmg_taken_team1'] / \
        data['deaths_participant1'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_taken_per_death_team1'] = data['jg_total_dmg_taken_team1'] / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_taken_per_death_team1'] = data['mid_total_dmg_taken_team1'] / \
        data['deaths_participant3'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_taken_per_death_team1'] = data['adc_total_dmg_taken_team1'] / \
        data['deaths_participant4'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_taken_per_death_team1'] = data['sup_total_dmg_taken_team1'] / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)

    data['top_total_dmg_taken_per_death_team2'] = data['top_total_dmg_taken_team2'] / \
        data['deaths_participant6'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_taken_per_death_team2'] = data['jg_total_dmg_taken_team2'] / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_taken_per_death_team2'] = data['mid_total_dmg_taken_team2'] / \
        data['deaths_participant8'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_taken_per_death_team2'] = data['adc_total_dmg_taken_team2'] / \
        data['deaths_participant9'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_taken_per_death_team2'] = data['sup_total_dmg_taken_team2'] / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)

    data['top_total_dmg_taken_per_death_delta_team1'] = data['top_total_dmg_taken_per_death_team1'] - \
        data['top_total_dmg_taken_per_death_team2']
    data['top_total_dmg_taken_per_death_delta_team2'] = data['top_total_dmg_taken_per_death_team2'] - \
        data['top_total_dmg_taken_per_death_team1']

    data['jg_total_dmg_taken_per_death_delta_team1'] = data['jg_total_dmg_taken_per_death_team1'] - \
        data['jg_total_dmg_taken_per_death_team2']
    data['jg_total_dmg_taken_per_death_delta_team2'] = data['jg_total_dmg_taken_per_death_team2'] - \
        data['jg_total_dmg_taken_per_death_team1']

    data['mid_total_dmg_taken_per_death_delta_team1'] = data['mid_total_dmg_taken_per_death_team1'] - \
        data['mid_total_dmg_taken_per_death_team2']
    data['mid_total_dmg_taken_per_death_delta_team2'] = data['mid_total_dmg_taken_per_death_team2'] - \
        data['mid_total_dmg_taken_per_death_team1']

    data['adc_total_dmg_taken_per_death_delta_team1'] = data['adc_total_dmg_taken_per_death_team1'] - \
        data['adc_total_dmg_taken_per_death_team2']
    data['adc_total_dmg_taken_per_death_delta_team2'] = data['adc_total_dmg_taken_per_death_team2'] - \
        data['adc_total_dmg_taken_per_death_team1']

    data['sup_total_dmg_taken_per_death_delta_team1'] = data['sup_total_dmg_taken_per_death_team1'] - \
        data['sup_total_dmg_taken_per_death_team2']
    data['sup_total_dmg_taken_per_death_delta_team2'] = data['sup_total_dmg_taken_per_death_team2'] - \
        data['sup_total_dmg_taken_per_death_team1']

    # Total damage dealt per kill
    data['top_total_dmg_dealt_per_kill_team1'] = data['top_total_dmg_dealt_team1'] / \
        data['kills_participant1'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_dealt_per_kill_team1'] = data['jg_total_dmg_dealt_team1'] / \
        data['kills_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_dealt_per_kill_team1'] = data['mid_total_dmg_dealt_team1'] / \
        data['kills_participant3'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_dealt_per_kill_team1'] = data['adc_total_dmg_dealt_team1'] / \
        data['kills_participant4'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_dealt_per_kill_team1'] = data['sup_total_dmg_dealt_team1'] / \
        data['kills_participant5'].apply(lambda x: 1 if x == 0 else x)

    data['top_total_dmg_dealt_per_kill_team2'] = data['top_total_dmg_dealt_team2'] / \
        data['kills_participant6'].apply(lambda x: 1 if x == 0 else x)
    data['jg_total_dmg_dealt_per_kill_team2'] = data['jg_total_dmg_dealt_team2'] / \
        data['kills_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['mid_total_dmg_dealt_per_kill_team2'] = data['mid_total_dmg_dealt_team2'] / \
        data['kills_participant8'].apply(lambda x: 1 if x == 0 else x)
    data['adc_total_dmg_dealt_per_kill_team2'] = data['adc_total_dmg_dealt_team2'] / \
        data['kills_participant9'].apply(lambda x: 1 if x == 0 else x)
    data['sup_total_dmg_dealt_per_kill_team2'] = data['sup_total_dmg_dealt_team2'] / \
        data['kills_participant10'].apply(lambda x: 1 if x == 0 else x)

    data['top_total_dmg_dealt_per_kill_delta_team1'] = data['top_total_dmg_dealt_per_kill_team1'] - \
        data['top_total_dmg_dealt_per_kill_team2']
    data['top_total_dmg_dealt_per_kill_delta_team2'] = data['top_total_dmg_dealt_per_kill_team2'] - \
        data['top_total_dmg_dealt_per_kill_team1']

    data['jg_total_dmg_dealt_per_kill_delta_team1'] = data['jg_total_dmg_dealt_per_kill_team1'] - \
        data['jg_total_dmg_dealt_per_kill_team2']
    data['jg_total_dmg_dealt_per_kill_delta_team2'] = data['jg_total_dmg_dealt_per_kill_team2'] - \
        data['jg_total_dmg_dealt_per_kill_team1']

    data['mid_total_dmg_dealt_per_kill_delta_team1'] = data['mid_total_dmg_dealt_per_kill_team1'] - \
        data['mid_total_dmg_dealt_per_kill_team2']
    data['mid_total_dmg_dealt_per_kill_delta_team2'] = data['mid_total_dmg_dealt_per_kill_team2'] - \
        data['mid_total_dmg_dealt_per_kill_team1']

    data['adc_total_dmg_dealt_per_kill_delta_team1'] = data['adc_total_dmg_dealt_per_kill_team1'] - \
        data['adc_total_dmg_dealt_per_kill_team2']
    data['adc_total_dmg_dealt_per_kill_delta_team2'] = data['adc_total_dmg_dealt_per_kill_team2'] - \
        data['adc_total_dmg_dealt_per_kill_team1']

    data['sup_total_dmg_dealt_per_kill_delta_team1'] = data['sup_total_dmg_dealt_per_kill_team1'] - \
        data['sup_total_dmg_dealt_per_kill_team2']
    data['sup_total_dmg_dealt_per_kill_delta_team2'] = data['sup_total_dmg_dealt_per_kill_team2'] - \
        data['sup_total_dmg_dealt_per_kill_team1']

    # KDA per participant + delta
    data['top_kda_team1'] = (data['kills_participant1'] + data['assists_participant1']) / \
        data['deaths_participant1'].apply(lambda x: 1 if x == 0 else x)
    data['jg_kda_team1'] = (data['kills_participant2'] + data['assists_participant2']) / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['mid_kda_team1'] = (data['kills_participant3'] + data['assists_participant3']) / \
        data['deaths_participant3'].apply(lambda x: 1 if x == 0 else x)
    data['adc_kda_team1'] = (data['kills_participant4'] + data['assists_participant4']) / \
        data['deaths_participant4'].apply(lambda x: 1 if x == 0 else x)
    data['sup_kda_team1'] = (data['kills_participant5'] + data['assists_participant5']) / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)

    data['top_kda_team2'] = (data['kills_participant6'] + data['assists_participant6']) / \
        data['deaths_participant6'].apply(lambda x: 1 if x == 0 else x)
    data['jg_kda_team2'] = (data['kills_participant7'] + data['assists_participant7']) / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['mid_kda_team2'] = (data['kills_participant8'] + data['assists_participant8']) / \
        data['deaths_participant8'].apply(lambda x: 1 if x == 0 else x)
    data['adc_kda_team2'] = (data['kills_participant9'] + data['assists_participant9']) / \
        data['deaths_participant9'].apply(lambda x: 1 if x == 0 else x)
    data['sup_kda_team2'] = (data['kills_participant10'] + data['assists_participant10']) / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)

    data['top_kda_delta_team1'] = data['top_kda_team1'] - data['top_kda_team2']
    data['top_kda_delta_team2'] = data['top_kda_team2'] - data['top_kda_team1']

    data['jg_kda_delta_team1'] = data['jg_kda_team1'] - data['jg_kda_team2']
    data['jg_kda_delta_team2'] = data['jg_kda_team2'] - data['jg_kda_team1']

    data['mid_kda_delta_team1'] = data['mid_kda_team1'] - data['mid_kda_team2']
    data['mid_kda_delta_team2'] = data['mid_kda_team2'] - data['mid_kda_team1']

    data['adc_kda_delta_team1'] = data['adc_kda_team1'] - data['adc_kda_team2']
    data['adc_kda_delta_team2'] = data['adc_kda_team2'] - data['adc_kda_team1']

    data['sup_kda_delta_team1'] = data['sup_kda_team1'] - data['sup_kda_team2']
    data['sup_kda_delta_team2'] = data['sup_kda_team2'] - data['sup_kda_team1']

    # Kill+assists per ward placed
    data['kill_assists_per_ward_placed_team1'] = data.apply(lambda row: (row['t100_kills'] + row['t100_assists'])
                                                             / (1 if row['wards_placed_team1'] == 0 else row['wards_placed_team1']), axis=1)
    data['kill_assists_per_ward_placed_team2'] = data.apply(lambda row: (row['t200_kills'] + row['t200_assists'])
                                                             / (1 if row['wards_placed_team2'] == 0 else row['wards_placed_team2']), axis=1)

    data['kill_assists_per_ward_placed_delta_team1'] = data['kill_assists_per_ward_placed_team1'] - \
        data['kill_assists_per_ward_placed_team2']
    data['kill_assists_per_ward_placed_delta_team2'] = data['kill_assists_per_ward_placed_team2'] - \
        data['kill_assists_per_ward_placed_team1']

    # Kill+assists per cc scored
    data['kill_assists_per_cc_time_team1'] = (
        data['t100_kills'] + data['t100_assists']) / data['cc_team1']
    data['kill_assists_per_cc_time_team2'] = (
        data['t200_kills'] + data['t200_assists']) / data['cc_team2']

    data['kill_assists_per_cc_time_delta_team1'] = data['kill_assists_per_cc_time_team1'] - \
        data['kill_assists_per_cc_time_team2']
    data['kill_assists_per_cc_time_delta_team2'] = data['kill_assists_per_cc_time_team2'] - \
        data['kill_assists_per_cc_time_team1']

    # Kill for adc or mid per team cc scored
    data['adc_kill_assists_per_cc_time_team1'] = (
        data['kills_participant4'] + data['assists_participant4']) / data['cc_team1']
    data['adc_kill_per_cc_time_team1'] = data['kills_participant4'] / data['cc_team1']
    data['mid_kill_assists_per_cc_time_team1'] = (
        data['kills_participant3'] + data['assists_participant3']) / data['cc_team1']
    data['mid_kill_per_cc_time_team1'] = data['kills_participant3'] / data['cc_team1']

    data['adc_kill_assists_per_cc_time_team2'] = (
        data['kills_participant9'] + data['assists_participant9']) / data['cc_team2']
    data['adc_kill_per_cc_time_team2'] = data['kills_participant9'] / data['cc_team2']
    data['mid_kill_assists_per_cc_time_team2'] = (
        data['kills_participant8'] + data['assists_participant8']) / data['cc_team2']
    data['mid_kill_per_cc_time_team2'] = data['kills_participant8'] / data['cc_team2']

    data['adc_kill_assists_per_cc_time_delta_team1'] = data['adc_kill_assists_per_cc_time_team1'] - \
        data['adc_kill_assists_per_cc_time_team2']
    data['adc_kill_per_cc_time_delta_team1'] = data['adc_kill_per_cc_time_team1'] - \
        data['adc_kill_per_cc_time_team2']
    data['mid_kill_assists_per_cc_time_delta_team1'] = data['mid_kill_assists_per_cc_time_team1'] - \
        data['mid_kill_assists_per_cc_time_team2']
    data['mid_kill_per_cc_time_delta_team1'] = data['mid_kill_per_cc_time_team1'] - \
        data['mid_kill_per_cc_time_team2']

    data['adc_kill_assists_per_cc_time_delta_team2'] = data['adc_kill_assists_per_cc_time_team2'] - \
        data['adc_kill_assists_per_cc_time_team1']
    data['adc_kill_per_cc_time_delta_team2'] = data['adc_kill_per_cc_time_team2'] - \
        data['adc_kill_per_cc_time_team1']
    data['mid_kill_assists_per_cc_time_delta_team2'] = data['mid_kill_assists_per_cc_time_team2'] - \
        data['mid_kill_assists_per_cc_time_team1']
    data['mid_kill_per_cc_time_delta_team2'] = data['mid_kill_per_cc_time_team2'] - \
        data['mid_kill_per_cc_time_team1']

    # Minions killed delta
    data['minions_killed_team1'] = (
        data['minions_killed_participant1'] +
        data['minions_killed_participant2'] +
        data['minions_killed_participant3'] +
        data['minions_killed_participant4'] +
        data['minions_killed_participant5']
    )

    data['minions_killed_team2'] = (
        data['minions_killed_participant6'] +
        data['minions_killed_participant7'] +
        data['minions_killed_participant8'] +
        data['minions_killed_participant9'] +
        data['minions_killed_participant10']
    )

    data['minions_killed_delta_team1'] = data['minions_killed_team1'] - data['minions_killed_team2']
    data['minions_killed_delta_team2'] = data['minions_killed_team2'] - data['minions_killed_team1']

    data['top_minions_killed_delta_team1'] = data['minions_killed_participant1'] - \
        data['minions_killed_participant6']
    data['jg_minions_killed_delta_team1'] = data['minions_killed_participant2'] - \
        data['minions_killed_participant7']
    data['mid_minions_killed_delta_team1'] = data['minions_killed_participant3'] - \
        data['minions_killed_participant8']
    data['adc_minions_killed_delta_team1'] = data['minions_killed_participant4'] - \
        data['minions_killed_participant9']
    data['sup_minions_killed_delta_team1'] = data['minions_killed_participant5'] - \
        data['minions_killed_participant10']
    
    data['top_minions_killed_delta_team2'] = - data['minions_killed_participant1'] + \
        data['minions_killed_participant6']
    data['jg_minions_killed_delta_team2'] = - data['minions_killed_participant2'] + \
        data['minions_killed_participant7']
    data['mid_minions_killed_delta_team2'] = -  data['minions_killed_participant3'] + \
        data['minions_killed_participant8']
    data['adc_minions_killed_delta_team2'] = - data['minions_killed_participant4'] + \
        data['minions_killed_participant9']
    data['sup_minions_killed_delta_team2'] = - data['minions_killed_participant5'] + \
        data['minions_killed_participant10']

    # Minions killed per death
    data['top_minions_killed_per_death_team1'] = data['minions_killed_participant1'] / \
        data['deaths_participant1'].apply(lambda x: 1 if x == 0 else x)
    data['jg_minions_killed_per_death_team1'] = data['minions_killed_participant2'] / \
        data['deaths_participant2'].apply(lambda x: 1 if x == 0 else x)
    data['mid_minions_killed_per_death_team1'] = data['minions_killed_participant3'] / \
        data['deaths_participant3'].apply(lambda x: 1 if x == 0 else x)
    data['adc_minions_killed_per_death_team1'] = data['minions_killed_participant4'] / \
        data['deaths_participant4'].apply(lambda x: 1 if x == 0 else x)
    data['sup_minions_killed_per_death_team1'] = data['minions_killed_participant5'] / \
        data['deaths_participant5'].apply(lambda x: 1 if x == 0 else x)

    data['top_minions_killed_per_death_team2'] = data['minions_killed_participant6'] / \
        data['deaths_participant6'].apply(lambda x: 1 if x == 0 else x)
    data['jg_minions_killed_per_death_team2'] = data['minions_killed_participant7'] / \
        data['deaths_participant7'].apply(lambda x: 1 if x == 0 else x)
    data['mid_minions_killed_per_death_team2'] = data['minions_killed_participant8'] / \
        data['deaths_participant8'].apply(lambda x: 1 if x == 0 else x)
    data['adc_minions_killed_per_death_team2'] = data['minions_killed_participant9'] / \
        data['deaths_participant9'].apply(lambda x: 1 if x == 0 else x)
    data['sup_minions_killed_per_death_team2'] = data['minions_killed_participant10'] / \
        data['deaths_participant10'].apply(lambda x: 1 if x == 0 else x)

    data['top_minions_killed_per_death_delta_team1'] = data['top_minions_killed_per_death_team1'] - \
        data['top_minions_killed_per_death_team2']
    data['jg_minions_killed_per_death_delta_team1'] = data['jg_minions_killed_per_death_team1'] - \
        data['jg_minions_killed_per_death_team2']
    data['mid_minions_killed_per_death_delta_team1'] = data['mid_minions_killed_per_death_team1'] - \
        data['mid_minions_killed_per_death_team2']
    data['adc_minions_killed_per_death_delta_team1'] = data['adc_minions_killed_per_death_team1'] - \
        data['adc_minions_killed_per_death_team2']
    data['sup_minions_killed_per_death_delta_team1'] = data['sup_minions_killed_per_death_team1'] - \
        data['sup_minions_killed_per_death_team2']
    
    data['top_minions_killed_per_death_delta_team2'] = data['top_minions_killed_per_death_team2'] - \
        data['top_minions_killed_per_death_team1']
    data['jg_minions_killed_per_death_delta_team2'] = data['jg_minions_killed_per_death_team2'] - \
        data['jg_minions_killed_per_death_team1']
    data['mid_minions_killed_per_death_delta_team2'] = data['mid_minions_killed_per_death_team2'] - \
        data['mid_minions_killed_per_death_team1']
    data['adc_minions_killed_per_death_delta_team2'] = data['adc_minions_killed_per_death_team2'] - \
        data['adc_minions_killed_per_death_team1']
    data['sup_minions_killed_per_death_delta_team2'] = data['sup_minions_killed_per_death_team2'] - \
        data['sup_minions_killed_per_death_team1']

    data['minions_killed_per_death_team1'] = (
        data['top_minions_killed_per_death_team1'] +
        data['jg_minions_killed_per_death_team1'] +
        data['mid_minions_killed_per_death_team1'] +
        data['adc_minions_killed_per_death_team1'] +
        data['sup_minions_killed_per_death_team1']
    )

    data['minions_killed_per_death_team2'] = (
        data['top_minions_killed_per_death_team2'] +
        data['jg_minions_killed_per_death_team2'] +
        data['mid_minions_killed_per_death_team2'] +
        data['adc_minions_killed_per_death_team2'] +
        data['sup_minions_killed_per_death_team2']
    )

    data['minions_killed_per_death_delta_team1'] = (
        data['minions_killed_per_death_team1'] -
        data['minions_killed_per_death_team2']
    )

    data['minions_killed_per_death_delta_team2'] = (
        data['minions_killed_per_death_team2'] -
        data['minions_killed_per_death_team1']
    )


    # Kill pct
    data['adc_kill_pct_team1'] = (data['kills_participant4'] / np.where(data['t100_kills'] == 0, 1, data['t100_kills'])) * 100
    data['adc_kill_pct_team2'] = (data['kills_participant9'] / np.where(data['t200_kills'] == 0, 1, data['t200_kills'])) * 100

    data['top_kill_pct_team1'] = (data['kills_participant1'] / np.where(data['t100_kills'] == 0, 1, data['t100_kills'])) * 100
    data['top_kill_pct_team2'] = (data['kills_participant6'] / np.where(data['t200_kills'] == 0, 1, data['t200_kills'])) * 100

    data['mid_kill_pct_team1'] = (data['kills_participant3'] / np.where(data['t100_kills'] == 0, 1, data['t100_kills'])) * 100
    data['mid_kill_pct_team2'] = (data['kills_participant8'] / np.where(data['t200_kills'] == 0, 1, data['t200_kills'])) * 100

    data['main_carries_kill_pct_team1'] = ((data['kills_participant4'] + data['kills_participant3']) / np.where(data['t100_kills'] == 0, 1, data['t100_kills'])) * 100
    data['main_carries_kill_pct_team2'] = ((data['kills_participant9'] + data['kills_participant8']) / np.where(data['t200_kills'] == 0, 1, data['t200_kills'])) * 100

    # Kill pct deltas
    data['adc_kill_pct_delta_team1'] = data['adc_kill_pct_team1'] - data['adc_kill_pct_team2']
    data['adc_kill_pct_delta_team2'] = data['adc_kill_pct_team2'] - data['adc_kill_pct_team1']
    data['top_kill_pct_delta_team1'] = data['top_kill_pct_team1'] - data['top_kill_pct_team2']
    data['top_kill_pct_delta_team2'] = data['top_kill_pct_team2'] - data['top_kill_pct_team1']
    data['mid_kill_pct_delta_team1'] = data['mid_kill_pct_team1'] - data['mid_kill_pct_team2']
    data['mid_kill_pct_delta_team2'] = data['mid_kill_pct_team2'] - data['mid_kill_pct_team1']
    data['main_carries_kill_pct_delta_team1'] = data['main_carries_kill_pct_team1'] - data['main_carries_kill_pct_team2']
    data['main_carries_kill_pct_delta_team2'] = data['main_carries_kill_pct_team2'] - data['main_carries_kill_pct_team1']

    # Damage pct
    data['adc_dmg_pct_team1'] = (data['adc_total_dmg_dealt_team1'] / np.where(data['total_dmg_dealt_team1'] == 0, 1, data['total_dmg_dealt_team1'])) * 100
    data['adc_dmg_pct_team2'] = (data['adc_total_dmg_dealt_team2'] / np.where(data['total_dmg_dealt_team2'] == 0, 1, data['total_dmg_dealt_team2'])) * 100

    data['mid_dmg_pct_team1'] = (data['mid_total_dmg_dealt_team1'] / np.where(data['total_dmg_dealt_team1'] == 0, 1, data['total_dmg_dealt_team1'])) * 100
    data['mid_dmg_pct_team2'] = (data['mid_total_dmg_dealt_team2'] / np.where(data['total_dmg_dealt_team2'] == 0, 1, data['total_dmg_dealt_team2'])) * 100

    data['top_dmg_pct_team1'] = (data['top_total_dmg_dealt_team1'] / np.where(data['total_dmg_dealt_team1'] == 0, 1, data['total_dmg_dealt_team1'])) * 100
    data['top_dmg_pct_team2'] = (data['top_total_dmg_dealt_team2'] / np.where(data['total_dmg_dealt_team2'] == 0, 1, data['total_dmg_dealt_team2'])) * 100

    data['adc_dmg_pct_delta_team1'] = data['adc_dmg_pct_team1'] - data['adc_dmg_pct_team2']
    data['adc_dmg_pct_delta_team2'] = data['adc_dmg_pct_team2'] - data['adc_dmg_pct_team1']

    data['mid_dmg_pct_delta_team1'] = data['mid_dmg_pct_team1'] - data['mid_dmg_pct_team2']
    data['mid_dmg_pct_delta_team2'] = data['mid_dmg_pct_team2'] - data['mid_dmg_pct_team1']

    data['top_dmg_pct_delta_team1'] = data['top_dmg_pct_team1'] - data['top_dmg_pct_team2']
    data['top_dmg_pct_delta_team2'] = data['top_dmg_pct_team2'] - data['top_dmg_pct_team1']

    # Damage Taken pct
    data['adc_dmg_taken_pct_team1'] = (data['adc_total_dmg_taken_team1'] / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['adc_dmg_taken_pct_team2'] = (data['adc_total_dmg_taken_team2'] / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['mid_dmg_taken_pct_team1'] = (data['mid_total_dmg_taken_team1'] / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['mid_dmg_taken_pct_team2'] = (data['mid_total_dmg_taken_team2'] / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['top_dmg_taken_pct_team1'] = (data['top_total_dmg_taken_team1'] / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['top_dmg_taken_pct_team2'] = (data['top_total_dmg_taken_team2'] / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['jg_dmg_taken_pct_team1'] = (data['jg_total_dmg_taken_team1'] / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['jg_dmg_taken_pct_team2'] = (data['jg_total_dmg_taken_team2'] / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['sup_dmg_taken_pct_team1'] = (data['sup_total_dmg_taken_team1'] / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['sup_dmg_taken_pct_team2'] = (data['sup_total_dmg_taken_team2'] / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['noncarries_dmg_taken_pct_team1'] = ((data['sup_total_dmg_taken_team1'] + data['top_total_dmg_taken_team1'] + data['jg_total_dmg_taken_team1']) / np.where(data['total_dmg_taken_team1'] == 0, 1, data['total_dmg_taken_team1'])) * 100
    data['noncarries_dmg_taken_pct_team2'] = ((data['sup_total_dmg_taken_team2'] + data['top_total_dmg_taken_team2'] + data['jg_total_dmg_taken_team2']) / np.where(data['total_dmg_taken_team2'] == 0, 1, data['total_dmg_taken_team2'])) * 100

    data['adc_dmg_taken_pct_delta_team1'] = data['adc_dmg_taken_pct_team1'] - data['adc_dmg_taken_pct_team2']
    data['adc_dmg_taken_pct_delta_team2'] = data['adc_dmg_taken_pct_team2'] - data['adc_dmg_taken_pct_team1']

    data['mid_dmg_taken_pct_delta_team1'] = data['mid_dmg_taken_pct_team1'] - data['mid_dmg_taken_pct_team2']
    data['mid_dmg_taken_pct_delta_team2'] = data['mid_dmg_taken_pct_team2'] - data['mid_dmg_taken_pct_team1']

    data['top_dmg_taken_pct_delta_team1'] = data['top_dmg_taken_pct_team1'] - data['top_dmg_taken_pct_team2']
    data['top_dmg_taken_pct_delta_team2'] = data['top_dmg_taken_pct_team2'] - data['top_dmg_taken_pct_team1']

    data['jg_dmg_taken_pct_delta_team1'] = data['jg_dmg_taken_pct_team1'] - data['jg_dmg_taken_pct_team2']
    data['jg_dmg_taken_pct_delta_team2'] = data['jg_dmg_taken_pct_team2'] - data['jg_dmg_taken_pct_team1']

    data['sup_dmg_taken_pct_delta_team1'] = data['sup_dmg_taken_pct_team1'] - data['sup_dmg_taken_pct_team2']
    data['sup_dmg_taken_pct_delta_team2'] = data['sup_dmg_taken_pct_team2'] - data['sup_dmg_taken_pct_team1']

    data['noncarries_dmg_taken_pct_delta_team1'] = data['noncarries_dmg_taken_pct_team1'] - data['noncarries_dmg_taken_pct_team2']
    data['noncarries_dmg_taken_pct_delta_team2'] = data['noncarries_dmg_taken_pct_team2'] - data['noncarries_dmg_taken_pct_team1']
    
    data['adc_death_participation_team1'] = (data['deaths_participant4'] / data['t100_deaths'].replace(0, 1)) * 100
    data['top_death_participation_team1'] = (data['deaths_participant1'] / data['t100_deaths'].replace(0, 1)) * 100
    data['jg_death_participation_team1'] = (data['deaths_participant2'] / data['t100_deaths'].replace(0, 1)) * 100
    data['mid_death_participation_team1'] = (data['deaths_participant3'] / data['t100_deaths'].replace(0, 1)) * 100
    data['sup_death_participation_team1'] = (data['deaths_participant5'] / data['t100_deaths'].replace(0, 1)) * 100

    data['adc_death_participation_team2'] = (data['deaths_participant9'] / data['t200_deaths'].replace(0, 1)) * 100
    data['top_death_participation_team2'] = (data['deaths_participant6'] / data['t200_deaths'].replace(0, 1)) * 100
    data['jg_death_participation_team2'] = (data['deaths_participant7'] / data['t200_deaths'].replace(0, 1)) * 100
    data['mid_death_participation_team2'] = (data['deaths_participant8'] / data['t200_deaths'].replace(0, 1)) * 100
    data['sup_death_participation_team2'] = (data['deaths_participant10'] / data['t200_deaths'].replace(0, 1)) * 100

    data['adc_death_participation_delta_team1'] = data['adc_death_participation_team1'] - data['adc_death_participation_team2']
    data['top_death_participation_delta_team1'] = data['top_death_participation_team1'] - data['top_death_participation_team2']
    data['mid_death_participation_delta_team1'] = data['mid_death_participation_team1'] - data['mid_death_participation_team2']
    data['jg_death_participation_delta_team1'] = data['jg_death_participation_team1'] - data['jg_death_participation_team2']
    data['sup_death_participation_delta_team1'] = data['sup_death_participation_team1'] - data['sup_death_participation_team2']
    
    data['adc_death_participation_delta_team2'] = data['adc_death_participation_team2'] - data['adc_death_participation_team1']
    data['top_death_participation_delta_team2'] = data['top_death_participation_team2'] - data['top_death_participation_team1']
    data['mid_death_participation_delta_team2'] = data['mid_death_participation_team2'] - data['mid_death_participation_team1']
    data['jg_death_participation_delta_team2'] = data['jg_death_participation_team2'] - data['jg_death_participation_team1']
    data['sup_death_participation_delta_team2'] = data['sup_death_participation_team2'] - data['sup_death_participation_team1']
    
    data['elo_delta_team1'] = data['elo_team1'] - data['elo_team2']
    data['elo_delta_team2'] = data['elo_team2'] - data['elo_team1']
    
    return data


if __name__ == "__main__":
    data = pd.read_csv("C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/DataPrep/Data_for_Merging/df_unagg.parquet")
    data = feature_eng(data)