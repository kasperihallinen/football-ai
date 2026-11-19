from collections import defaultdict
import pandas as pd

# Premier League teams and their corresponding years of participation in the league from 2012 to 2026. 
# The years represent the start of the season. 
# all_names is a list of all the names that all the sources of this project can use to refer to the teams.
# sports_mole_name is the team name as it appears in the Sports Mole URL paths, e.g. /brighton-and-hove-albion/.
TEAMS = {
    "arsenal": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['arsenal', 'arsenal fc'],
        "sports_mole_name": 'arsenal',
        "home_venue": 'Emirates Stadium',
    },
    "aston villa": {
        "seasons": {2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['aston villa'],
        "sports_mole_name": 'aston-villa',
        "home_venue": 'Villa Park',
    },
    "bournemouth": {
        "seasons": {2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['bournemouth', 'afc bournemouth'],
        "sports_mole_name": 'bournemouth',
        "home_venue": 'Vitality Stadium',
    },
    "brentford": {
        "seasons": {2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['brentford'],
        "sports_mole_name": 'brentford',
        "home_venue": ['Brentford Community Stadium', 'Gtech Community Stadium'],
    },
    "brighton": {
        "seasons": {2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['brighton', 'brighton and hove albion', 'brighton & hove albion'],
        "sports_mole_name": 'brighton-and-hove-albion',
        "home_venue": ['The American Express Community Stadium', 'The American Express Stadium'],
    },
    "burnley": {
        "seasons": {2014, 2016, 2017, 2018, 2019, 2020, 2021, 2023, 2025},
        "all_names": ['burnley'],
        "sports_mole_name": 'burnley',
        "home_venue": 'Turf Moor',
    },
    "cardiff": {
        "seasons": {2013, 2018},
        "all_names": ['cardiff', 'cardiff city'],
        "sports_mole_name": 'cardiff-city',
        "home_venue": 'Cardiff City Stadium',
    },
    "chelsea": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['chelsea', 'chelsea fc'],
        "sports_mole_name": 'chelsea',
        "home_venue": 'Stamford Bridge',
    },
    "coventry": {
        "seasons": {2026},
        "all_names": ['coventry', 'coventry city'],
        "sports_mole_name": 'coventry-city',
    },
    "crystal palace": {
        "seasons": {2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['crystal palace', 'palace'],
        "sports_mole_name": 'crystal-palace',
        "home_venue": 'Selhurst Park',
    },
    "everton": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['everton', 'everton fc'],
        "sports_mole_name": 'everton',
        "home_venue": ['Goodison Park', 'Hill Dickinson Stadium'],
    },
    "fulham": {
        "seasons": {2012, 2013, 2018, 2020, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['fulham', 'fulham fc'],
        "sports_mole_name": 'fulham',
        "home_venue": 'Craven Cottage',
    },
    "huddersfield": {
        "seasons": {2017, 2018},
        "all_names": ['huddersfield', 'huddersfield town'],
        "sports_mole_name": 'huddersfield-town',
        "home_venue": "The John Smith's Stadium",
    },
    "hull": {
        "seasons": {2013, 2014, 2016, 2026},
        "all_names": ['hull', 'hull city'],
        "sports_mole_name": 'hull-city',
    },
    "ipswich": {
        "seasons": {2024, 2026},
        "all_names": ['ipswich', 'ipswich town'],
        "sports_mole_name": 'ipswich-town',
        "home_venue": 'Portman Road Stadium',
    },
    "leeds": {
        "seasons": {2020, 2021, 2022, 2025, 2026},
        "all_names": ['leeds', 'leeds united'],
        "sports_mole_name": 'leeds-united',
        "home_venue": 'Elland Road',
    },
    "leicester": {
        "seasons": {2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024},
        "all_names": ['leicester', 'leicester city'],
        "sports_mole_name": 'leicester-city',
        "home_venue": 'King Power Stadium'
    },
    "liverpool": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['liverpool', 'liverpool fc'],
        "sports_mole_name": 'liverpool',
        "home_venue": 'Anfield',
    },
    "luton": {
        "seasons": {2023},
        "all_names": ['luton', 'luton town'],
        "sports_mole_name": 'luton-town',
        "home_venue": 'Kenilworth Road Stadium',
    },
    "man city": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['man city', 'manchester city'],
        "sports_mole_name": 'man-city',
        "home_venue": 'Etihad Stadium',
    },
    "man utd": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['man utd', 'man united', 'manchester utd', 'manchester united'],
        "sports_mole_name": 'man-utd',
        "home_venue": 'Old Trafford',
    },
    "middlesbrough": {
        "seasons": {2016},
        "all_names": ['middlesbrough', 'middlesbrough fc'],
        "sports_mole_name": 'middlesbrough',
    },
    "newcastle": {
        "seasons": {2012, 2013, 2014, 2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['newcastle', 'newcastle united'],
        "sports_mole_name": 'newcastle-united',
        "home_venue": ["St James' Park"],
    },
    "norwich": {
        "seasons": {2012, 2013, 2015, 2019, 2021},
        "all_names": ['norwich', 'norwich city'],
        "sports_mole_name": 'norwich-city',
        "home_venue": 'Carrow Road',
    },
    "nottingham forest": {
        "seasons": {2022, 2023, 2024, 2025, 2026},
        "all_names": ['nottingham forest', 'nottm forest', "nott'm forest", 'forest'],
        "sports_mole_name": 'nottingham-forest',
        "home_venue": 'The City Ground',
    },
    "qpr": {
        "seasons": {2012, 2014},
        "all_names": ['qpr', 'queens park rangers'],
        "sports_mole_name": 'qpr',
    },
    "reading": {
        "seasons": {2012},
        "all_names": ['reading'],
        "sports_mole_name": 'reading',
    },
    "sheffield united": {
        "seasons": {2019, 2020, 2023},
        "all_names": ['sheffield united', 'sheff utd'],
        "sports_mole_name": 'sheffield-united',
        "home_venue": 'Bramall Lane',
    },
    "southampton": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024},
        "all_names": ['southampton', 'southampton fc'],
        "sports_mole_name": 'southampton',
        "home_venue": ["St Mary's Stadium"],
    },
    "stoke": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017},
        "all_names": ['stoke', 'stoke city'],
        "sports_mole_name": 'stoke-city',
    },
    "sunderland": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2025, 2026},
        "all_names": ['sunderland', 'sunderland afc'],
        "sports_mole_name": 'sunderland',
        "home_venue": 'Stadium of Light',
    },
    "swansea": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017},
        "all_names": ['swansea', 'swansea city'],
        "sports_mole_name": 'swansea-city',
    },
    "tottenham": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026},
        "all_names": ['tottenham', 'spurs', 'tottenham hotspur'],
        "sports_mole_name": 'spurs',
        "home_venue": ['Tottenham Hotspur Stadium', 'Wembley Stadium'],
    },
    "watford": {
        "seasons": {2015, 2016, 2017, 2018, 2019, 2021},
        "all_names": ['watford'],
        "sports_mole_name": 'watford',
        "home_venue": 'Vicarage Road Stadium',
    },
    "west brom": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2020},
        "all_names": ['west brom', 'west brom albion', 'west bromwich albion'],
        "sports_mole_name": 'west-brom-albion',
        "home_venue": 'The Hawthorns',
    },
    "west ham": {
        "seasons": {2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025},
        "all_names": ['west ham', 'west ham united'],
        "sports_mole_name": 'west-ham-united',
        "home_venue": 'London Stadium',
    },
    "wigan": {
        "seasons": {2012},
        "all_names": ['wigan', 'wigan athletic'],
        "sports_mole_name": 'wigan-athletic',
    },
    "wolves": {
        "seasons": {2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025},
        "all_names": ['wolves', 'wolverhampton', 'wolverhampton wanderers'],
        "sports_mole_name": 'wolves',
        "home_venue": 'Molineux Stadium',
    }
}

