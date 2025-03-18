from flask import Flask, render_template, request, jsonify
from yt_dlp import YoutubeDL
import os
import json
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)

# Configuration Spotify
SPOTIFY_CLIENT_ID = '7b0ec8040813480887b5d5e6180c1993'  # Remplacer par votre client ID
SPOTIFY_CLIENT_SECRET = 'ada62d5ebed645c68bf6e2562a014ebf'  # Remplacer par votre client secret

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

def load_playlists():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_playlists(playlists):
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(playlists, f)

playlists = load_playlists()

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

@app.route('/import-spotify', methods=['POST'])
def import_spotify_playlist():
    spotify_url = request.json.get('url')
    if not spotify_url:
        return jsonify({'success': False, 'error': 'URL manquante'})
    
    try:
        # Extraire l'ID de la playlist depuis l'URL
        playlist_id = spotify_url.split('playlist/')[1].split('?')[0]
        
        try:
            # Récupérer les informations de la playlist
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist['name']
            
            # Vérifier si la playlist existe déjà
            if playlist_name in playlists:
                playlist_name = f"{playlist_name}_{len(playlists)}"
            
            playlists[playlist_name] = []
            
            # Récupérer tous les morceaux
            results = sp.playlist_tracks(playlist_id)
            tracks = results['items']
            
            # Gérer les playlists de plus de 100 morceaux
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])
            
            # Pour chaque morceau, chercher sur YouTube
            for item in tracks:
                track = item['track']
                if not track:  # Skip if track is None or local file
                    continue
                
                # Construire le titre de recherche
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
            
            # Sauvegarder la playlist
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

@app.route('/play/<video_id>')
def play(video_id):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return jsonify({
                'success': True,
                'audio_url': info['url'],
                'title': info['title']
            })
    except Exception as e:
        print(f"Play error: {str(e)}")
        return jsonify({'success': False, 'error': 'Stream failed'})

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

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)