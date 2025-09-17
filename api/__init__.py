from dotenv import load_dotenv
from .utils.info import Info
from .utils.video import Video
from .utils.episode import Episode
from .utils.home import Home
from .utils.search import Search
from .utils.genre import Genres
from .utils.anime import Anime
import cloudscraper
from bs4 import BeautifulSoup
import base64
import re


load_dotenv()


class Main:
    def __init__(self) -> None:
        pass

    def get_info(self, slug):
        return Info(slug).to_json()

    def get_video_source(self, slug):
        # URL halaman episode di Anichin
        episode_page_url = f"https://anichin.moe/{slug}"

        try:
            # Gunakan cloudscraper
            scraper = cloudscraper.create_scraper()

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://anichin.moe/',
                'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
            }

            response = scraper.get(episode_page_url, headers=headers)
            response.raise_for_status()

            # Parsing HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            video_sources = []

            # --- Cari Dailymotion ---
            dailymotion_option = soup.find('option', string=re.compile(r'Dailymotion', re.IGNORECASE))

            if dailymotion_option:
                encoded_iframe = dailymotion_option.get('value')
                if encoded_iframe:
                    decoded_iframe_html = base64.b64decode(encoded_iframe + "===").decode("utf-8")
                    iframe_soup = BeautifulSoup(decoded_iframe_html, "html.parser")
                    dailymotion_iframe = iframe_soup.find("iframe")

                    if dailymotion_iframe and "src" in dailymotion_iframe.attrs:
                        dailymotion_link = dailymotion_iframe["src"]
                        video_sources.append({
                            "name": "Dailymotion [ADS]",
                            "url": dailymotion_link,
                            "type": "iframe_embed"
                        })

            # --- Fallback OK.ru ---
            if not video_sources:
                iframe_tag = soup.find("iframe", src=lambda s: s and "ok.ru/videoembed" in s)
                if iframe_tag and "src" in iframe_tag.attrs:
                    video_sources.append({
                        "name": "OK.ru Embed",
                        "url": iframe_tag["src"],
                        "type": "iframe_embed"
                    })

            return {"sources": video_sources}

        except Exception as e:
            print(f"Error saat mengambil dari Anichin: {e}")
            raise


    def get_episode(self, slug):
        return Episode(slug).to_json()

    def get_home(self, page=1):
        return Home(page).get_details()

    def search(self, query):
        return Search(query).get_details()

    def genres(self, genre=None, page=1):
        genres = Genres()
        if not genre:
            return genres.list_genre()
        return genres.get_genre(genre, page)

    def anime(self, **kwargs):
        return Anime().get_details(**kwargs)


if __name__ == "__main__":
    main = Main()
    # info = main.get_info("battle-through-the-heavens-season-5/")
    video = main.get_video("perfect-world-episode-03-subtitle-indonesia")
    print(video)
