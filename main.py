from typing import Text
import json # Import json untuk JSONDecodeError
import requests
from urllib.parse import urlparse

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from api import Main
# Pastikan Anda juga mengimpor exception dari requests jika Anda menggunakannya di Main
# from requests.exceptions import ConnectionError, RequestException

app = Flask(__name__)
main = Main()

# cors
CORS(app)


@app.get("/")
def read_root():
    """
    Get home page
    params: page (optional) - int
    return: JSON

    """

    page = request.args.get("page")
    try:
        if page and not page.isdigit():
            return jsonify(message="error: Parameter 'page' harus berupa angka."), 400
        # Asumsi main.get_home mengembalikan data yang langsung bisa di-jsonify atau tuple (data, status_code)
        data, status_code = main.get_home(int(page) if page else 1), 200
        return jsonify(data), status_code
    except Exception as err:
        # Mengubah objek error menjadi string agar bisa di-jsonify
        print(f"Error di /: {err}")
        return jsonify(message=f"Terjadi kesalahan server: {str(err)}"), 500


@app.get("/search/<query>")
def search(query):
    """
    Search donghua by query
    params: query - string (required)
    return: JSON
    """
    try:
        if not query:
            return jsonify(message="error: Parameter 'query' tidak boleh kosong"), 400
        # Asumsi main.search mengembalikan data yang langsung bisa di-jsonify
        data = main.search(query)
        return jsonify(data), 200
    except Exception as err:
        print(f"Error di /search/{query}: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mencari: {str(err)}"), 500


# slug from url
@app.get("/info/<slug>")
def get_info(slug: Text):
    """
    Show detail of donghua
    params: slug name of donghua - string (required)
    return: JSON

    """
    try:
        data = main.get_info(slug)
        # Asumsi data dari main.get_info sudah siap di-jsonify
        return jsonify(data), 200
    except Exception as err:
        print(f"Error di /info/{slug}: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mengambil info: {str(err)}"), 500


@app.get("/genres")
def list_genres():
    """
    Show list of genres
    return: JSON

    """
    try:
        data = main.genres()
        # Asumsi data dari main.genres sudah siap di-jsonify
        return jsonify(data), 200
    except Exception as err:
        print(f"Error di /genres: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mengambil daftar genre: {str(err)}"), 500


@app.get("/genre/<slug>")
def get_genres(slug):
    """
    Show list of donghua by genre
    params: slug genre - string (required)
    query: page (optional) - int
    return: JSON

    """
    try:
        page = request.args.get("page")
        if page and not page.isdigit():
            return jsonify(message="error: Parameter 'page' harus berupa angka."), 400

        data = main.genres(slug, int(page) if page else 1)
        return jsonify(data), 200
    except Exception as err:
        print(f"Error di /genre/{slug}: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mengambil genre: {str(err)}"), 500


@app.get("/episode/<slug>")
def get_episode(slug: Text):
    """
    Get detail of episode
    params: slug episode - string (required)
    return: JSON

    """
    try:
        data = main.get_episode(slug)
        if data:
            return jsonify(data), 200
        return jsonify(message="tidak ditemukan"), 404
    except Exception as err:
        print(f"Error di /episode/{slug}: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mengambil episode: {str(err)}"), 500


# get episode from url
@app.get("/video-source/<path:slug>")
def get_video(slug: Text):
    """
    Show list of video source
    params: slug - string (required)
    return: JSON

    """
    try:
        print(f"Menerima permintaan untuk slug video: {slug}")
        data = main.get_video_source(slug)
        if data:
            return jsonify(data), 200
        return jsonify(message="tidak ditemukan"), 404
    except json.JSONDecodeError as err: # Menambahkan penanganan spesifik untuk JSONDecodeError
        print(f"JSON Decode Error di /video-source/{slug}: {err}")
        return jsonify(message=f"Kesalahan penguraian JSON dari sumber eksternal: {str(err)}"), 500
    except Exception as err:
        print(f"Error umum di /video-source/{slug}: {err}")
        return jsonify(message=f"Terjadi kesalahan server: {str(err)}"), 500


@app.get("/anime")
def anime():
    """
    Show list of anime
    return: JSON

    """
    try:
        req = request.args
        todict = dict(req)
        data = main.anime(params=todict)
        return jsonify(data), 200
    except Exception as err:
        print(f"Error di /anime: {err}")
        return jsonify(message=f"Terjadi kesalahan saat mengambil daftar anime: {str(err)}"), 500
    
@app.route('/proxy-video')
def proxy_video():
    video_url = request.args.get('url') # URL video asli dari yt-dlp
    if not video_url:
        return "URL video tidak diberikan", 400

    parsed_video_url = urlparse(video_url)
    
    # Menentukan Referer yang benar berdasarkan domain URL video
    # Ini sangat penting untuk Ok.ru/VKUser.net
    if "ok.ru" in parsed_video_url.netloc or "vkuser.net" in parsed_video_url.netloc:
        target_referer = "https://ok.ru/"
    elif "dailymotion.com" in parsed_video_url.netloc:
        target_referer = "https://www.dailymotion.com/"
    else:
        # Fallback, bisa jadi domain Anichin.moe atau domain default lain
        target_referer = "https://anichin.moe/" 
    
    headers_to_send_to_source = {
        'Referer': target_referer,
        # Teruskan User-Agent dari browser pengguna ke server video asli
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
        # Head-headers seperti range request juga penting untuk streaming
        'Range': request.headers.get('Range', '') # Meneruskan Range header untuk seek
    }

    try:
        # Gunakan requests.get dengan stream=True untuk mengalirkan data
        # Timeout disetel untuk mencegah hanging requests
        r = requests.get(video_url, headers=headers_to_send_to_source, stream=True, timeout=60)
        r.raise_for_status() # Akan memunculkan HTTPError untuk status 4xx/5xx

        # Buat respons Flask yang akan mengalirkan konten dari server video asli
        response = Response(r.iter_content(chunk_size=8192), status=r.status_code)
        
        # Salin header relevan dari respons server video asli ke respons Flask
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        for name, value in r.headers.items():
            if name.lower() not in excluded_headers:
                response.headers[name] = value
        
        # Jika Content-Type tidak ada, atur fallback
        if 'Content-Type' not in response.headers:
            if ".m3u8" in video_url:
                response.headers['Content-Type'] = 'application/x-mpegURL'
            elif ".mp4" in video_url:
                response.headers['Content-Type'] = 'video/mp4'
            else:
                response.headers['Content-Type'] = 'application/octet-stream' # Generic binary
        
        print(f"Proxying: {video_url} -> Status: {r.status_code}, Content-Type: {response.headers.get('Content-Type')}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error saat memproxy video {video_url}: {e}")
        # Tangani error dengan memberikan respons yang informatif
        return f"Gagal memuat video melalui proxy: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
