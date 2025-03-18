# 🎶 OpenMusicPlayer 🎧

**OpenMusicPlayer** est une application gratuite et open-source pour gérer des playlists musicales en utilisant **YouTube** et **Spotify**. Elle vous permet de rechercher des chansons sur YouTube, d'importer des playlists depuis Spotify, de créer vos propres playlists, et d'écouter vos chansons en streaming directement depuis l'application ! 🎵

## 🚀 Fonctionnalités
- 🔍 Recherche de musique sur **YouTube**
- 🎶 Importation de playlists depuis **Spotify**
- ➕ Création et gestion de playlists personnalisées
- 🎧 Lecture audio en streaming depuis **YouTube**
- 💾 Stockage local des playlists

---

## 📑 Configuration de l'intégration avec **Spotify** 🎵

### 🎯 Étape 1 : Créez un compte **Spotify Developer**

1. **Créez un compte Spotify Developer** :
   - Allez sur le [**Spotify Developer Dashboard**](https://developer.spotify.com/dashboard) et connectez-vous avec votre compte **Spotify**. **(Pas besoin d'un compte Premium !)**
   
   > 🌟 *Si vous n'avez pas encore de compte Spotify, créez-en un gratuitement !* Vous aurez besoin de ce compte pour récupérer le nom des morceaux dans les playlists, ce qui permet d'intégrer correctement vos playlists Spotify dans **OpenMusicPlayer**.

2. **Créez une application** :
   - Cliquez sur **"Create an App"**, donnez un joli nom à votre application (par exemple, "OpenMusicPlayer"), puis sauvegardez les paramètres.
   - Une fois l'application créée, vous pourrez accéder à vos identifiants **Client ID** et **Client Secret**.

3. **Obtenez vos identifiants** :
   - Après avoir créé l'application, vous trouverez votre **Client ID** et **Client Secret** dans les paramètres de l'application. 🆔

---

### ⚙️ Étape 2 : Configurez l'application

1. **Mettez à jour votre code** :
   Remplacez les valeurs `SPOTIFY_CLIENT_ID` et `SPOTIFY_CLIENT_SECRET` par vos propres identifiants dans le fichier `app.py`.

   ```python
   # Configuration Spotify
   SPOTIFY_CLIENT_ID = 'votre_client_id_ici'  # Remplacer par votre Client ID
   SPOTIFY_CLIENT_SECRET = 'votre_client_secret_ici'  # Remplacer par votre Client Secret
📝 Copyright
Créé par Freaz.

Ce projet est open-source et sous licence MIT. Vous pouvez l'utiliser, le modifier et le redistribuer selon les termes de la licence.

Copyright (c) Freaz. Tous droits réservés.
