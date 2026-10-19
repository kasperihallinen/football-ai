import random
import time
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os
from pathlib import Path
from teams import PREMIER_LEAGUE_TEAMS

# Folder where the URLs of the preview articles for Premier League matches are stored. 
# If this folder exists, we will read the URLs from it instead of scraping them again.
PREVIEW_ARTICLE_URLS_FOLDER = './data/preview_article_urls'
# The file name format for the files where the URLs of the preview articles will be stored.
PREVIEW_ARTICLE_URL_FILE_FORMAT = os.path.join(PREVIEW_ARTICLE_URLS_FOLDER, 'preview_article_urls_{year}.csv')
# The first match preview of the 2018-2019 season. We will drop all articles that were written before this.
LAST_PREVIEW = 'https://www.sportsmole.co.uk/football/man-city/preview/man-city-vs-chelsea-prediction-team-news-lineups_332136.html'
# The parent folder where the HTML files of the preview articles will be saved.
BASE_OUTPUT_FOLDER = './data/raw_html_previews'
# The yearly folder name format where the HTML files of the preview articles will be saved.
YEARLY_OUTPUT_FOLDER_FORMAT = os.path.join(BASE_OUTPUT_FOLDER, '{year}')
# Possible leagues or cups that we want to ignore that could include Premier League teams.
IGNORED_LEAGUES = ['fa-cup', 'league-cup', 'champions-league', 'europa-league', 
                   'europa-conference-league', 'club-world-cup']

base_url = 'https://www.sportsmole.co.uk'
years = list(range(2018, 2028))  # Years from 2018 to 2027
# dict that maps the years to the teams that participated in the Premier League during that year
year_to_teams = defaultdict(lambda: defaultdict(list))
for year in years:
    for team, values in PREMIER_LEAGUE_TEAMS.items():
        # The years in values['seasons'] represent the start of the season. 
        # To get all the years that the team played in the Premier League, 
        # we need to add 1 to each year to get also the end of the season.
        if year in values['seasons'].union({year + 1 for year in values['seasons']}):
            year_to_teams[year]['path_names'].append(team)
            year_to_teams[year]['all_names'].extend(values['all_names'])

# Simulate organic traffic coming from a search engine
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}
# Subsequent queries now auto-manage cookies correctly
session = requests.Session()
session.headers.update(headers)  # Appends your browser headers globally

urls_df = pd.DataFrame(columns=['Preview Article URLs', 'Year'])

# Read the files from the PREVIEW_ARTICLE_URLS_FOLDER if it exists and is not empty.
if os.path.exists(PREVIEW_ARTICLE_URLS_FOLDER) and os.listdir(PREVIEW_ARTICLE_URLS_FOLDER):
    print(f"Reading preview article URLs from {PREVIEW_ARTICLE_URLS_FOLDER}...")
    for year in years:
        file_path = PREVIEW_ARTICLE_URL_FILE_FORMAT.format(year=year)
        if os.path.exists(file_path):
            temp_df = pd.read_csv(file_path)
            temp_df['Year'] = year
            urls_df = pd.concat([urls_df, temp_df], ignore_index=True)

