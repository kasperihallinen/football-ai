# This file is responsible for fetching and processing data, mainly with the soccerdata package, 
# which includes FBref and SoFIFA data. 
# It contains functions to fetch rest days and venues, final standings and player statistics for Premier League teams 
# across multiple seasons.

import os
from pathlib import Path
import pandas as pd
from teams import PREMIER_LEAGUE_TEAMS, unify_team_names

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_CONFIG_DIR = PROJECT_ROOT / "soccerdata_config"

os.environ["SOCCERDATA_DIR"] = str(CUSTOM_CONFIG_DIR)

import soccerdata as sd

pd.set_option("display.max_columns", None)


def fetch_rest_days_and_venues():
    '''
    Fetches the rest days between matches and the venues for Premier League teams across multiple seasons from FBref
    using the soccerdata package. The data is aggregated from all competitions a Premier League team could play in, 
    including domestic leagues, cups, and international competitions.
    The resulting CSV contains the date of the match, home team, away team, rest days for both teams, and the venue.'''

    custom_data_dir = PROJECT_ROOT / "data" / "fbref" / "raw_data"
    output_file = "./data/fbref/rest_days_and_venues.csv"

    # Include all competitions a Premier League team could play in
    all_competitions = [
        "ENG-Premier League",  # Domestic League
        "FA Cup",              # Domestic Cup
        "EFL Cup",             # Domestic League Cup
        "FA Community Shield", # Domestic Club Competition
        "Champions League",    # Continental Top Tier
        "Europa League",       # Continental 2nd Tier
        "Conference League",   # Continental 3rd Tier
        "FIFA Club World Cup"  # International Club Competition
    ]

    # Initialize FBref reader with all tournaments across multiple seasons
    fbref = sd.FBref(leagues=all_competitions, 
                    seasons=["17-18", "18-19", "19-20", "20-21", "21-22", "22-23", "23-24", "24-25", "25-26"], 
                    data_dir=custom_data_dir)

    # This will aggregate schedules from ALL defined competitions into one DataFrame
    full_schedule = fbref.read_schedule()

    # Reset index to make filtering and sorting by date straightforward
    df_all = full_schedule.reset_index()

    # Print the columns to understand the structure of the DataFrame
    print(df_all.columns)

    # Unify team names
    unify_team_names(df_all, "home_team")
    unify_team_names(df_all, "away_team")

    # Get all Premier League team names
    premier_league_teams = PREMIER_LEAGUE_TEAMS.keys()

    # Keep only the rows where either the home or away team is a Premier League team
    df_all = df_all[df_all["home_team"].isin(premier_league_teams) | df_all["away_team"].isin(premier_league_teams)]

    rest_days_df = pd.DataFrame(columns=["date", "league", "home_team", "away_team", "rest_days", "venue"])
    # Go through each team in the Premier League and calculate the rest days between matches
    for team in premier_league_teams:
        team_all_fixtures = df_all[(df_all["home_team"] == team) | (df_all["away_team"] == team)].copy()
        team_all_fixtures = team_all_fixtures.sort_values(by="date").reset_index(drop=True)
        
        # Calculate rest days between matches
        team_all_fixtures["rest_days"] = team_all_fixtures["date"].diff().dt.days - 1
        # If the team is home team, we set the rest days to a column called "home_rest_days", 
        # otherwise we set it to a column called "away_rest_days"
        team_all_fixtures["home_rest_days"] = team_all_fixtures.apply(
            lambda row: row["rest_days"] if row["home_team"] == team else None, axis=1)
        team_all_fixtures["away_rest_days"] = team_all_fixtures.apply(
            lambda row: row["rest_days"] if row["away_team"] == team else None, axis=1)

        # Keep only Premier League matches from 2017-08-01 onwards
        premier_league_fixtures = team_all_fixtures[team_all_fixtures["league"] == "ENG-Premier League"]
        premier_league_fixtures = premier_league_fixtures[premier_league_fixtures["date"] >= '2017-08-01']

        # Add the rest days data to the main DataFrame
        rest_days_df = pd.concat([rest_days_df, premier_league_fixtures], ignore_index=True)

    # Now each match has two rows in the rest_days_df, one for the home team and one for the away team. 
    # We need to combine them into one row per match.
    rest_days_df = rest_days_df.groupby(["date", "home_team", "away_team", "venue"]).agg({
        "home_rest_days": "first",
        "away_rest_days": "first"
    }).reset_index()

    # Remove dots from venue names to unify them, e.g. "St. James' Park" and "St James' Park" should be the same.
    rest_days_df["venue"] = rest_days_df["venue"].str.replace('.', '', regex=False)
    # Replace 'The American Express Community Stadium' with 'The American Express Stadium' to unify the venue names.
    rest_days_df["venue"] = rest_days_df["venue"].replace("The American Express Community Stadium", "The American Express Stadium")

    rest_days_df = rest_days_df.sort_values(by="date").reset_index(drop=True)

    print(rest_days_df.head(20))

    # Save the rest days and venue data to a CSV file
    rest_days_df.to_csv(output_file, index=False)


fetch_rest_days_and_venues()