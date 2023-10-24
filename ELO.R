library(data.table)

setwd("~/Downloads")
data2 <- read.csv("elo_round_1.csv", header=T, na.strings=c("",".","NA"))
data1 <- read.csv("objective_ranking_round_1.csv", header=T, na.strings=c("",".","NA"))
data3 <- read.csv("games_id.csv", header=T, na.strings=c("",".","NA"))


# Setting data tables
dt2 = setDT(data2)    
dt1 = setDT(data1)    
d3 = setDT(data3)

# Rename columns for merging
setnames(dt2, "tournamentid", "tournament_id")
setnames(d3, "id", "tournament_id")
setnames(d3, "games_id", "game_id")
d3_unique <- d3[!duplicated(d3[, .(game_id, tournament_id)]), ]
dt2_with_stage <- merge(dt2, d3_unique[, .(tournament_id, game_id, stage_name)], 
                        by=c("tournament_id", "game_id"), 
                        all.x=TRUE)

# Columns from dt1 to be merged
cols_from_dt1 <- c("tournament_name", "tournament_slug", "league_id", "section_name", 
                   "team_name", "team_slug", "team_acronym", "strategy_type", "strategy_count",
                   "total_match_wins", "total_match_losses", "match_win_percentage", 
                   "total_wins_record", "total_losses_record", "total_ties_record", "total_game_wins",
                   "total_game_losses", "blue_side_wins", "blue_side_losses", "red_side_wins", 
                   "red_side_losses", "game_win_percentage", "league_name", "region", "league_slug",
                   "type_of_competition", "region_type", "full_team_name", "full_team_slug", 
                   "acronym", "region_type_modified", "blue_side_win_percentage", 
                   "red_side_win_percentage", "best_of", "enddate", "startdate", "Team_Region", "tournament_ranking", 
                   "ranking_ordinal")

# Merge for team1
team1_merged <- merge(dt2_with_stage, dt1, 
                      by.x = c("team1", "tournament_id", "stage_name"), 
                      by.y = c("team_id", "tournament_id", "stage_name"),
                      all.x = TRUE)

# Rename columns for team1
cols_to_rename_team1 <- paste0(cols_from_dt1, "_team1")
setnames(team1_merged, cols_from_dt1, cols_to_rename_team1)

# Merge for team2
team2_merged <- merge(dt2_with_stage, dt1, 
                      by.x = c("team2", "tournament_id", "stage_name"), 
                      by.y = c("team_id", "tournament_id", "stage_name"),
                      all.x = TRUE)

# Rename columns for team2
cols_to_rename_team2 <- paste0(cols_from_dt1, "_team2")
setnames(team2_merged, cols_from_dt1, cols_to_rename_team2)

# Now join team1 and team2 results based on game-specific columns
final_dt <- merge(team1_merged, team2_merged, 
                  by = c("game_id", "tournament_id", "stage_name", "X", "game_num", "team1", "team2", "elo1", "elo2"),
                  all.x = TRUE)

# View the final result
View(final_dt)

head(final_dt)

setnames(final_dt, "X", "game_number_order")

write.csv(final_dt, file="objective_ranking_and_ELO.csv")


#################################################################################
library(dplyr)
library(stringr)

data <- read.csv("objective_ranking_and_ELO.csv", header=T, na.strings=c("",".","NA"))

#####################################################################
# Add a year column to the original dataset
data$year <- as.numeric(format(as.Date(data$startdate_team1, format="%Y-%m-%d"), "%Y"))

# Filter out data for teams that participated in MSI or Worlds
teams_at_msi_worlds <- data %>%
  dplyr::filter(league_name_team1 %in% c("MSI", "Worlds")) %>%
  dplyr::select(team1) %>%
  dplyr::distinct()

data_before_tournaments <- data %>%
  dplyr::filter(!league_name_team1 %in% c("MSI", "Worlds") & 
                  team1 %in% teams_at_msi_worlds$team1)

# Rename the column to prevent name clash during join
msi_worlds_dates <- data %>%
  dplyr::filter(league_name_team1 %in% c("MSI", "Worlds")) %>%
  dplyr::group_by(year, league_name_team1) %>%
  dplyr::summarize(end_date = max(as.Date(enddate_team1, format="%Y-%m-%d"), na.rm = TRUE), .groups = "drop")
msi_worlds_dates <- msi_worlds_dates %>%
  dplyr::rename(tournament_name = league_name_team1)

# Join the dataframes based on the year column
data_with_dates <- data_before_tournaments %>%
  dplyr::left_join(msi_worlds_dates, by = "year")

# Filter for games that took place before MSI and were MSI games
data_before_msi <- data_with_dates %>%
  dplyr::filter(as.Date(startdate_team1, format="%Y-%m-%d") <= end_date & tournament_name == "MSI")

# Filter for games that took place before Worlds and were Worlds games
data_before_worlds <- data_with_dates %>%
  dplyr::filter(as.Date(startdate_team1, format="%Y-%m-%d") <= end_date & tournament_name == "Worlds")


# Identify teams with region not in ("North_America", "Europe", "Korea")
other_region_teams <- data %>%
  dplyr::filter(!(Team_Region_team1 %in% c("North_America", "Europe", "Korea")))

# Filter for games before MSI for other region teams
data_before_msi_other <- data_with_dates %>%
  dplyr::filter(as.Date(startdate_team1, format="%Y-%m-%d") <= end_date & 
                  tournament_name == "MSI" & team1 %in% other_region_teams$team1)

