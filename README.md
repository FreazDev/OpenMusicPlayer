# OpenMusicPlayer

OpenMusicPlayer est une application gratuite et open-source pour gérer des playlists musicales en utilisant YouTube et Spotify. Elle vous permet de rechercher des chansons sur YouTube, d'importer des playlists depuis Spotify, de créer vos propres playlists, et d'écouter vos chansons en streaming directement.

## Fonctionnalités
- Recherche de musique sur YouTube
- Importation de playlists Spotify
- Création et gestion de playlists personnalisées
- Lecture audio en streaming depuis YouTube
- Stockage local des playlists

## Configuration de l'intégration avec Spotify

### Étape 1 : Créez un compte Spotify Developer

1. **Créez un compte Spotify Developer** :
   - Allez sur le [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) et connectez-vous avec votre compte Spotify.

2. **Créez une application** :
   - Cliquez sur **"Create an App"**, donnez un nom à votre application, puis sauvegardez les paramètres.

3. **Obtenez vos identifiants** :
   - Une fois l'application créée, vous trouverez votre **Client ID** et **Client Secret** dans les paramètres de l'application.

### Étape 2 : Configurez l'application

1. **Mettez à jour votre code** :
   Remplacez les valeurs `SPOTIFY_CLIENT_ID` et `SPOTIFY_CLIENT_SECRET` par vos propres identifiants dans le fichier `app.py`.

   ```python
   # Configuration Spotify
   SPOTIFY_CLIENT_ID = 'votre_client_id_ici'
   SPOTIFY_CLIENT_SECRET = 'votre_client_secret_ici'
