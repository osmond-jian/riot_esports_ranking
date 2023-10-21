import math
import random

# Glicko-2 constants
TAU = 0.5  # System constant determining volatility change; may need tuning
q = math.log(10) / 400  # Mathematical constant for Glicko-2 scaling


def g(RD):
    """
    G-function to weight the impact of an opponent's outcome.
    """
    return 1 / math.sqrt(1 + 3 * (q**2) * (RD**2) / (math.pi**2))


def E(r, rj, RDj):
    """
    Expected score of player with rating r against an opponent with rating rj and RD RDj.
    """
    return 1 / (1 + math.exp(-g(RDj) * (r - rj)))


def update_parameters(r, RD, sigma, outcomes):
    """
    Update Glicko-2 parameters r, RD, and sigma based on match outcomes.
    
    Parameters:
        r, RD, sigma (float): Current rating, rating deviation, and volatility.
        outcomes (list of dict): Match outcomes and opponent parameters. 
                                 Each entry should be {'rj': , 'RDj': , 'sj': }
                                 where 'rj' and 'RDj' are the opponent's parameters
                                 and 'sj' is the match outcome (1 for win, 0 for loss).
    
    Returns:
        Updated parameters r, RD, sigma.
    """
    # Precompute some values
    v_inv = 0  # Inverse of estimated variance of player's rating based on game outcomes
    delta = 0  # Estimated improvement in rating
    
    for outcome in outcomes:
        Ej = E(r, outcome['rj'], outcome['RDj'])
        v_inv += g(outcome['RDj'])**2 * Ej * (1 - Ej)
        delta += g(outcome['RDj']) * (outcome['sj'] - Ej)
    
    v = 1 / v_inv  # Estimated variance of player's rating based on game outcomes
    
    # Step 4: Update volatility sigma
    delta_squared = delta**2
    a = math.log(sigma**2)  # Initial estimate of log volatility square
    
    # Define f(x) as per Glicko-2 system document
    def f(x):
        ex = math.exp(x)
        tmp = (ex * (delta_squared - RD**2 - v - ex)) / (2 * (RD**2 + v + ex)**2)
        return tmp - (x - a) / (TAU**2)
    
    # Find a root of f(x) using the Raphson method
    A = a
    if delta_squared > RD**2 + v:
        B = math.log(delta_squared - RD**2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        B = a - k * TAU
    
    f_A = f(A)
    f_B = f(B)
    
    # Continue until convergence
    while abs(B - A) > 0.000001:
        C = A + ((A - B) * f_A) / (f_B - f_A)
        f_C = f(C)
        if f_C * f_B < 0:
            A = B
            f_A = f_B
        else:
            f_A /= 2
        B = C
        f_B = f_C
    
    sigma_new = math.exp(A / 2)
    
    # Step 5: Update rating and rating deviation
    RD_star = math.sqrt(RD**2 + sigma_new**2)  # Intermediate RD value
    r_new = r + (q / (1 / (RD_star**2) + 1 / v)) * delta  # Updated rating
    RD_new = 1 / math.sqrt(1 / (RD_star**2) + 1 / v)  # Updated RD
    
    return r_new, RD_new, sigma_new

def soft_reset_glicko(ratings, baseline_r, weight=0.5):
    """
    Apply a soft reset to Glicko-2 ratings.
    
    Parameters:
        ratings (dict): Current Glicko-2 ratings for each team.
        baseline_r (float): Baseline rating towards which ratings are reset.
        weight (float): Weight given to the old rating during the reset.
        
    Returns:
        dict: Glicko-2 ratings after the soft reset.
    """
    return {team: {'r': weight * params['r'] + (1 - weight) * baseline_r, 
                   'RD': params['RD'], 
                   'sigma': params['sigma']} 
            for team, params in ratings.items()}


if __name__ == "__main__":

    # Constants for Glicko-2
    INITIAL_R = 1500
    INITIAL_RD = 350
    INITIAL_SIGMA = 0.06

    # Extract unique teams
    teams = pd.concat([cleaned_data['team1_id'], cleaned_data['team2_id']]).unique()

    # Initialize Glicko-2 parameters for each team
    glicko_params = {team: {'r': INITIAL_R, 'RD': INITIAL_RD, 'sigma': INITIAL_SIGMA} for team in teams}

    # Randomly select 3 tournaments
    selected_tournaments = random.sample(cleaned_data['tournament_id'].unique().tolist(), 3)

    # Subset data to the selected tournaments
    subset_data = cleaned_data[cleaned_data['tournament_id'].isin(selected_tournaments)].copy()

    # Display basic info about the subsetted data
    (subset_data['tournament_id'].value_counts(), subset_data.head())

    # Example usage (with hypothetical match outcomes)
    example_outcomes = [
        {'rj': 1400, 'RDj': 30, 'sj': 1},
        {'rj': 1550, 'RDj': 100, 'sj': 0},
        {'rj': 1700, 'RDj': 300, 'sj': 0}
    ]

    # Update parameters based on example outcomes
    update_parameters(INITIAL_R, INITIAL_RD, INITIAL_SIGMA, example_outcomes)

    
    # Apply Glicko-2 updates and soft resets iteratively across games
    glicko_ratings_over_time = []

    # Tracker for the last tournament each team participated in
    last_tournament = {team: None for team in glicko_params.keys()}

    # Iterate over each game in the subsetted data
    for _, row in subset_data.iterrows():
        team1, team2 = row['team1_id'], row['team2_id']
        s = 1 if row['team1_result'] == 'win' else 0  # Outcome
        tournament = row['tournament_id']

        # Soft reset if a team is in a new tournament
        for team in [team1, team2]:
            if last_tournament[team] != tournament:
                # Calculate the baseline rating as the mean rating of all teams
                baseline_r = sum([params['r'] for params in glicko_params.values()]) / len(glicko_params)
                
                # Apply the soft reset
                glicko_params[team] = soft_reset_glicko({team: glicko_params[team]}, baseline_r)[team]
                
                # Update the last tournament tracker
                last_tournament[team] = tournament
        
        # Update parameters based on the game outcome
        outcomes_team1 = [{'rj': glicko_params[team2]['r'], 'RDj': glicko_params[team2]['RD'], 'sj': s}]
        outcomes_team2 = [{'rj': glicko_params[team1]['r'], 'RDj': glicko_params[team1]['RD'], 'sj': 1-s}]
        
        glicko_params[team1]['r'], glicko_params[team1]['RD'], glicko_params[team1]['sigma'] = \
            update_parameters(glicko_params[team1]['r'], glicko_params[team1]['RD'], glicko_params[team1]['sigma'], outcomes_team1)
        glicko_params[team2]['r'], glicko_params[team2]['RD'], glicko_params[team2]['sigma'] = \
            update_parameters(glicko_params[team2]['r'], glicko_params[team2]['RD'], glicko_params[team2]['sigma'], outcomes_team2)
        
        # Log the updated Glicko-2 parameters
        glicko_ratings_over_time.append((team1, team2, 
                                        glicko_params[team1]['r'], glicko_params[team1]['RD'], glicko_params[team1]['sigma'],
                                        glicko_params[team2]['r'], glicko_params[team2]['RD'], glicko_params[team2]['sigma']))
        
    # Convert to DataFrame for easier analysis and visualization
    glicko_df = pd.DataFrame(glicko_ratings_over_time, columns=['team1', 'team2', 'r1', 'RD1', 'sigma1', 'r2', 'RD2', 'sigma2'])

    # Display final ratings and a snippet of ratings over time
    (final_glicko_ratings := glicko_params, glicko_df.head())