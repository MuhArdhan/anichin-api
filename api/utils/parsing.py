import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Parsing:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper()  # ini ganti requests.Session
        self.url = getenv("HOST", "")
        self.history_url = None

    def __get_html(self, slug, **kwargs):
        if slug.startswith("/"):
            url = f"{self.url}{slug}"
        else:
            url = f"{self.url}/{slug}"
        r = self.scraper.get(url, **kwargs)
        self.history_url = url
        return r.text

    def get_parsed_html(self, url, **kwargs):
        return BeautifulSoup(self.__get_html(url, **kwargs), "html.parser")

    def parsing(self, data):
        return BeautifulSoup(data, "html.parser")