from flask import Flask, render_template, request, jsonify, session, send_file
from yt_dlp import YoutubeDL
import os
import json
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import zipfile

app = Flask(__name__)
app.secret_key = '1234567890'  # Add a secret key for session management
executor = ThreadPoolExecutor(max_workers=5)

# Configuration Spotify
SPOTIFY_CLIENT_ID = '7b0ec8040813480887b5d5e6180c1993'
SPOTIFY_CLIENT_SECRET = 'ada62d5ebed645c68bf6e2562a014ebf'

# Initialisation de l'API Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Configuration optimisée de yt-dlp
ydl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio',
    'no_warnings': True,
    'quiet': True,
    'extract_flat': True,
    'skip_download': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'no_call_home': True
}

PLAYLIST_FILE = 'playlists.json'
THEME_FILE = 'theme.json'
STATS_FILE = 'stats.json'
audio_cache = {}  # Cache pour les URLs audio préchargées

def get_audio_url(video_id):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return {
                'url': info['url'],
                'title': info['title']
            }
    except Exception as e:
        print(f"Error getting audio URL: {str(e)}")
        return None

def preload_next_song(playlist_name, current_index):
    if playlist_name not in playlists:
        return
    
    playlist = playlists[playlist_name]
    if current_index + 1 < len(playlist):
        next_song_id = playlist[current_index + 1]['id']
        if next_song_id not in audio_cache:
            audio_info = get_audio_url(next_song_id)
            if audio_info:
                audio_cache[next_song_id] = audio_info

