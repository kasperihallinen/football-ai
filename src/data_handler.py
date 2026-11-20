# This file is responsible for processing and merging the data fetched from
# various sources, such as Sports Mole, FBref, and SoFIFA.
# It contains functions to clean, transform, and combine the data into a
# unified format for further analysis and modeling.

import pandas as pd

FBREF_PATH = "./data/fbref/"
XGABORA_PATH = "./data/xgabora_github/"


def calculate_standings():
    """
    Calculate the final standings for each season of the Premier League based
    on match results.
    The resulting csv contains the following columns: season, matches played
    (MP), wins (W), draws (D), losses (L), goals for (GF), goals against (GA),
    points (Pts) and goal difference (GD).
    """

    output_file = XGABORA_PATH + "standings.csv"
    matches_df = pd.read_csv(XGABORA_PATH + "match_data.csv")

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

    standings = df.groupby(["season", "team"])[
        ["MP", "W", "D", "L", "GF", "GA", "Pts"]
    ].sum()
    standings["GD"] = standings["GF"] - standings["GA"]
    standings = standings.sort_values(
        by=["season", "Pts", "GD", "GF"], ascending=False
    )

    # If MP of a team in previous seasons is not 38, print a warning message
    current_season = standings.index.get_level_values(0).max()
    for season in standings.index.get_level_values(0).unique():
        season_standings = standings.loc[season]
        if season != current_season and (season_standings["MP"] != 38).any():
            print(
                f"\nWarning: Not all teams played 38 matches in season {season}."
            )
            print(season_standings[season_standings["MP"] != 38])

    print("\nStandings:")
    print(standings)

    # Save the standings to a CSV file
    standings.to_csv(output_file)


# calculate_standings()
