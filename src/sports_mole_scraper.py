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

# File that contains the URLs of the preview articles for Premier League matches from 2012 to 2027
PREVIEW_ARTICLES_FILE = 'preview_articles.csv'
# The first match preview of the 2012-2013 season. We will drop all articles that were written before this.
LAST_ARTICLE = 'https://www.sportsmole.co.uk/football/arsenal/preview/arsenal-vs-sunderland_40590.html'

base_url = 'https://www.sportsmole.co.uk'
years = list(range(2012, 2028))  # Years from 2012 to 2027

# Simulate organic traffic coming from a search engine
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",  # Simulates organic traffic coming from a search engine
    "Connection": "keep-alive"
}
# Subsequent queries now auto-manage cookies correctly
session = requests.Session()
session.headers.update(headers)  # Appends your browser headers globally

# Read the preview article URLs from the CSV file if it exists
if os.path.exists(PREVIEW_ARTICLES_FILE):
    urls_df = pd.read_csv(PREVIEW_ARTICLES_FILE)
# Else, scrape the preview article URLs from the Sports Mole website
else:
    # the URL of the sitemap index which contains links to individual sitemaps
    sitemap_index = f'{base_url}/sitemap_index.xml'
    response = session.get(sitemap_index)
    soup = BeautifulSoup(response.content, 'xml')

    # Find all the sitemap URLs in the sitemap index
    sitemaps = soup.find_all('loc')

    # Keep only the URLs that contain the word "articles"
    sitemaps = [s for s in sitemaps if 'articles' in s.text]
    # Keep only the URLs that contain a year from 2012 to 2027
    sitemaps = [s for s in sitemaps if any(str(year) in s.text for year in years)]
    print(f"Found {len(sitemaps)} article sitemaps from {min(years)} to {max(years)}.")
    for sitemap in sitemaps:
        print(sitemap.text)
    print("\nScraping preview article URLs from the sitemaps...")

    # dict that maps the years to the teams that participated in the Premier League during that year
    year_to_teams = defaultdict(list)
    for year in years:
        for team, team_years in PREMIER_LEAGUE_TEAMS.items():
            if year in team_years:
                year_to_teams[year].append(team)

    preview_article_urls = []

    # Now, for each sitemap, we will go through the article URLs and check if they contain any of the Premier League teams for that year.
    for sitemap in sitemaps:
        sitemap_url = sitemap.text
        response = session.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')

        article_urls = [loc.text for loc in soup.find_all('loc')]
        # Keep only the article URLs that contain the paths "/football/" and "/preview/" 
        # and does not contain "fa-cup" or "league-cup"
        article_urls = [url for url in article_urls 
                        if '/football/' in url and '/preview/' in url 
                        and 'fa-cup' not in url and 'league-cup' not in url]

        # Extract the year from the sitemap URL
        year_match = re.search(r'(\d{4})', sitemap_url)
        if year_match:
            year = int(year_match.group(1))
            teams_for_year = year_to_teams[year]
            print(f"Checking articles for the year {year}")

            for article_url in article_urls:
                # Check if any of the team names are in the article URL
                if any(f'/{team}/' in article_url for team in teams_for_year):
                    preview_article_urls.append(article_url)

        time.sleep(random.uniform(0.5, 1.5))  # Sleep to avoid overwhelming the server

    # Save the preview article URLs to a CSV file
    urls_df = pd.DataFrame(preview_article_urls, columns=['Preview Article URLs'])
    urls_df.to_csv(PREVIEW_ARTICLES_FILE, index=False)

# Drop the articles that are after the last article we want to scrape
if LAST_ARTICLE in urls_df['Preview Article URLs'].values:
    last_article_index = urls_df[urls_df['Preview Article URLs'] == LAST_ARTICLE].index[0]
    urls_df = urls_df.iloc[:last_article_index + 1]

print(f"\nFound {len(urls_df)} preview article URLs from {min(years)} to {max(years)}.")
print(urls_df.head())



# Get the contents of the last preview article URL as a test
test_url = urls_df.iloc[-1, 0]
print(f"\nTesting the last preview article URL: {test_url}")

response = session.get(test_url)
response.raise_for_status()

print(f"Status: {response.status_code}")
print(f"Final URL: {response.url}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content length: {len(response.content)} bytes")

Path("debug_response_2.html").write_bytes(response.content)

# Print the URLs of last 10 preview articles
print("\nLast 10 preview article URLs:")
print(urls_df.tail(10).to_string(index=False))