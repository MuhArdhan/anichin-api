from dotenv import load_dotenv
from .utils.info import Info
from .utils.video import Video
from .utils.episode import Episode
from .utils.home import Home
from .utils.search import Search
from .utils.genre import Genres
from .utils.anime import Anime
import requests
from bs4 import BeautifulSoup


load_dotenv()


class Main:
    def __init__(self) -> None:
        pass

    def get_info(self, slug):
        return Info(slug).to_json()

    def get_video_source(self, slug):
        # URL halaman episode di Anichin
        # Ini adalah URL yang akan Anda scrape untuk menemukan iframe
        episode_page_url = f"https://anichin.moe/{slug}"

        try:
            # Mengirim User-Agent untuk mensimulasikan browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(episode_page_url, headers=headers)
            response.raise_for_status() # Akan mengeluarkan HTTPError untuk status 4xx/5xx

            # Mengurai HTML menggunakan BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            video_sources = []

            # Mencari tag <iframe>
            # Karena Anda memberikan contoh iframe tanpa ID atau kelas unik,
            # kita akan mencoba mencari iframe pertama atau mencari berdasarkan atribut src yang khas
            # Jika ada banyak iframe, Anda mungkin perlu mencari cara yang lebih spesifik
            # (misalnya, mencari div parent-nya, atau iframe dengan atribut tertentu)
            
            # Strategi 1: Cari iframe pertama
            iframe_tag = soup.find('iframe') 
            
            # Strategi 2 (lebih spesifik jika ada banyak iframe):
            # Jika iframe ini selalu memiliki 'ok.ru/videoembed' di src-nya,
            # Anda bisa mencari berdasarkan substring di src.
            # iframe_tag = soup.find('iframe', src=lambda s: s and 'ok.ru/videoembed' in s)

            if iframe_tag and 'src' in iframe_tag.attrs:
                video_url = iframe_tag['src']
                video_sources.append({
                    'name': 'OK.ru Embed', # Nama sumber video
                    'url': video_url,
                    'type': 'iframe_embed'
                })
            else:
                print("Tidak menemukan tag iframe dengan atribut 'src' yang valid.")
                # Anda bisa mengembalikan pesan kosong atau error jika tidak ditemukan
                return {"sources": []}

            # Mengembalikan data dalam format yang diharapkan oleh frontend Anda
            return {"sources": video_sources}

        except requests.exceptions.RequestException as e:
            print(f"Error saat mengambil dari Anichin: {e}")
            # Angkat exception ini agar ditangkap di main.py dan diubah menjadi string
            raise

        except Exception as e:
            print(f"Error saat parsing HTML untuk video source: {e}")
            # Angkat exception ini agar ditangkap di main.py dan diubah menjadi string
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
