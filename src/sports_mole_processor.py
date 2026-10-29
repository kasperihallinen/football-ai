from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os
from pathlib import Path
import json
from teams import PREMIER_LEAGUE_TEAMS

# The parent folder where the HTML files of the preview articles are saved.
BASE_PREVIEW_FOLDER = './data/raw_html_previews'
# The parent folder where the data from the processed preview articles will be saved.
BASE_PROCESSED_FOLDER = './data/processed_previews'
# The raw articles were saved in yearly folders, but the processed data will be saved in seasonal folders, e.g. 2018_2019.
SEASONAL_PROCESSED_FOLDER_FORMAT = os.path.join(BASE_PROCESSED_FOLDER, '{year_1}_{year_2}')
# Phrases that Sports Mole uses to refer to the recent form of the teams.
FORM_PHRASES = ['form:', 'form in Premier League:', 'form in the Premier League:',
                'form (all competitions)', 'form (pre-season friendlies)', 'pre-season:', 
                'pre-season form']
FORM_REGEX = re.compile('|'.join(re.escape(text) for text in FORM_PHRASES))
# Matches that are missing the recent form sections
MISSING_RECENT_FORM_MATCHES = [
    'bournemouth-vs-fulham-prediction-team-news-lineups_532103.html',
    'spurs-vs-man-city-prediction-team-news-lineups_543465.html'
]
# Remove everything starting from these phrases in the article text, as they are not relevant to the match preview.
REMOVE_STARTING_FROM_PHRASES = [
    'For data analysis of the most likely results',
    'For additional data used by our team',
    'Top tip',
    'Top betting tip',
]   
# Years to process. Change this list to process other years.
YEARS_TO_PROCESS = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']

