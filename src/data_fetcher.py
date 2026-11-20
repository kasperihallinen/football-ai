# This file contains functions to fetch and calculate
# - rest days, venues, travel distances and lineups from FBref,
# - player attributes and ratings from SoFIFA,
# - match stats from Github, and
# - managers from Wikipedia
# for Premier League teams across multiple seasons.

import os
from pathlib import Path
import pandas as pd
import io
import requests
from geopy.distance import geodesic
from premier_league import (
    TEAMS,
    SEASONS,
    unify_team_names,
    unify_venue_names,
    get_venues_df,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_CONFIG_DIR = PROJECT_ROOT / "soccerdata_config"

os.environ["SOCCERDATA_DIR"] = str(CUSTOM_CONFIG_DIR)

import soccerdata as sd
from custom_sofifa import SoFIFA as CustomSoFIFA

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def fetch_schedules_and_venues():
    """
    Fetches the schedules and venues for Premier League teams across multiple
    seasons from FBref using the soccerdata package.
    The data is aggregated from all competitions a Premier League team could
    play in, including domestic leagues, cups, and international competitions.
    The resulting CSV contains the date of the match, home team, away team,
    rest days for both teams, venue and travel distance of the away team.
    """

    custom_data_dir = PROJECT_ROOT / "data" / "fbref" / "raw_data"
    output_file = "./data/fbref/rest_days_and_venues.csv"

    # Include all competitions a Premier League team could play in
    all_competitions = [
        "ENG-Premier League",  # Domestic League
        "FA Cup",  # Domestic Cup
        "EFL Cup",  # Domestic League Cup
        "FA Community Shield",  # Domestic Club Competition
        "Champions League",  # Continental Top Tier
        "Europa League",  # Continental 2nd Tier
        "Conference League",  # Continental 3rd Tier
        "FIFA Club World Cup",  # International Club Competition
    ]

    # Initialize FBref reader with all tournaments across multiple seasons
    fbref = sd.FBref(
        leagues=all_competitions,
        seasons=[
            "17-18",
            "18-19",
            "19-20",
            "20-21",
            "21-22",
            "22-23",
            "23-24",
            "24-25",
            "25-26",
        ],
        data_dir=custom_data_dir,
    )

    # This will aggregate schedules from ALL defined competitions into one DataFrame
    df_all = fbref.read_schedule()
    # Reset index to make filtering and sorting by date straightforward
    df_all = df_all.reset_index()

    # Print the columns to understand the structure of the DataFrame
    print(df_all.columns)

    # Unify team names
    unify_team_names(df_all, "home_team")
    unify_team_names(df_all, "away_team")

    # Get all Premier League team names
    premier_league_teams = TEAMS.keys()

    # Keep only the rows where either the home or away team is a Premier League
    # team
    df_all = df_all[
        df_all["home_team"].isin(premier_league_teams)
        | df_all["away_team"].isin(premier_league_teams)
    ]

    matches_df = pd.DataFrame(
        columns=[
            "date",
            "league",
            "home_team",
            "away_team",
            "rest_days",
            "venue",
        ]
    )
    # Go through each team in the Premier League and calculate the rest days
    # between matches
    for team in premier_league_teams:
        team_all_fixtures = df_all[
            (df_all["home_team"] == team) | (df_all["away_team"] == team)
        ]
        team_all_fixtures = team_all_fixtures.sort_values(
            by="date"
        ).reset_index(drop=True)

        # Calculate rest days between matches
        team_all_fixtures["rest_days"] = (
            team_all_fixtures["date"].diff().dt.days - 1
        )
        # If the team is home team, we set the rest days to a column called
        # "home_rest_days", otherwise we set it to a column called
        # "away_rest_days"
        team_all_fixtures["home_rest_days"] = team_all_fixtures.apply(
            lambda row: row["rest_days"] if row["home_team"] == team else None,
            axis=1,
        )
        team_all_fixtures["away_rest_days"] = team_all_fixtures.apply(
            lambda row: row["rest_days"] if row["away_team"] == team else None,
            axis=1,
        )

        # Keep only Premier League matches from 2017-08-01 onwards
        premier_league_fixtures = team_all_fixtures[
            team_all_fixtures["league"] == "ENG-Premier League"
        ]
        premier_league_fixtures = premier_league_fixtures[
            premier_league_fixtures["date"] >= "2017-08-01"
        ]

        # Add the rest days data to the main DataFrame
        matches_df = pd.concat(
            [matches_df, premier_league_fixtures], ignore_index=True
        )

    # Now each match has two rows, one for the home team and one for the away
    # team. We need to combine them into one row per match.
    matches_df = (
        matches_df.groupby(["date", "home_team", "away_team", "venue"])
        .agg({"home_rest_days": "first", "away_rest_days": "first"})
        .reset_index()
    )

    # Unify venue names
    unify_venue_names(matches_df, "venue")

    venues_df = get_venues_df()

    # Merge match data with venue coordinates
    matches_with_coords = matches_df.merge(
        venues_df.rename(columns={"team": "home_team"}),
        on=["home_team", "venue"],
        how="left",
    ).merge(
        venues_df,
        left_on="away_team",
        right_on="team",
        how="left",
        suffixes=("_home", "_away"),
    )

    # Keep only those rows where the match date is between from_away and
    # to_away, when those columns are not null.
    matches_with_coords = matches_with_coords[
        (
            matches_with_coords["from_away"].isnull()
            | (matches_with_coords["date"] >= matches_with_coords["from_away"])
        )
        & (
            matches_with_coords["to_away"].isnull()
            | (matches_with_coords["date"] <= matches_with_coords["to_away"])
        )
    ]

    # Calculate travel distance in kilometers for each match
    matches_with_coords["travel_distance"] = matches_with_coords.apply(
        lambda row: geodesic(
            (row["latitude_home"], row["longitude_home"]),
            (row["latitude_away"], row["longitude_away"]),
        ).kilometers,
        axis=1,
    )

    # Keep only relevant columns
    matches_with_coords = matches_with_coords[
        [
            "date",
            "home_team",
            "away_team",
            "home_rest_days",
            "away_rest_days",
            "venue_home",
            "travel_distance",
        ]
    ].rename(columns={"venue_home": "venue"})
    matches_with_coords = matches_with_coords.sort_values(
        by="date"
    ).reset_index(drop=True)

    print(matches_with_coords.head(20))

    # Save the rest days and venue data to a CSV file
    matches_with_coords.to_csv(output_file, index=False)


def fetch_lineups():
    """
    Fetches the lineups for Premier League teams across multiple seasons from
    FBref using the soccerdata package.
    The resulting CSV contains the date of the match, home team, away team, and
    the lineups for both teams.
    """

    custom_data_dir = PROJECT_ROOT / "data" / "fbref" / "raw_data"
    output_file = "./data/fbref/lineups.csv"

    # Initialize FBref reader with Premier League across multiple seasons
    fbref = sd.FBref(
        leagues=["ENG-Premier League"],
        seasons=[
            "17-18",
            "18-19",
            "19-20",
            "20-21",
            "21-22",
            "22-23",
            "23-24",
            "24-25",
            "25-26",
        ],
        data_dir=custom_data_dir,
    )

    # This will aggregate lineups from all matches into one DataFrame
    lineups_df = fbref.read_lineup(force_cache=True)
    lineups_df = lineups_df.reset_index()

    # The 'game' column is in format '2020-09-12 Crystal Palace-Southampton'
    # Take the date from the 'game' column and convert it to datetime.
    lineups_df["date"] = pd.to_datetime(
        lineups_df["game"].str.split().str[0], format="%Y-%m-%d"
    )
    # Take the teams from the 'game' column and split them into home and away
    # teams.
    lineups_df["home_team"] = (
        lineups_df["game"].str.split(n=1).str[1].str.split("-").str[0]
    )
    lineups_df["away_team"] = (
        lineups_df["game"].str.split(n=1).str[1].str.split("-").str[1]
    )
    # Unify team names
    unify_team_names(lineups_df, "home_team")
    unify_team_names(lineups_df, "away_team")
    unify_team_names(lineups_df, "team")

    print(lineups_df.head(20))

    # Save the lineups data to a CSV file
    lineups_df.to_csv(output_file, index=False)


def fetch_player_attributes(days_between_versions=60):
    """
    Fetches player overall ratings, physical attributes and financial data for
    Premier League teams across multiple seasons from SoFIFA using a customized
    soccerdata script.
    The resulting CSV contains the player name, team, league, version id, fifa
    edition, update date, player id, age, height, weight, overall rating,
    potential rating, value and wage.

    Parameters
    ----------
    days_between_versions: int
        Number of days between each SoFIFA version to fetch per season.
        Default is 60. The first version will be the closed beta version and
        the second version will be the official release version.
        After that, the versions will be spaced approximately every
        `days_between_versions` days across the season.
    """

    custom_data_dir = PROJECT_ROOT / "data" / "sofifa" / "raw_data"
    output_file = "./data/sofifa/player_attributes.csv"

    # Initialize SoFIFA reader to read FIFA and FC versions.
    sofifa = sd.SoFIFA(data_dir=custom_data_dir)
    versions_df = sofifa.read_versions()

    # Skip the versions that do not have a valid date.
    # The update column is in the format Aug 30, 2006.
    versions_df = versions_df[
        versions_df["update"].str.match(r"^[A-Za-z]{3} \d{1,2}, \d{4}$")
    ]
    # Cast update column to datetime for proper sorting.
    versions_df["date"] = pd.to_datetime(
        versions_df["update"], format="%b %d, %Y"
    )

    editions = [
        "FIFA18",
        "FIFA19",
        "FIFA20",
        "FIFA21",
        "FIFA22",
        "FIFA23",
        "FC24",
        "FC25",
        "FC26",
    ]

    versions_list = []
    for edition in editions:
        year = int(edition[-2:]) + 2000 - 1
        season_data = SEASONS[year]
        start_date = pd.to_datetime(season_data["dates"][0])
        end_date = pd.to_datetime(season_data["dates"][1])
        fifa_release = pd.to_datetime(season_data["fifa_release"])

        # Filter the versions_df to only include rows for the current edition.
        edition_versions_df = versions_df[
            versions_df["fifa_edition"] == edition
        ]
        # Sort by index which corresponds to chronological order of the
        # versions.
        edition_versions_df = edition_versions_df.sort_index()
        # Find the date of the first version after the end date of the season.
        first_version_after_end = edition_versions_df[
            edition_versions_df["date"] > end_date
        ].head(1)
        # The date of the first version after the end date is the cutoff date
        # for the versions we want to take.
        # The ratings and lineups are not updated after this.
        if not first_version_after_end.empty:
            cutoff_date = first_version_after_end["date"].values[0]
        else:
            cutoff_date = end_date

        edition_versions_df = edition_versions_df[
            edition_versions_df["date"] <= cutoff_date
        ]

        # We can also drop versions from the start of the season.
        # First, we want to take the latest version before the start of the
        # season.
        first_version = edition_versions_df[
            edition_versions_df["date"] < start_date
        ].tail(1)
        # If there are no versions before the start of the season, we will take
        # the first version available.
        if first_version.empty:
            first_version = edition_versions_df.head(1)
        versions_list.append(first_version.index[0])

        # Then we want to take the latest version before the official release
        # of the game.
        version_before_release = edition_versions_df[
            edition_versions_df["date"] < fifa_release
        ].tail(1)
        versions_list.append(version_before_release.index[0])
        next_version_date = version_before_release["date"].values[0]

        # Now take one version every `days_between_versions` days.
        while next_version_date < end_date:
            next_version_date += pd.Timedelta(days=days_between_versions)
            # Find the version closest to the next_version_date
            closest_version = edition_versions_df.iloc[
                (edition_versions_df["date"] - next_version_date)
                .abs()
                .argsort()[:1]
            ]
            if (
                not closest_version.empty
                and closest_version.index[0] not in versions_list
            ):
                versions_list.append(closest_version.index[0])

    # Cast the versions_list to a list of integers
    versions_list = [int(v) for v in versions_list]

    # Initialize custom SoFIFA reader for Premier League across multiple
    # versions.
    sofifa = CustomSoFIFA(
        leagues=["ENG-Premier League"],
        versions=versions_list,
        data_dir=custom_data_dir,
    )

    player_attributes_df = sofifa.read_player_attributes()

    # Drop duplicate rows
    player_attributes_df = player_attributes_df.drop_duplicates(
        subset=["player_id", "version_id"]
    )
    # Take only the cm and kg amounts from height and weight columns,
    # respectively.
    player_attributes_df["height"] = (
        player_attributes_df["height"].str.extract(r"(\d+)cm").astype(float)
    )
    player_attributes_df["weight"] = (
        player_attributes_df["weight"].str.extract(r"(\d+)kg").astype(float)
    )
    # overall and potential columns are in the format "81 +14".
    # We will take only the first part.
    player_attributes_df["overall"] = (
        player_attributes_df["overall"].str.split().str[0]
    )
    player_attributes_df["potential"] = (
        player_attributes_df["potential"].str.split().str[0]
    )
    # Convert value and wage to numeric values, handling cases like
    # '€1.5M' or '€500K'
    player_attributes_df["value"] = (
        player_attributes_df["value"]
        .replace({"€": "", "K": "e3", "M": "e6"}, regex=True)
        .astype(float)
    )
    player_attributes_df["wage"] = (
        player_attributes_df["wage"]
        .replace({"€": "", "K": "e3", "M": "e6"}, regex=True)
        .astype(float)
    )
    # Unify team names
    unify_team_names(player_attributes_df, "team")

    print(player_attributes_df.head(20))

    # Save the player statistics data to a CSV file
    player_attributes_df.to_csv(output_file, index=False)


def fetch_match_stats(use_cache=True):
    """
    Download and process the Matches.csv from https://github.com/xgabora/Club-Football-Match-Data/
    The resulting CSV contains the date of the match, season, home team,
    away team, maximum odds for home win, draw and away win, and the following
    match stats for both teams: Elo rating, form in last 5 matches, full time
    goals scored, shots on target, fouls committed, corners, yellow cards and
    red cards.
    """

    data_dir = PROJECT_ROOT / "data" / "xgabora_github"
    raw_data_file = data_dir / "Matches.csv"
    output_file = data_dir / "match_data.csv"

    raw_data_file.parent.mkdir(parents=True, exist_ok=True)

    if use_cache and raw_data_file.exists():
        print(f"Using cached match data from {raw_data_file}")
        matches_df = pd.read_csv(raw_data_file)
    else:
        url = "https://raw.githubusercontent.com/xgabora/Club-Football-Match-Data/main/data/Matches.csv"
        # Load the match stats data
        matches_df = pd.read_csv(url)
        # Save the raw match stats data to a file for future reference
        matches_df.to_csv(raw_data_file, index=False)

    # Keep only Premier League matches from 2017-08-01 onwards.
    matches_df = matches_df[matches_df["Division"] == "E0"]
    matches_df = matches_df[matches_df["MatchDate"] >= "2017-08-01"]

    # Convert the 'MatchDate' column to datetime format.
    # Dates are in YYYY-MM-DD format.
    matches_df["MatchDate"] = pd.to_datetime(
        matches_df["MatchDate"], format="%Y-%m-%d"
    )

    # Rename columns for consistency with other data sources
    matches_df.rename(
        columns={
            "MatchDate": "date",
            "HomeTeam": "home_team",
            "AwayTeam": "away_team",
        },
        inplace=True,
    )

    # Determine the season based on the match date.
    # The season starts first of August and ends last of July of the following
    # year.
    matches_df["season"] = matches_df["date"].apply(
        lambda x: x.year if x.month >= 8 else x.year - 1
    )

    # Keep only relevant columns
    matches_df = matches_df[
        [
            "date",
            "season",
            "home_team",
            "away_team",
            "HomeElo",
            "AwayElo",
            "Form5Home",
            "Form5Away",
            "FTHome",
            "FTAway",
            "HomeTarget",
            "AwayTarget",
            "HomeFouls",
            "AwayFouls",
            "HomeCorners",
            "AwayCorners",
            "HomeYellow",
            "AwayYellow",
            "HomeRed",
            "AwayRed",
            "MaxHome",
            "MaxDraw",
            "MaxAway",
        ]
    ]

    # Unify team names in the home_team and away_team columns
    unify_team_names(matches_df, "home_team")
    unify_team_names(matches_df, "away_team")

    print(matches_df.head(20))
    # Save the processed match stats data to a new CSV file
    matches_df.to_csv(output_file, index=False)


def fetch_managers(use_cache=True):
    """
    Fetches manager data for Premier League teams across multiple seasons from
    Wikipedia.
    The resulting CSV contains the manager name, team, start date and end date.
    """

    data_dir = PROJECT_ROOT / "data" / "wikipedia"
    raw_data_file = data_dir / "raw_managers.html"
    output_file = data_dir / "managers.csv"

    raw_data_file.parent.mkdir(parents=True, exist_ok=True)

    if use_cache and raw_data_file.exists():
        print(f"Using cached manager data from {raw_data_file}")
        with open(raw_data_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        html_content = None

    if html_content is None:
        url = "https://en.wikipedia.org/wiki/List_of_Premier_League_managers"
        headers = {
            "User-Agent": "PremierLeagueMLProject/1.0 (contact: your-email@example.com)"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensures the request succeeded
        html_content = response.text

        # Save the raw HTML content to a file for future reference
        with open(raw_data_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    tables = pd.read_html(io.StringIO(html_content))
    managers_df = tables[1]

    # Take only the relevant columns and rename them for clarity
    managers_df = managers_df[["Name", "Club", "From", "Until"]]
    managers_df = managers_df.rename(
        columns={
            "Name": "manager_name",
            "Club": "team",
            "From": "start_date",
            "Until": "end_date",
        }
    )

    # Replace 'Present*' in the 'end_date' column with none to indicate that
    # the manager is still in position.
    managers_df["end_date"] = managers_df["end_date"].replace("Present*", None)
    # Convert the 'start_date' and 'end_date' columns to datetime format.
    # Dates are in '2 November 2025' format, but they might have a reference
    # attached to them, e.g. '2 November 2025[a]'.
    managers_df["start_date"] = (
        managers_df["start_date"]
        .str.replace(r"\[.*\]", "", regex=True)
        .str.strip()
    )
    managers_df["end_date"] = (
        managers_df["end_date"]
        .str.replace(r"\[.*\]", "", regex=True)
        .str.strip()
    )
    managers_df["start_date"] = pd.to_datetime(
        managers_df["start_date"], format="%d %B %Y", errors="coerce"
    )
    managers_df["end_date"] = pd.to_datetime(
        managers_df["end_date"], format="%d %B %Y", errors="coerce"
    )
    # Strip manager names of '†' and '‡' symbols, which indicate incumbent and
    # caretaker managers.
    managers_df["manager_name"] = (
        managers_df["manager_name"]
        .str.replace("†", "")
        .str.replace("‡", "")
        .str.strip()
    )
    # Unify team names
    unify_team_names(managers_df, "team")

    print(managers_df.head(20))

    # Save the manager data to a CSV file
    managers_df.to_csv(output_file, index=False)


fetch_schedules_and_venues()
# fetch_lineups()
# There's so much data that we will take only a limited number of versions.
# fetch_player_attributes(days_between_versions=30)
# fetch_match_stats()
# fetch_managers()
