import csv
import json

data_dict = {}

with open('tournament_rankings.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        # Using tournament_id as the key to group tournament data
        t_id = row["tournament_id"]
        
        if t_id not in data_dict:
            data_dict[t_id] = {
                "tournament_id": t_id,
                "tournament_name": row["tournament_name"],
                "section_name": {
                    "name": row["section_name"],
                    "section_name_rankings": []
                }
            }

        # Append team ranking to the specific tournament's section's rankings list
        data_dict[t_id]["section_name"]["section_name_rankings"].append({
            "team_name": row["team_name"],
            "team_id": str(row["ranking_team_id"]),
            "rank": row["ranking_ordinal"]
        })

# Convert dictionary to list of dictionaries to match desired output structure
output_list = list(data_dict.values())

# Convert list of dictionaries to JSON string
json_str = json.dumps(output_list, indent=4)

# Write the JSON string to a file
with open('output.json', 'w') as json_file:
    json_file.write(json_str)