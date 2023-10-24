import json

# Read the JSON data from a file
with open('output.json', 'r') as file:
    sample_json = json.load(file)

# Initialize the result list.
result = []

for item in sample_json:
    # Check if the tournament_id already exists in the result.
    tournament_exists = [x for x in result if x["tournament_id"] == item["tournament_id"]]
    
    # If the tournament already exists, add the team to its final ranking list.
    if tournament_exists:
        tournament = tournament_exists[0]
        tournament["final ranking"].append({
            "team_name": item["team_name"],
            "team_id": item["ranking_team_id"],
            "rank": item["ranking_ordinal"]
        })
    # Otherwise, create a new tournament entry.
    else:
        result.append({
            "tournament_id": item["tournament_id"],
            "tournament_name": item["tournament_name"],
            "final ranking": [{
                "team_name": item["team_name"],
                "team_id": item["ranking_team_id"],
                "rank": item["ranking_ordinal"]
            }]
        })

# Sort the teams in each tournament based on their rank.
for tournament in result:
    tournament["final ranking"] = sorted(tournament["final ranking"], key=lambda x: int(x["rank"]))

# Write the transformed data to a new file (or you can replace 'path_to_your_output_file.json' with the input file path to overwrite it)
with open('rankings.json', 'w') as file:
    json.dump(result, file, indent=4)