# Else, scrape the preview article URLs from the Sports Mole website
else:
    print("\nScraping preview article URLs from the sitemaps...")

    # Create the folder to store the preview article URLs if it doesn't exist
    Path(PREVIEW_ARTICLE_URLS_FOLDER).mkdir(exist_ok=True)

    # the URL of the sitemap index which contains links to individual sitemaps
    sitemap_index = f'{base_url}/sitemap_index.xml'
    response = session.get(sitemap_index)
    soup = BeautifulSoup(response.content, 'xml')

    # Find all the sitemap URLs in the sitemap index
    sitemaps = soup.find_all('loc')
    # Keep only the URLs that contain the word "articles"
    sitemaps = [s for s in sitemaps if 'articles' in s.text]
    # Keep only the URLs that contain a year from 2018 to 2027
    sitemaps = [s for s in sitemaps if any(str(year) in s.text for year in years)]
    print(f"Found {len(sitemaps)} article sitemaps from {min(years)} to {max(years)}.")
    for sitemap in sitemaps:
        print(sitemap.text)

    # Now, for each sitemap, we will go through the article URLs and check if they contain any of 
    # the Premier League teams for that year.
    for sitemap in sitemaps:
        preview_article_urls = []
        sitemap_url = sitemap.text
        response = session.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')

        # Extract the year from the sitemap URL
        year_match = re.search(r'(\d{4})', sitemap_url)
        if year_match:
            year = int(year_match.group(1))
            teams_for_year = year_to_teams[year]
            print(f"Checking articles for the year {year}")

            article_urls = [loc.text for loc in soup.find_all('loc')]
            # Keep only the article URLs that contain the paths "/football/" and "/preview/" 
            # and does not contain any of the ignored leagues or cups
            article_urls = [url for url in article_urls 
                            if '/football/' in url and '/preview/' in url and 
                            not any(ignored in url for ignored in IGNORED_LEAGUES)]

            for article_url in article_urls:
                # Skip the article if it does not contain any of the Premier League teams for that year
                if all(f'/{team}/' not in article_url for team in teams_for_year['path_names']):
                    continue
                # Also skip the article if it does not contain the names of two premier league 
                # teams in the format "team-1-vs-team-2".
                vs_match = re.search(r'([^/]+)-vs-([^/_]+?)(?=-prediction)', article_url)
                if not vs_match or \
                    not vs_match.group(1) in teams_for_year['all_names'] \
                        or not vs_match.group(2) in teams_for_year['all_names']:
                    continue

                preview_article_urls.append(article_url)

                # Skip the articles that are after the last article we want to scrape
                if article_url == LAST_PREVIEW:
                    break

            temp_df = pd.DataFrame(preview_article_urls, columns=['Preview Article URLs', 'Year'])
            # Drop duplicate URLs if any
            temp_df.drop_duplicates(inplace=True)
            temp_df['Year'] = year
            urls_df = pd.concat([urls_df, temp_df], ignore_index=True)
            # Drop Year from temp_df before saving to CSV
            temp_df.drop(columns=['Year'], inplace=True)
            # Save the preview article URLs to a CSV file
            temp_df.to_csv(PREVIEW_ARTICLE_URL_FILE_FORMAT.format(year=year), index=False)
        
        time.sleep(random.uniform(0.5, 1.5))  # Sleep to avoid overwhelming the server

print(f"\nFound {len(urls_df)} preview article URLs from {min(years)} to {max(years)}.")

# Create the base output folder if it doesn't exist
Path(BASE_OUTPUT_FOLDER).mkdir(exist_ok=True)
# For each year, create a folder to store the HTML files of the preview articles
for year in years:
    output_folder = YEARLY_OUTPUT_FOLDER_FORMAT.format(year=year)
    Path(output_folder).mkdir(exist_ok=True)

    # Get the preview article URLs for the current year
    temp_df = urls_df[urls_df['Year'] == year]

    # Get the names of the files that are already in the folder and drop them from the list of URLs to scrape
    existing_files = [f for f in os.listdir(output_folder) if f.endswith('.html')]
    print(f"\nFound {len(existing_files)} existing HTML files in the output folder for year {year}. They will be skipped.")
    temp_df = temp_df[~temp_df['Preview Article URLs'].str.split('/').str[-1].isin(existing_files)]
    # Reset the index of the temp_df after dropping the existing files
    temp_df.reset_index(drop=True, inplace=True)

    print(f"Scraping {len(temp_df)} preview articles for year {year}...")

    for index, row in temp_df.iterrows():
        article_url = row['Preview Article URLs']
        response = session.get(article_url)
        if response.status_code == 200:
            # Save the HTML content to a file
            article_id = article_url.split('/')[-1].replace('.html', '')
            output_file = os.path.join(output_folder, f'{article_id}.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            if index % 10 == 0 or index == len(temp_df) - 1:
                print(f"Scraped {index + 1}/{len(temp_df)} articles")
        else:
            print(f"Failed to retrieve {article_url}: Status code {response.status_code}")

        time.sleep(random.uniform(1, 3))  # Sleep to avoid overwhelming the server