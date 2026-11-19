# This file is responsible for fetching and processing data, mainly with the soccerdata package, 
# which includes FBref and SoFIFA data. 
# It contains functions to fetch rest days and venues, and player statistics for Premier League teams 
# across multiple seasons.

import os
from pathlib import Path
import pandas as pd

from premier_league import TEAMS, SEASONS, unify_team_names

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_CONFIG_DIR = PROJECT_ROOT / "soccerdata_config"

os.environ["SOCCERDATA_DIR"] = str(CUSTOM_CONFIG_DIR)

import soccerdata as sd
from custom_sofifa import SoFIFA as CustomSoFIFA

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def fetch_rest_days_and_venues():
    '''
    Fetches the rest days between matches and the venues for Premier League teams across multiple seasons from FBref
    using the soccerdata package. The data is aggregated from all competitions a Premier League team could play in, 
    including domestic leagues, cups, and international competitions.
    The resulting CSV contains the date of the match, home team, away team, rest days for both teams, and the venue.
    '''

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
    premier_league_teams = TEAMS.keys()

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
    rest_days_df["venue"] = rest_days_df["venue"].replace("The American Express Community Stadium", 
                                                          "The American Express Stadium")

    rest_days_df = rest_days_df.sort_values(by="date").reset_index(drop=True)

    print(rest_days_df.head(20))

    # Save the rest days and venue data to a CSV file
    rest_days_df.to_csv(output_file, index=False)


def fetch_player_attributes(days_between_versions=60):
    """
    Fetches player overall ratings, physical attributes and finacial data for Premier League teams across multiple 
    seasons from SoFIFA using a customized soccerdata script.
    The resulting CSV contains the player name, team, league, version id, fifa edition, update date, player id, age, 
    height, weight, overall rating, potential rating, value and wage.
    Parameters
    ----------
    days_between_versions: int
        Number of days between each SoFIFA version to fetch per season. Default is 60.
        The first version will be the closed beta version and the second version will be the official release version.
        After that, the versions will be spaced approximately every `days_between_versions` days across the season.
    """
    custom_data_dir = PROJECT_ROOT / "data" / "sofifa" / "raw_data"
    output_file = "./data/sofifa/player_attributes.csv"

    # Initialize SoFIFA reader to read FIFA and FC versions.
    sofifa = sd.SoFIFA(data_dir=custom_data_dir)
    versions_df = sofifa.read_versions()

    # Skip the versions that do not have a valid date. The update column is in the format Aug 30, 2006.
    versions_df = versions_df[versions_df['update'].str.match(r'^[A-Za-z]{3} \d{1,2}, \d{4}$')]
    # Cast update column to datetime for proper sorting.
    versions_df['date'] = pd.to_datetime(versions_df['update'], format='%b %d, %Y')

    editions = ['FIFA18', 'FIFA19', 'FIFA20', 'FIFA21', 'FIFA22', 'FIFA23', 'FC24', 'FC25', 'FC26']

    versions_list = []
    for edition in editions:
        year = int(edition[-2:]) + 2000 - 1
        season_data = SEASONS[year]
        start_date = pd.to_datetime(season_data['dates'][0])
        end_date = pd.to_datetime(season_data['dates'][1])
        fifa_release = pd.to_datetime(season_data['fifa_release'])

        # Sort by index which corresponds to chronological order of the versions.
        edition_versions_df = versions_df[versions_df['fifa_edition'] == edition].sort_index()
        # Find the date of the first version after the end date of the season.
        first_version_after_end = edition_versions_df[edition_versions_df['date'] > end_date].head(1)
        # The date of the first version after the end date is the cutoff date for the versions we want to take.
        # The ratings and lineups are not updated after this.
        if not first_version_after_end.empty:
            cutoff_date = first_version_after_end['date'].values[0]
        else:
            cutoff_date = end_date

        edition_versions_df = edition_versions_df[edition_versions_df['date'] <= cutoff_date]

        # We can also drop versions from the start of the season.
        # First, we want to take the latest version before the start of the season.
        first_version = edition_versions_df[edition_versions_df['date'] < start_date].tail(1)
        # If there are no versions before the start of the season, we will take the first version available.
        if first_version.empty:
            first_version = edition_versions_df.head(1)
        versions_list.append(first_version.index[0])

        # Then we want to take the latest version before the official release of the game.
        version_before_release = edition_versions_df[edition_versions_df['date'] < fifa_release].tail(1)
        versions_list.append(version_before_release.index[0])
        next_version_date = version_before_release['date'].values[0]

        # Now take one version every `days_between_versions` days.
        while next_version_date < end_date:
            next_version_date += pd.Timedelta(days=days_between_versions)
            # Find the version closest to the next_version_date
            closest_version = edition_versions_df.iloc[(edition_versions_df['date'] - next_version_date).abs().argsort()[:1]]
            if not closest_version.empty and closest_version.index[0] not in versions_list:
                versions_list.append(closest_version.index[0])

    # Cast the versions_list to a list of integers
    versions_list = [int(v) for v in versions_list]

    # Initialize custom SoFIFA reader for Premier League across multiple versions (seasons).
    sofifa = CustomSoFIFA(leagues=["ENG-Premier League"], 
                          versions=versions_list,
                          data_dir=custom_data_dir)

    player_attributes_df = sofifa.read_player_attributes()

    # Drop duplicate rows
    player_attributes_df = player_attributes_df.drop_duplicates(subset=["player_id", "version_id"])
    # Take only the cm and kg amounts from height and weight columns, respectively.
    player_attributes_df["height"] = player_attributes_df["height"].str.extract(r'(\d+)cm').astype(float)
    player_attributes_df["weight"] = player_attributes_df["weight"].str.extract(r'(\d+)kg').astype(float)
    # overall and potential columns are in the format "81 +14". We will take only the first part.
    player_attributes_df["overall"] = player_attributes_df["overall"].str.split().str[0]
    player_attributes_df["potential"] = player_attributes_df["potential"].str.split().str[0]
    # Convert value and wage to numeric values, handling cases like '€1.5M' or '€500K'
    player_attributes_df["value"] = player_attributes_df["value"].replace(
        {'€': '', 'K': 'e3', 'M': 'e6'}, regex=True).astype(float)
    player_attributes_df["wage"] = player_attributes_df["wage"].replace(
        {'€': '', 'K': 'e3', 'M': 'e6'}, regex=True).astype(float)
    # Unify team names
    unify_team_names(player_attributes_df, "team")

    print(player_attributes_df.head(20))

    # Save the player statistics data to a CSV file
    player_attributes_df.to_csv(output_file, index=False)

# fetch_rest_days_and_venues()
# There's so much data that we will take only a limited number of versions.
fetch_player_attributes(days_between_versions=30)