# Venue coordinates for all premier league stadiums from season 2018-2019 onwards. The keys are the stadium names, 
# and the values are tuples containing the latitude and longitude of each stadium.
VENUES = {
    "Anfield": (53.4308, -2.9608),
    "Bramall Lane": (53.3703, -1.4708),
    "Brentford Community Stadium": (51.4907, -0.2890),
    "Cardiff City Stadium": (51.4728, -3.2031),
    "Carrow Road": (52.6222, 1.3092),
    "Craven Cottage": (51.4750, -0.2217),
    "Elland Road": (53.7778, -1.5721),
    "Emirates Stadium": (51.5550, -0.1086),
    "Etihad Stadium": (53.4831, -2.2004),
    "Goodison Park": (53.4389, -2.9664),
    "Gtech Community Stadium": (51.4908, -0.2890),
    "Hill Dickinson Stadium": (53.4251, -3.0028),
    "Kenilworth Road Stadium": (51.8842, -0.4317),
    "King Power Stadium": (52.6206, -1.1422),
    "London Stadium": (51.5388, -0.0171),
    "Molineux Stadium": (52.5903, -2.1303),
    "Old Trafford": (53.4631, -2.2914),
    "Portman Road Stadium": (52.0550, 1.1453),
    "Selhurst Park": (51.3983, -0.0856),
    "St James' Park": (54.9752, -1.6225),
    "St Mary's Stadium": (50.9061, -1.3917),
    "Stadium of Light": (54.9145, -1.3886),
    "Stamford Bridge": (51.4817, -0.1911),
    "The American Express Stadium": (50.8618, -0.0844),
    "The City Ground": (52.9400, -1.1328),
    "The Hawthorns": (52.5092, -1.9639),
    "The John Smith's Stadium": (53.6542, -1.7692),
    "Tottenham Hotspur Stadium": (51.6044, -0.0664),
    "Turf Moor": (53.7891, -2.2305),
    "Vicarage Road Stadium": (51.6499, -0.4021),
    "Villa Park": (52.5090, -1.8840),
    "Vitality Stadium": (50.7356, -1.8386),
    "Wembley Stadium": (51.5558, -0.2797)
}

