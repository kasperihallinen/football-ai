# Premier League teams and their corresponding years of participation in the league from 2012 to 2026. 
# The keys are the team names as they appear in the Sports Mole URL paths, e.g. /brighton-and-hove-albion/.
# vs_name is the name of the team as it appears in the "team1-vs-team2" part of the Sports Mole filenames, 
# e.g. brighton-vs-millwall_59804.html.
# The year can represent either the start or end of the season, depending on the context. 
# For example, "2012" can represent the 2011-2012 season or the 2012-2013 season. 
# all_names is a list of all the names that Sports Mole can use to refer to the team in their URLs.
PREMIER_LEAGUE_TEAMS = {
    "arsenal": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['arsenal'],
    },
    "aston-villa": {
        "seasons": {2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['aston-villa'],
    },
    "bournemouth": {
        "seasons": {2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['bournemouth'],
    },
    "brentford": {
        "seasons": {2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['brentford'],
    },
    "brighton-and-hove-albion": {
        "seasons": {2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['brighton-and-hove-albion', 'brighton', 'brighton-&-hove-albion'],
    },
    "burnley": {
        "seasons": {2014, 2016, 2017, 2018, 2019, 2020, 2021, 2023, 2025},
        "all_names": ['burnley'],
    },
    "cardiff-city": {
        "seasons": {2013, 2018},
        "all_names": ['cardiff-city', 'cardiff'],
    },
    "chelsea": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['chelsea'],
    },
    "coventry-city": {
        "seasons": {2026},
        "all_names": ['coventry-city', 'coventry'],
    },
    "crystal-palace": {
        "seasons": {2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['crystal-palace', 'palace'],
    },
    "everton": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['everton'],
    },
    "fulham": {
        "seasons": {2012, 2013, 2018, 2020, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['fulham'],
    },
    "huddersfield-town": {
        "seasons": {2017, 2018},
        "all_names": ['huddersfield-town', 'huddersfield'],
    },
    "hull-city": {
        "seasons": {2013, 2014, 2016, 2026},
        "all_names": ['hull-city', 'hull'],
    },
    "ipswich-town": {
        "seasons": {2024, 2026},
        "all_names": ['ipswich-town', 'ipswich'],
    },
    "leeds-united": {
        "seasons": {2020, 2021, 2022, 2025, 2026},
        "all_names": ['leeds-united', 'leeds'],
    },
    "leicester-city": {
        "seasons": {2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024},
        "all_names": ['leicester-city', 'leicester'],
    },
    "liverpool": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['liverpool'],
    },
    "luton-town": {
        "seasons": {2023},
        "all_names": ['luton-town', 'luton'],
    },
    "man-city": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['man-city', 'manchester-city'],
    },
    "man-utd": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['man-utd', 'manchester-united'],
    },
    "middlesbrough": {
        "seasons": {2016},
        "all_names": ['middlesbrough'],
    },
    "newcastle-united": {
        "seasons": {2012, 2013, 2014, 2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['newcastle-united', 'newcastle'],
    },
    "norwich-city": {
        "seasons": {2012, 2013, 2015, 2019, 2021},
        "all_names": ['norwich-city', 'norwich'],
    },
    "nottingham-forest": {
        "seasons": {2022, 2023, 2024, 2025, 2026},
        "all_names": ['nottingham-forest', 'nottm-forest'],
    },
    "qpr": {
        "seasons": {2012, 2014},
        "all_names": ['qpr', 'queens-park-rangers'],
    },
    "reading": {
        "seasons": {2012},
        "all_names": ['reading'],
    },
    "sheffield-united": {
        "seasons": {2019, 2020, 2023},
        "all_names": ['sheffield-united', 'sheff-utd'],
    },
    "southampton": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024},
        "all_names": ['southampton'],
    },
    "stoke-city": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017},
        "all_names": ['stoke-city', 'stoke'],
    },
    "sunderland": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2025, 2026},
        "all_names": ['sunderland'],
    },
    "swansea-city": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017},
        "all_names": ['swansea-city', 'swansea'],
    },
    "spurs": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['spurs', 'tottenham-hotspur', 'tottenham'],
    },
    "watford": {
        "seasons": {2015, 2016, 2017, 2018, 2019, 2021},
        "all_names": ['watford'],
    },
    "west-brom-albion": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2020},
        "all_names": ['west-brom-albion', 'west-brom'],
    },
    "west-ham-united": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025},
        "all_names": ['west-ham-united', 'west-ham'],
    },
    "wigan-athletic": {
        "seasons": {2012},
        "all_names": ['wigan-athletic', 'wigan'],
    },
    "wolves": {
        "seasons": {2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025},
        "all_names": ['wolves', 'wolverhampton'],
    }
}