# Calculate the most recent ELO for other region teams before MSI
most_recent_elo_before_msi_other <- data_before_msi_other %>%
  dplyr::group_by(year, team1, team_name_team1) %>%
  dplyr::arrange(desc(startdate_team1)) %>%
  dplyr::slice(n = 1) %>%
  dplyr::select(-startdate_team1) %>%
  dplyr::summarize(Most_Recent_Elo_MSI_Other = mean(elo1, na.rm = TRUE), .groups = "drop")

# Add league_name_team1 column based on team1 and team_name_team1
most_recent_elo_before_msi_other <- most_recent_elo_before_msi_other %>%
  left_join(data %>% select(year, team1, team_name_team1, league_name_team1) %>%
              distinct(year, team1, team_name_team1, league_name_team1),
            by = c("year", "team1", "team_name_team1"))

# Calculate the most recent ELO for other region teams before Worlds
most_recent_elo_before_worlds_other <- data_before_worlds_other %>%
  dplyr::group_by(year, team1, team_name_team1) %>%
  dplyr::arrange(desc(startdate_team1)) %>%
  dplyr::slice(n = 1) %>%
  dplyr::select(-startdate_team1) %>%
  dplyr::summarize(Most_Recent_Elo_Worlds_Other = mean(elo1, na.rm = TRUE), .groups = "drop")

# Add league_name_team1 column based on team1 and team_name_team1
most_recent_elo_before_worlds_other <- most_recent_elo_before_worlds_other %>%
  left_join(data %>% select(year, team1, team_name_team1, league_name_team1) %>%
              distinct(year, team1, team_name_team1, league_name_team1),
            by = c("year", "team1", "team_name_team1"))

# Print the results
print(most_recent_elo_before_msi_other)
print(most_recent_elo_before_worlds_other)

#Filter to create correct data tables
MSI_ELO <- most_recent_elo_before_msi_other %>%
  dplyr::filter(league_name_team1 %in% c("MSI"))

Worlds_ELO <- most_recent_elo_before_worlds_other %>%
  dplyr::filter(league_name_team1 %in% c("Worlds"))

#Add Team Region

MSI_ELO_FINAL <- MSI_ELO %>%
  left_join(data %>% select(team1, team_name_team1, Team_Region_team1) %>%
              distinct(team1, team_name_team1, Team_Region_team1),
            by = c("team1", "team_name_team1"))

# Join Team_Region to most_recent_elo_before_worlds_other
Worlds_ELO_FINAL <- Worlds_ELO %>%
  left_join(data %>% select(team1, team_name_team1, Team_Region_team1) %>%
              distinct(team1, team_name_team1, Team_Region_team1),
            by = c("team1", "team_name_team1"))

write.csv(MSI_ELO_FINAL, file="MSI_ELO_FINAL.csv")
write.csv(Worlds_ELO_FINAL, file="Worlds_ELO_FINAL.csv")

##################################################################################

df_worlds_elo <- read.csv("Worlds_ELO_FINAL_updated.csv", header=T, na.strings=c("",".","NA"))
df_msi_elo <- read.csv("MSI_ELO_FINAL_updated.csv", header=T, na.strings=c("",".","NA"))

# First DataFrame
msi_ranking_summary_average <- df_msi_elo %>%
  group_by(Team_Region, year, league_name_team1) %>%
  summarize(Average_Elo = mean(Most_Recent_Elo, na.rm = TRUE),
            Average_Ranking = mean(Final_Ranking_in_Tournament, na.rm = TRUE)) %>%
  rename(Year = year, Tournament = league_name_team1) %>%
  ungroup()

write.csv(msi_ranking_summary_average, file="msi_ranking_summary_average.csv")

# Second DataFrame
msi_ranking_summary_highest <- df_msi_elo %>%
  group_by(Team_Region, year, league_name_team1) %>%
  summarize(Average_Elo = mean(Most_Recent_Elo, na.rm = TRUE),
            Highest_Placement = min(Final_Ranking_in_Tournament, na.rm = TRUE)) %>%
  rename(Year = year, Tournament = league_name_team1) %>%
  ungroup()

write.csv(msi_ranking_summary_highest, file="msi_ranking_summary_highest.csv")

# First DataFrame
worlds_ranking_summary_average <- df_worlds_elo %>%
  group_by(Team_Region, year, league_name_team1) %>%
  summarize(Average_Elo = mean(Most_Recent_Elo, na.rm = TRUE),
            Average_Ranking = mean(Final_Ranking_in_Tournament, na.rm = TRUE)) %>%
  rename(Year = year, Tournament = league_name_team1) %>%
  ungroup()

write.csv(worlds_ranking_summary_average, file="worlds_ranking_summary_average.csv")

# Second DataFrame
worlds_ranking_summary_highest <- df_worlds_elo %>%
  group_by(Team_Region, year, league_name_team1) %>%
  summarize(Average_Elo = mean(Most_Recent_Elo, na.rm = TRUE),
            Highest_Placement = min(Final_Ranking_in_Tournament, na.rm = TRUE)) %>%
  rename(Year = year, Tournament = league_name_team1) %>%
  ungroup()

write.csv(worlds_ranking_summary_highest, file="worlds_ranking_summary_highest.csv")
