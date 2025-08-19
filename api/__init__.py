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
            # Mengirim User-Agent untuk mensimulasikan browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(episode_page_url, headers=headers)
            response.raise_for_status() # Akan mengeluarkan HTTPError untuk status 4xx/5xx

            # Mengurai HTML menggunakan BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            video_sources = []

            # --- Bagian yang dimodifikasi untuk mencari Dailymotion ---

            # Cari elemen <option> dengan teks "Dailymotion [ADS]"
            dailymotion_option = soup.find('option', string=re.compile(r'Dailymotion', re.IGNORECASE))

            if dailymotion_option:
                # Ambil nilai dari atribut 'value'
                encoded_iframe = dailymotion_option.get('value')
                
                if encoded_iframe:
                    try:
                        # Dekode string Base64
                        # Pastikan string Base64 memiliki padding yang benar jika diperlukan
                        decoded_iframe_bytes = base64.b64decode(encoded_iframe + '===') # Tambahkan padding potensial
                        decoded_iframe_html = decoded_iframe_bytes.decode('utf-8')
                        
                        # Parsing string HTML yang sudah didekode
                        iframe_soup = BeautifulSoup(decoded_iframe_html, 'html.parser')
                        dailymotion_iframe = iframe_soup.find('iframe')
                        
                        if dailymotion_iframe and 'src' in dailymotion_iframe.attrs:
                            dailymotion_link = dailymotion_iframe['src']
                            video_sources.append({
                                'name': 'Dailymotion [ADS]', # Nama sumber video
                                'url': dailymotion_link,
                                'type': 'iframe_embed'
                            })
                            print(f"Link Dailymotion yang ditemukan: {dailymotion_link}")
                        else:
                            print("Tidak dapat menemukan tag iframe atau atribut src dalam dekode HTML Dailymotion.")
                    except base64.binascii.Error as be:
                        print(f"Error dekode Base64 untuk Dailymotion: {be}. String: {encoded_iframe}")
                    except Exception as e:
                        print(f"Error saat memproses link Dailymotion: {e}")
                else:
                    print("Atribut 'value' untuk opsi Dailymotion kosong.")
            else:
                print("Tidak ditemukan opsi Dailymotion [ADS] dalam HTML. Mencoba mencari OK.ru sebagai fallback.")
                # Fallback ke pencarian iframe OK.ru jika Dailymotion tidak ditemukan
                iframe_tag = soup.find('iframe', src=lambda s: s and 'ok.ru/videoembed' in s)
                if iframe_tag and 'src' in iframe_tag.attrs:
                    video_url = iframe_tag['src']
                    video_sources.append({
                        'name': 'OK.ru Embed', # Nama sumber video
                        'url': video_url,
                        'type': 'iframe_embed'
                    })
                    print(f"Link OK.ru ditemukan sebagai fallback: {video_url}")
                else:
                    print("Tidak menemukan tag iframe OK.ru dengan atribut 'src' yang valid.")

            # Mengembalikan data dalam format yang diharapkan oleh frontend Anda
            return {"sources": video_sources}

        except requests.exceptions.RequestException as e:
            print(f"Error saat mengambil dari Anichin: {e}")
            raise # Angkat exception ini agar ditangkap di main.py dan diubah menjadi string

        except Exception as e:
            print(f"Error umum saat parsing HTML untuk video source: {e}")
            raise # Angkat exception ini agar ditangkap di main.py dan diubah menjadi string

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