def load_playlists():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_playlists(playlists):
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(playlists, f)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {'totalSongsPlayed': 0, 'totalHoursPlayed': 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

playlists = load_playlists()
stats = load_stats()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    with YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            songs = []
            for entry in result['entries']:
                if entry:
                    songs.append({
                        'title': entry['title'],
                        'id': entry['id']
                    })
            return jsonify({'success': True, 'songs': songs})
        except Exception as e:
            print(f"Search error: {str(e)}")
            return jsonify({'success': False, 'error': 'Search failed'})

@app.route('/play/<video_id>')
def play(video_id):
    playlist_name = request.args.get('playlist')
    current_index = int(request.args.get('index', -1))
    
    if video_id in audio_cache:
        info = audio_cache.pop(video_id)
        if playlist_name and current_index >= 0:
            executor.submit(preload_next_song, playlist_name, current_index)
        return jsonify({
            'success': True,
            'audio_url': info['url'],
            'title': info['title']
        })
    
    try:
        info = get_audio_url(video_id)
        if info:
            if playlist_name and current_index >= 0:
                executor.submit(preload_next_song, playlist_name, current_index)
            return jsonify({
                'success': True,
                'audio_url': info['url'],
                'title': info['title']
            })
        return jsonify({'success': False, 'error': 'Could not get audio URL'})
    except Exception as e:
        print(f"Play error: {str(e)}")
        return jsonify({'success': False, 'error': 'Stream failed'})

@app.route('/save-theme', methods=['POST'])
def save_theme():
    theme = request.json.get('theme')
    if theme:
        try:
            with open(THEME_FILE, 'w') as f:
                json.dump(theme, f)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Invalid theme data'})

@app.route('/get-theme', methods=['GET'])
def get_theme():
    try:
        with open(THEME_FILE, 'r') as f:
            theme = json.load(f)
        return jsonify({'success': True, 'theme': theme})
    except:
        default_theme = {
            'primary': '#fca606',
            'background': '#121212',
            'text': '#ffffff'
        }
        with open(THEME_FILE, 'w') as f:
            json.dump(default_theme, f)
        return jsonify({'success': True, 'theme': default_theme})

@app.route('/import-spotify', methods=['POST'])
def import_spotify_playlist():
    spotify_url = request.json.get('url')
    if not spotify_url:
        return jsonify({'success': False, 'error': 'URL manquante'})
    
    try:
        playlist_id = spotify_url.split('playlist/')[1].split('?')[0]
        
        try:
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist['name']
            
            if playlist_name in playlists:
                playlist_name = f"{playlist_name}_{len(playlists)}"
            
            playlists[playlist_name] = []
            
            results = sp.playlist_tracks(playlist_id)
            tracks = results['items']
            
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])
            
            for item in tracks:
                track = item['track']
                if not track:
                    continue
                
                artists = [artist['name'] for artist in track['artists']]
                search_query = f"{track['name']} {' '.join(artists)}"
                
                with YoutubeDL(ydl_opts) as ydl:
                    try:
                        result = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                        if 'entries' in result and result['entries']:
                            video = result['entries'][0]
                            playlists[playlist_name].append({
                                'id': video['id'],
                                'title': f"{track['name']} - {', '.join(artists)}"
                            })
                            logging.info(f"Ajouté: {track['name']}")
                    except Exception as e:
                        logging.error(f"Erreur YouTube pour {search_query}: {str(e)}")
                        continue
            
            save_playlists(playlists)
            return jsonify({
                'success': True,
                'message': f'Playlist "{playlist_name}" importée ({len(playlists[playlist_name])} morceaux)'
            })
            
        except spotipy.SpotifyException as e:
            logging.error(f"Erreur Spotify: {str(e)}")
            return jsonify({'success': False, 'error': 'Erreur d\'accès à Spotify'})
            
    except Exception as e:
        logging.error(f"Erreur d'importation: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de l\'importation'})

@app.route('/playlist', methods=['POST'])
def create_playlist():
    data = request.json
    playlist_name = data.get('name')
    if playlist_name:
        if playlist_name not in playlists:
            playlists[playlist_name] = []
            save_playlists(playlists)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Playlist already exists'})
    return jsonify({'success': False, 'error': 'Invalid playlist name'})

@app.route('/playlists', methods=['GET'])
def get_playlists():
    return jsonify({
        'success': True,
        'playlists': playlists
    })

@app.route('/playlist/<name>/add', methods=['POST'])
def add_to_playlist(name):
    if name in playlists:
        song = request.json
        if not any(s['id'] == song['id'] for s in playlists[name]):
            playlists[name].append(song)
            save_playlists(playlists)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Song already in playlist'})
    return jsonify({'success': False, 'error': 'Playlist not found'})

@app.route('/playlist/<name>', methods=['GET'])
def get_playlist(name):
    if name in playlists:
        return jsonify({
            'success': True,
            'playlist': playlists[name],
            'name': name
        })
    return jsonify({'success': False, 'error': 'Playlist not found'})

@app.route('/playlist/<name>/remove/<song_id>', methods=['DELETE'])
def remove_from_playlist(name, song_id):
    if name in playlists:
        playlists[name] = [song for song in playlists[name] if song['id'] != song_id]
        save_playlists(playlists)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Playlist not found'})

@app.route('/playlist/<name>', methods=['DELETE'])
def delete_playlist(name):
    if name in playlists:
        del playlists[name]
        save_playlists(playlists)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Playlist not found'})

@app.route('/download-playlist/<name>', methods=['GET'])
def download_playlist(name):
    if name not in playlists:
        return jsonify({'success': False, 'error': 'Playlist not found'})
    
    try:
        # Créer un dossier temporaire pour la playlist
        temp_dir = f"temp_{name}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Télécharger chaque morceau de la playlist
        for song in playlists[name]:
            video_id = song['id']
            with YoutubeDL({'format': 'bestaudio', 'outtmpl': f"{temp_dir}/{song['title']}.%(ext)s"}) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        # Créer un fichier ZIP de la playlist
        zip_path = f"{name}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
        
        # Supprimer le dossier temporaire
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
        
        # Envoyer le fichier ZIP à l'utilisateur
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get-stats', methods=['GET'])
def get_stats():
    return jsonify({'success': True, 'stats': stats})

@app.route('/save-stats', methods=['POST'])
def save_stats_route():
    global stats
    stats = request.json
    save_stats(stats)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)