# for folder_name in folder_names:
for folder_name in YEARS_TO_PROCESS:
    year = int(folder_name)
    print(f"Processing preview articles for year {year}...")

    # Create the processed folders for the seasons starting previous year and this year if they don't exist.
    processed_folder_1 = SEASONAL_PROCESSED_FOLDER_FORMAT.format(year_1=year - 1, year_2=year)
    processed_folder_2 = SEASONAL_PROCESSED_FOLDER_FORMAT.format(year_1=year, year_2=year + 1)
    Path(processed_folder_1).mkdir(parents=True, exist_ok=True)
    Path(processed_folder_2).mkdir(parents=True, exist_ok=True)

    yearly_preview_folder = os.path.join(BASE_PREVIEW_FOLDER, folder_name)

    # Get the list of HTML files in the yearly preview folder.
    html_files = [f for f in os.listdir(yearly_preview_folder) if f.endswith('.html')]
    non_premier_league_matches = 0
    too_old_articles = 0
    valid_matches = 0

    for html_file in html_files:
        html_file_path = os.path.join(yearly_preview_folder, html_file)
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Get the <div class="header"> and extract the text from it.
        header_div = soup.find('div', class_='header')
        header_text = header_div.get_text(strip=True) if header_div else 'N/A'

        # Skip the file if the header text does not contain "Premier League"
        if "Premier League" not in header_text:
            non_premier_league_matches += 1
            continue

        # Get the <time itemprop="datePublished"> element and its datetime attribute.
        published_time_element = soup.find('time', itemprop='datePublished')
        if not published_time_element:
            print(f"Warning: Could not find <time itemprop='datePublished'> in file {html_file_path}.")
            exit(1)
        published_datetime = published_time_element.get('datetime')
        if not published_datetime:
            print(f"Warning: Could not find datetime attribute in <time> element in file {html_file_path}.")
            exit(1)
        # The published datetime is in the format "2021-12-16T18:07:00+00:00". 
        # We don't need the timezone information, so we will remove it and parse the datetime.
        published_datetime = published_datetime.split('+')[0]
        try:
            published_datetime_obj = datetime.strptime(published_datetime, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            print(f"Warning: Could not parse published datetime '{published_datetime}' in file {html_file_path}.")
            exit(1)

        # Get the <div class="date"> and extract the text from it.
        match_date_div = soup.find('div', class_='date')
        match_date_text = match_date_div.get_text(strip=True) if match_date_div else 'N/A'
        # The dates are in the format "Dec 22, 2018 12.30pm". We will convert them to the format "YYYY-MM-DD".
        try:
            match_date_obj = datetime.strptime(match_date_text, '%b %d, %Y %I.%M%p')
            match_date_formatted = match_date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"Warning: Could not parse date '{match_date_text}' in file {html_file_path}.")
            exit(1)

        # Some of the matches have been postponed so they have multiple preview articles. 
        # If there are more than two weeks between the published date of the article and the date of the match,
        # we will skip the article.
        if abs((match_date_obj - published_datetime_obj).days) > 14:
            too_old_articles += 1
            continue

        # If the match date is before August 1st of the year, it belongs to the previous season. 
        # Otherwise, it belongs to the current season.
        if match_date_obj < datetime(year, 8, 1):
            season_year_1 = year - 1
            season_year_2 = year
        else:
            season_year_1 = year
            season_year_2 = year + 1

        # Get the title from <h1 class="sm-article-title">
        h1_title = soup.find('h1', class_='sm-article-title')
        h1_text = h1_title.get_text(strip=True) if h1_title else 'N/A'
        if h1_text == 'N/A':
            print(f"Warning: Could not find <h1 class='sm-article-title'> in file {html_file_path}.")
            exit(1)

        # Get the article body from <div class="sm-article-body"
        article_body = soup.find('div', class_='sm-article-body')
        if not article_body:
            print(f"Warning: Could not find <div class='sm-article-body'> in file {html_file_path}.")
            exit(1)

        # Get the <h2 class="sm_center"> that contains the text "We say:" and remove it from article_body
        we_say_h2 = article_body.find('h2', class_='sm_center', string=re.compile(r'We say:', re.IGNORECASE))
        if we_say_h2:
            we_say_h2.decompose()
        else:
            print(f"Warning: Could not find <h2 class='sm_center'> with text 'We say:' in file {html_file_path}.")
            exit(1)

        # Get the <div class="sm-image-copyright"> elemenents and remove them from article_body
        image_copyright_divs = article_body.find_all('div', class_='sm-image-copyright')
        for div in image_copyright_divs:
            div.decompose()

        # Get the team names from the <div class="team-title"> elements.
        team_title_divs = soup.find_all('div', class_='team-title')
        team_names = [div.get_text(strip=True).lower().replace(' ', '-') for div in team_title_divs]
        # Print a warning if there are not exactly 2 team names.
        if len(team_names) != 2:
            print(f"Warning: Could not find exactly 2 team names in file {html_file_path}.")
            print(f"Team names found: {team_names}")
            exit(1)
        found = False
        for i, team_name in enumerate(team_names):
            # Check if the team name is in the PREMIER_LEAGUE_TEAMS dictionary.
            if team_name not in PREMIER_LEAGUE_TEAMS:
                # If the team name is not found, check if it is in the all_names list of any team.
                for team_key, team_data in PREMIER_LEAGUE_TEAMS.items():
                    if team_name in team_data['all_names']:
                        # If found, replace the team name with the key of the team.
                        team_names[i] = team_key
                        found = True
                        break

                if not found:
                    print(f"Warning: Team name not found in PREMIER_LEAGUE_TEAMS for file {html_file_path}.")
                    print(f"Team names: {team_names}")
                    exit(1)

        # Get all the names that Sports Mole can use to refer to the teams.
        home_team_names = PREMIER_LEAGUE_TEAMS[team_names[0]]['all_names']
        away_team_names = PREMIER_LEAGUE_TEAMS[team_names[1]]['all_names']
        # Form the names without the dashes, e.g. "brighton-and-hove-albion" becomes "brighton and hove albion".
        home_team_names = [name.replace('-', ' ') for name in home_team_names]
        away_team_names = [name.replace('-', ' ') for name in away_team_names]
        all_team_names = home_team_names + away_team_names

        # Get all <h2> elements and add a dot and a new line before them, and a colon and a space after 
        # them in the article_body
        h2_elements = article_body.find_all('h2')
        home_h2 = None
        away_h2 = None
        for h2 in h2_elements:
            # Get the <h2> element that contains the home team name
            if any(home_team_name in h2.get_text(strip=True).lower() for home_team_name in home_team_names):
                home_h2 = h2
            # Get the <h2> element that contains the away team name
            elif any(away_team_name in h2.get_text(strip=True).lower() for away_team_name in away_team_names):
                away_h2 = h2

            h2.insert_before('\n')
            h2.insert_after(': ')

        # If the article is structured in a way that there are separate sections for the home and away teams, 
        # we will prepend the team names to the recent form elements if they are not already present. 
        # This is to ensure that the recent form elements are clearly associated with the correct team.
        if home_h2 and away_h2:
            # Print a warning if away_h2 is not found after home_h2 in the article_body, as this is not the 
            # expected structure.
            if away_h2 not in home_h2.find_all_next():
                print(f"Warning: Away team section not found after home team section in {html_file_path}.")
                exit(1)
            # Get the recent form elements for the home team
            for element in away_h2.previous_elements:
                if element.name and element.string and FORM_REGEX.search(element.string) and \
                    not any(team_name in element.string.lower() for team_name in all_team_names):
                    # Prepend the home team name (capitalize the first letter of the team name)
                    element.string = f"| {home_team_names[0].capitalize()} {element.string}"

            # Get the recent form elements for the away team
            for element in away_h2.next_elements:
                if element.name and element.string and FORM_REGEX.search(element.string) and \
                    not any(team_name in element.string.lower() for team_name in all_team_names):
                    # Prepend the away team name (capitalize the first letter of the team name)
                    element.string = f"| {away_team_names[0].capitalize()} {element.string}"

        # Get the article text from the <div class="sm-article-body"> element.
        article_text = article_body.get_text(separator=' ', strip=True)
        # Remove everything starting from the phrases in REMOVE_STARTING_FROM_PHRASES
        for phrase in REMOVE_STARTING_FROM_PHRASES:
            article_text = article_text.split(phrase)[0].strip()
        # Split into words and strip leading/trailing whitespace from each word.
        article_text = h1_text + '. ' + ' '.join(article_text.split()).strip()

        # Print the article name if the article text is less than 1000 characters.
        if len(article_text) < 1000:
            print(f"Too short: {html_file}")

        # Get the <div class="value"> elements and extract the text from them. Those contain the scores
        value_divs = soup.find_all('div', class_='value')
        scores = [int(div.get_text(strip=True)) for div in value_divs]

        # Print a warning if the scores are not found or if there are not exactly 2 scores.
        if not scores or len(scores) != 2:
            print(f"Warning: Could not find exactly 2 scores in file {html_file_path}.")
            exit(1)

        if scores[0] > scores[1]:
            result = 'home'
        elif scores[0] < scores[1]:
            result = 'away'
        else:
            result = 'draw'

        # Create a dictionary with the extracted data.
        article_data = {
            'match_date': match_date_formatted,
            'season': f"{season_year_1}_{season_year_2}",
            'home_team': team_names[0],
            'away_team': team_names[1],
            'home_score': scores[0],
            'away_score': scores[1],
            'result': result,
            'article_url': html_file,
            'scraped_at': '2026-10-08',
            'article_text': article_text,
        }

        # Save the extracted data to a json file in the corresponding seasonal processed folder.
        output_folder = SEASONAL_PROCESSED_FOLDER_FORMAT.format(year_1=season_year_1, year_2=season_year_2)
        output_file = html_file.replace('-prediction-team-news-lineups', '').replace('.html', '.json')
        output_file_path = os.path.join(output_folder, output_file)

        # Write the extracted data to the json file with pretty printing.
        with open(output_file_path, 'w') as f:
            json.dump(article_data, f, indent=4)

        valid_matches += 1


    print(f"Number of too old articles skipped: {too_old_articles}")
    print(f"Number of non-Premier League articles skipped: {non_premier_league_matches}")
    print(f"Total number of valid matches: {valid_matches}")
