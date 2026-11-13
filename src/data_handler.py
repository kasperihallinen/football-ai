# This file is responsible for processing and merging the data fetched from various sources, such as Sports Mole, FBref, 
# and SoFIFA. It contains functions to clean, transform, and combine the data into a unified format for further 
# analysis and modeling.

import pandas as pd
from teams import unify_team_names

XGABORA_PATH = "./data/xgabora_github/"


def process_match_stats():
    """
    Process the Matches.csv downloaded from https://github.com/xgabora/Club-Football-Match-Data/ to prepare it 
    for merging with other data sources.
    """
    # Load the match stats data
    matches_df = pd.read_csv(XGABORA_PATH + "Matches.csv")

    # Keep only Premier League matches from 2017-08-01 onwards.
    matches_df = matches_df[matches_df['Division'] == 'E0']
    matches_df = matches_df[matches_df['MatchDate'] >= '2017-08-01']

    # Convert the 'MatchDate' column to datetime format. Dates are in YYYY-MM-DD format.
    matches_df['MatchDate'] = pd.to_datetime(matches_df['MatchDate'], format='%Y-%m-%d')

    # Rename columns for consistency with other data sources
    matches_df.rename(columns={
        'MatchDate': 'date',
        'HomeTeam': 'home_team',
        'AwayTeam': 'away_team',
    }, inplace=True)

    # Determine the season based on the match date. 
    # The season starts first of August and ends last of July of the following year.
    matches_df['season'] = matches_df['date'].apply(lambda x: x.year if x.month >= 8 else x.year - 1)

    # Keep only relevant columns
    matches_df = matches_df[[
        'date', 'season', 'home_team', 'away_team', 'HomeElo', 'AwayElo', 'Form5Home', 'Form5Away', 'FTHome', 'FTAway', 'HomeTarget', 'AwayTarget', 'HomeFouls', 'AwayFouls', 'HomeCorners', 'AwayCorners', 'HomeYellow', 'AwayYellow', 'HomeRed', 'AwayRed', 'MaxHome', 'MaxDraw', 'MaxAway'
    ]]

    # Unify team names in the home_team and away_team columns
    unify_team_names(matches_df, "home_team")
    unify_team_names(matches_df, "away_team")

    print(matches_df.head(20))
    # Save the processed match stats data to a new CSV file
    matches_df.to_csv(XGABORA_PATH + "processed_matches.csv", index=False)


def calculate_standings():
    """
    Calculate the standings for the Premier League based on match results.
    """
    matches_df = pd.read_csv(XGABORA_PATH + "processed_matches.csv")

    # Build home and away match records
    home = matches_df[["season", "home_team", "FTHome", "FTAway"]].rename(
        columns={"home_team": "team", "FTHome": "GF", "FTAway": "GA"}
    )
    away = matches_df[["season", "away_team", "FTAway", "FTHome"]].rename(
        columns={"away_team": "team", "FTAway": "GF", "FTHome": "GA"}
    )
    df = pd.concat([home, away])

    # Calculate W, D, L, and Points
    df["MP"] = 1
    df["W"] = (df["GF"] > df["GA"]).astype(int)
    df["D"] = (df["GF"] == df["GA"]).astype(int)
    df["L"] = (df["GF"] < df["GA"]).astype(int)
    df["Pts"] = df["W"] * 3 + df["D"]

    standings = df.groupby(["season", "team"])[["MP", "W", "D", "L", "GF", "GA", "Pts"]].sum()
    standings["GD"] = standings["GF"] - standings["GA"]
    standings = standings.sort_values(by=["season", "Pts", "GD", "GF"], ascending=False)

    # If MP of a team in previous seasons is not 38, print a warning message
    current_season = standings.index.get_level_values(0).max()
    for season in standings.index.get_level_values(0).unique():
        season_standings = standings.loc[season]
        if season != current_season and (season_standings["MP"] != 38).any():
            print(f"\nWarning: Not all teams played 38 matches in season {season}.")
            print(season_standings[season_standings["MP"] != 38])

    print('\nStandings:')
    print(standings)

    # Save the standings to a CSV file
    standings.to_csv(XGABORA_PATH + "standings.csv")


process_match_stats()
calculate_standings()