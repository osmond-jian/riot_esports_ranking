import trueskill

#todo check trueskill library

# Initialize TrueSkill parameters for each team
initial_mu = 25
initial_sigma = initial_mu / 3  # Default in TrueSkill system
trueskill_params = {team: {'mu': initial_mu, 'sigma': initial_sigma} for team in teams}


def soft_reset_trueskill(ratings, baseline_mu, weight=0.5):
    return {team: {'mu': weight * params['mu'] + (1 - weight) * baseline_mu, 
                   'sigma': params['sigma']} 
            for team, params in ratings.items()}

# Placeholder for TrueSkill parameters over time
trueskill_ratings_over_time = []

# Tracker for the last tournament each team participated in
last_tournament = {team: None for team in trueskill_params.keys()}

# Iterate over each game in your data
for _, row in data.iterrows():
    team1, team2 = row['team1_id'], row['team2_id']
    s = 1 if row['team1_result'] == 'win' else 0  # Outcome
    tournament = row['tournament_id']

    # Soft reset if a team is in a new tournament
    for team in [team1, team2]:
        if last_tournament[team] != tournament:
            baseline_mu = sum([params['mu'] for params in trueskill_params.values()]) / len(trueskill_params)
            trueskill_params[team] = soft_reset_trueskill({team: trueskill_params[team]}, baseline_mu)[team]
            last_tournament[team] = tournament
    
    # Update parameters
    rating1 = trueskill.Rating(mu=trueskill_params[team1]['mu'], sigma=trueskill_params[team1]['sigma'])
    rating2 = trueskill.Rating(mu=trueskill_params[team2]['mu'], sigma=trueskill_params[team2]['sigma'])
    new_rating1, new_rating2 = trueskill.rate_1vs1(rating1, rating2)
    trueskill_params[team1]['mu'], trueskill_params[team1]['sigma'] = new_rating1.mu, new_rating1.sigma
    trueskill_params[team2]['mu'], trueskill_params[team2]['sigma'] = new_rating2.mu, new_rating2.sigma
    
    # Log the updated TrueSkill parameters
    trueskill_ratings_over_time.append((team1, team2, 
                                        trueskill_params[team1]['mu'], trueskill_params[team1]['sigma'],
                                        trueskill_params[team2]['mu'], trueskill_params[team2]['sigma']))
