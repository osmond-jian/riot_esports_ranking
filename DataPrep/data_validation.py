import json
import sys

def check_tournament_level(tournament):
    """Check required keys at the tournament level."""
    required_keys = ['id', 'leagueId', 'slug', 'startDate', 'endDate']
    return all(key in tournament for key in required_keys)

def check_stage_level(stage):
    """Check required keys at the stage level."""
    return 'slug' in stage

def check_section_level(stage):
    """Check required keys at the section level."""
    return 'sections' in stage

def check_matches_level(section):
    """Check required keys at the matches level."""
    return 'matches' in section

def check_teams_level(match):
    """Check required keys at the teams level within a match."""
    if 'teams' not in match:
        return False
    for team in match['teams']:
        if 'id' not in team:
            return False
    return True

def check_games_level(match):
    """Check required keys at the games level."""
    return 'games' in match

def validate_json_structure(data):
    """Validate the overall structure of the JSON data."""
    for tournament in data:
        if not check_tournament_level(tournament):
            return False, "Tournament level check failed."
        
        for stage in tournament.get('stages', []):
            if not check_stage_level(stage):
                return False, "Stage level check failed."
            
            if not check_section_level(stage):
                return False, "Section level check failed."
            
            for section in stage.get('sections', []):
                if not check_matches_level(section):
                    return False, "Matches level check failed."
                
                for match in section.get('matches', []):
                    if not check_teams_level(match):
                        return False, "Teams level check failed."
                    
                    if not check_games_level(match):
                        return False, "Games level check failed."
    
    return True, "All checks passed successfully."

if __name__ == "__main__":

    sys.path.append("..")
    with open(f'C:/Users/akmar/PycharmProjects/lolpowerrank/riot_esports_ranking/esports-data/tournaments.json', 'r') as f:
        data = json.load(f)
    # Validate the sample data
    validate_json_structure(data)