# The start and end dates of the Premier League seasons from 2017-2018 to 2025-2026. 
# The keys are the start years of the seasons,
# and the values are tuples containing the start and end dates of each season in YYYY-MM-DD
SEASONS = {
    2017: {
        'dates': ('2017-08-11', '2018-05-13'),
        'fifa_release': '2017-09-29'
    },
    2018: {
        'dates': ('2018-08-10', '2019-05-12'), 
        'fifa_release': '2018-09-28'
        },
    2019: {
        'dates': ('2019-08-09', '2020-07-26'), 
        'fifa_release': '2019-09-27'
    },
    2020: {
        'dates': ('2020-09-12', '2021-05-23'), 
        'fifa_release': '2020-10-09'
    },
    2021: {
        'dates': ('2021-08-13', '2022-05-22'), 
        'fifa_release': '2021-10-01'
    },
    2022: {
        'dates': ('2022-08-05', '2023-05-28'), 
        'fifa_release': '2022-09-30'
    },
    2023: {
        'dates': ('2023-08-11', '2024-05-19'), 
        'fifa_release': '2023-09-29'
    },
    2024: {
        'dates': ('2024-08-16', '2025-05-25'), 
        'fifa_release': '2024-09-27'
    },
    2025: {
        'dates': ('2025-08-15', '2026-05-24'), 
        'fifa_release': '2025-09-26'
    },
}


def get_all_teams(use_hyphens=False):
    """
    Get all the Premier League team names from the teams module.
    Returns a list of all the names that all the sources of this project can use to refer to the teams.
    If use_hyphens is True, the names will use hyphens instead of spaces.
    """
    premier_league_teams = []
    for team, data in TEAMS.items():
        if use_hyphens:
            # Use hyphens instead of spaces
            all_names = [name.replace(' ', '-') for name in data["all_names"]]
        else:
            # Use spaces instead of hyphens
            all_names = [name.replace('-', ' ') for name in data["all_names"]]
        premier_league_teams.extend(all_names)
    return premier_league_teams


def get_year_to_teams(years=range(2017, 2028)):
    '''
    Get a dictionary that maps the years to the teams that participated in the Premier League during that year.
    The years represent the start of the season.
    The returned dictionary has the following structure:
    {
        year: {
            'sports_mole_names': [list of team names as they appear in the Sports Mole URL paths],
            'all_names': [list of all the names that all the sources of this project can use to refer to the teams]
        },
        ...
    }
    '''
    # dict that maps the years to the teams that participated in the Premier League during that year
    year_to_teams = defaultdict(lambda: defaultdict(list))
    for year in years:
        for team, values in TEAMS.items():
            # The years in values['seasons'] represent the start of the season. 
            # To get all the years that the team played in the Premier League, 
            # we need to add 1 to each year to get also the end of the season.
            if year in values['seasons'].union({year + 1 for year in values['seasons']}):
                year_to_teams[year]['sports_mole_names'].append(values['sports_mole_name'])
                year_to_teams[year]['all_names'].extend(values['all_names'])

    return year_to_teams


def unify_team_names(df, team_column):
    """
    Unify the team names in the given DataFrame column to the standardized names from the teams module.
    This function modifies the DataFrame in place.
    """
    for team_key, team_info in TEAMS.items():
        for name in team_info["all_names"]:
            df.loc[df[team_column].str.lower() == name, team_column] = team_key


def get_unified_name(team_name):
    """
    Get the unified name for a given team name.
    If the team name is not found in the PREMIER_LEAGUE_TEAMS dictionary, return None.
    """
    for team_key, team_info in TEAMS.items():
        if team_name.lower() in [name.lower() for name in team_info["all_names"]]:
            return team_key
    return None