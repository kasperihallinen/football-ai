from itertools import product
import pandas as pd
from lxml import html
from soccerdata import SoFIFA

from soccerdata._common import standardize_colnames
from soccerdata._config import DATA_DIR, TEAMNAME_REPLACEMENTS, logger

SO_FIFA_DATADIR = DATA_DIR / "SoFIFA"
SO_FIFA_API = "https://sofifa.com"


class SoFIFA(SoFIFA):
    """
    Custom SoFIFA scraper with an added method to fetch player name, id,
    league, age, overall rating, potential rating, team, height, weigth, value
    and wage.
    """

    @classmethod
    def available_leagues(cls) -> list[str]:
        return SoFIFA.available_leagues()

    def read_player_attributes(self) -> pd.DataFrame:
        """Retrieve player attributes for all players in the selected leagues.

        Returns
        -------
        pd.DataFrame
        """

        # Define the player attributes to retrieve
        attributes = {
            "pi": "player_id",
            "ae": "age",
            "hi": "height",
            "wi": "weight",
            "oa": "overall",
            "pt": "potential",
            "vl": "value",
            "wg": "wage",
        }

        # Build URL
        urlmask = SO_FIFA_API + "/players?type=all&lg[]={}&r={}&set=true"

        for attribute_id in attributes:
            urlmask += f"&showCol[]={attribute_id}"

        # Get league IDs
        leagues = self.read_leagues()

        # Collect players
        players = []
        # SoFIFA displays 60 players per page
        page_size = 60
        iterator = list(product(leagues.iterrows(), self.versions.iterrows()))
        for i, ((lkey, league), (version_id, version)) in enumerate(iterator):
            logger.info(
                "[%s/%s] Retrieving player attributes for %s in %s edition",
                i + 1,
                len(iterator),
                lkey,
                version["update"],
            )

            league_id = league["league_id"]
            offset = 0
            while True:
                # Read player page
                filepath = self.data_dir / (
                    f"player_attributes_{league_id}_{version_id}_{offset}.html"
                )
                url = (
                    urlmask.format(league_id, version_id) + f"&offset={offset}"
                )
                reader = self.get(url, filepath)

                tree = html.parse(
                    reader,
                    parser=html.HTMLParser(encoding="utf8"),
                )
                # Extract player rows
                rows = tree.xpath("//table/tbody/tr")
                if not rows:
                    break

                for node in rows:
                    # Extract player link
                    player_links = node.xpath(
                        ".//a[contains(@href, '/player/')]"
                    )

                    if not player_links:
                        continue

                    player_link = player_links[0]
                    player_name = (
                        player_link.get("data-tippy-content")
                        or player_link.text_content().strip()
                    )

                    # Extract team name
                    team_links = node.xpath(".//a[contains(@href, '/team/')]")
                    team = (
                        team_links[0].text_content().strip()
                        if team_links
                        else None
                    )

                    # Extract player attributes
                    player_data = {
                        "player": player_name,
                        "team": team,
                        "league": lkey,
                        "version_id": version_id,
                        **version.to_dict(),
                    }

                    for attribute_id, description in attributes.items():
                        value = node.xpath(
                            f".//td[@data-col='{attribute_id}']//text()"
                        )
                        value = " ".join(
                            text.strip() for text in value if text.strip()
                        )

                        player_data[description] = value if value else None

                    players.append(player_data)

                # Move to next page
                offset += page_size

                # Stop if the current page contains fewer than 60 players
                if len(rows) < page_size:
                    break

        # Return DataFrame
        return (
            pd.DataFrame(players)
            .replace({"team": TEAMNAME_REPLACEMENTS})
            .pipe(standardize_colnames)
            .sort_values(by=["player", "version_id"])
        )
