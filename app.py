from flask import Flask, render_template, request, jsonify, session, send_file
from yt_dlp import YoutubeDL
import os
import json
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import zipfile
from datetime import datetime

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
    'no_call_home': True,
    'socket_timeout': 10,  # Timeout amélioré
    'retries': 3  # Nombre de tentatives en cas d'échec
}

PLAYLIST_FILE = 'playlists.json'
THEME_FILE = 'theme.json'
STATS_FILE = 'stats.json'
audio_cache = {}  # Cache pour les URLs audio préchargées

def get_audio_url(video_id):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if not info:
                raise Exception("Could not extract video info")
            return {
                'url': info.get('url'),
                'title': info.get('title', 'Unknown Title')
            }
    except Exception as e:
        logging.error(f"Error getting audio URL for {video_id}: {str(e)}")
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
    default_stats = {
        'totalSongsPlayed': 0,
        'totalHoursPlayed': 0.0,
        'lastUpdated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                loaded_stats = json.load(f)
                return {**default_stats, **loaded_stats}
        else:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_stats, f, indent=2)
            return default_stats
    except Exception as e:
        logging.error(f"Error loading stats: {str(e)}")
        return default_stats

def save_stats(new_stats):
    try:
        if not isinstance(new_stats, dict):
            raise ValueError("Invalid stats format")
        
        new_stats['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if 'totalHoursPlayed' in new_stats:
            new_stats['totalHoursPlayed'] = round(float(new_stats['totalHoursPlayed']), 2)
        
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_stats, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving stats: {str(e)}")
        return False

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
    try:
        info = get_audio_url(video_id)
        if info and info.get('url'):
            return jsonify({
                'success': True,
                'audio_url': info['url'],
                'title': info['title']
            })
        return jsonify({'success': False, 'error': 'Could not get audio URL'})
    except Exception as e:
        logging.error(f"Play error: {str(e)}")
        return jsonify({'success': False, 'error': 'Stream failed'})

@app.route('/save-theme', methods=['POST'])
def save_theme():
    theme_data = request.json
    if theme_data:
        try:
            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'theme': theme_data.get('theme', 'default'),
                    'primaryColor': theme_data.get('primaryColor', '#fca606')
                }, f, indent=2)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Invalid theme data'})

@app.route('/get-theme', methods=['GET'])
def get_theme():
    try:
        with open(THEME_FILE, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        return jsonify({'success': True, 'theme': theme_data})
    except:
        default_theme = {
            'theme': 'default',
            'primaryColor': '#fca606'
        }
        with open(THEME_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_theme, f, indent=2)
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
    if not name or name not in playlists:
        return jsonify({'success': False, 'error': 'Invalid playlist name'})
    
    try:
        song = request.json
        if not song or 'id' not in song or 'title' not in song:
            return jsonify({'success': False, 'error': 'Invalid song data'})
            
        if not any(s['id'] == song['id'] for s in playlists[name]):
            playlists[name].append(song)
            save_playlists(playlists)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Song already in playlist'})
    except Exception as e:
        logging.error(f"Error adding to playlist: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to add song'})

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

@app.route('/get-stats', methods=['GET'])
def get_stats():
    try:
        current_stats = load_stats()
        return jsonify({'success': True, 'stats': current_stats})
    except Exception as e:
        logging.error(f"Error in get_stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save-stats', methods=['POST'])
def save_stats_route():
    try:
        new_stats = request.json
        if not new_stats:
            raise ValueError("No stats data provided")
        
        current_stats = load_stats()
        current_stats.update({
            'totalSongsPlayed': new_stats.get('totalSongsPlayed', current_stats['totalSongsPlayed']),
            'totalHoursPlayed': new_stats.get('totalHoursPlayed', current_stats['totalHoursPlayed'])
        })
        
        if save_stats(current_stats):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to save stats'})
    except Exception as e:
        logging.error(f"Error in save_stats_route: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Gestionnaire d'erreurs global
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Unhandled error: {str(error)}")
    return jsonify({'success': False, 'error': 'An unexpected error occurred'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)