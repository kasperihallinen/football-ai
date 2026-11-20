# This file is responsible for processing and merging the data fetched from
# various sources, such as Sports Mole, FBref, and SoFIFA.
# It contains functions to clean, transform, and combine the data into a
# unified format for further analysis and modeling.

import pandas as pd

FBREF_PATH = "./data/fbref/"
XGABORA_PATH = "./data/xgabora_github/"


def calculate_cumulative_standings():
    """
    Calculate the standings before each matchday of the Premier League based on
    match results.
    The resulting csv contains the season, date, team, and the following
    cumulative stats before each matchday: matches played (MP), wins (CW), draws
    (CD), losses (CL), points (CPTS), goals for (CGF), goals against (CGA),
    goal difference (CGD), and rank.
    """
    output_file = XGABORA_PATH + "cumulative_standings.csv"
    df = pd.read_csv(XGABORA_PATH + "match_data.csv")

    # Ensure data is sorted chronologically
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["season", "date"]).reset_index(drop=True)
    df["match_id"] = df.index  # Unique ID to merge back later

    # Create Home perspective
    home_df = pd.DataFrame(
        {
            "match_id": df["match_id"],
            "season": df["season"],
            "date": df["date"],
            "team": df["home_team"],
            "GF": df["FTHome"],
            "GA": df["FTAway"],
        }
    )
    # Create Away perspective
    away_df = pd.DataFrame(
        {
            "match_id": df["match_id"],
            "season": df["season"],
            "date": df["date"],
            "team": df["away_team"],
            "GF": df["FTAway"],
            "GA": df["FTHome"],
        }
    )
    team_df = (
        pd.concat([home_df, away_df])
        .sort_values(["season", "date", "match_id"])
        .reset_index(drop=True)
    )

    # Calculate W, D, L, and Points
    team_df["W"] = (team_df["GF"] > team_df["GA"]).astype(int)
    team_df["D"] = (team_df["GF"] == team_df["GA"]).astype(int)
    team_df["L"] = (team_df["GF"] < team_df["GA"]).astype(int)
    team_df["PTS"] = team_df["W"] * 3 + team_df["D"]
    team_df["GD"] = team_df["GF"] - team_df["GA"]

    grouped = team_df.groupby(["season", "team"])

    # Calculate cumulative stats after each match
    team_df["MP"] = grouped.cumcount() + 1
    team_df["CW"] = grouped["W"].cumsum()
    team_df["CD"] = grouped["D"].cumsum()
    team_df["CL"] = grouped["L"].cumsum()
    team_df["CPTS"] = grouped["PTS"].cumsum()
    team_df["CGF"] = grouped["GF"].cumsum()
    team_df["CGA"] = grouped["GA"].cumsum()
    team_df["CGD"] = grouped["GD"].cumsum()

    # Get unique match dates per season
    dates = team_df[["season", "date"]].drop_duplicates()

    # Create a "Final Standings" date (1 day after the last match of each
    # season)
    final_dates = dates.groupby("season")["date"].max().reset_index()
    final_dates["date"] = final_dates["date"] + pd.Timedelta(days=1)

    # Combine regular matchdays with the final standings date
    all_dates = pd.concat(
        [dates, final_dates], ignore_index=True
    ).drop_duplicates()
    teams = team_df[["season", "team"]].drop_duplicates()

    # Cross-join dates and teams within each season to build a full timeline
    standings = pd.merge(all_dates, teams, on="season")

    # Merge the latest cumulative stats up to each date
    standings = pd.merge_asof(
        standings.sort_values("date"),
        team_df.sort_values("date"),
        on="date",
        by=["season", "team"],
        direction="backward",
        allow_exact_matches=False,
    ).fillna(
        {
            "MP": 0,
            "CW": 0,
            "CD": 0,
            "CL": 0,
            "CPTS": 0,
            "CGF": 0,
            "CGA": 0,
            "CGD": 0,
        }
    )

    # Create a tuple of tie-breakers (Points, Goal Difference, Goals For)
    standings["tie_breaker"] = list(
        zip(standings["CPTS"], standings["CGD"], standings["CGF"])
    )

    # Rank teams so identical tuples receive the same rank (e.g., 1, 2, 2, 4)
    standings["rank"] = (
        standings.groupby(["season", "date"])["tie_breaker"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # Drop the helper column
    standings = standings.drop(columns=["tie_breaker"])

    standings = standings.sort_values(["season", "date", "rank"])

    # Keep only the relevant columns
    standings = standings[
        [
            "season",
            "date",
            "team",
            "MP",
            "CW",
            "CD",
            "CL",
            "CPTS",
            "CGF",
            "CGA",
            "CGD",
            "rank",
        ]
    ]

    print("\nCumulative Standings:")
    print(standings.tail(20))

    print(f"\nSaving cumulative standings to {output_file}")
    standings.to_csv(output_file, index=False)


calculate_cumulative_standings()
