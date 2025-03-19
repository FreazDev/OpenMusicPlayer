# 🎶 OpenMusicPlayer 🎧  

**OpenMusicPlayer** est une application gratuite et open-source pour gérer des playlists musicales en utilisant **YouTube** et **Spotify**. Elle vous permet de rechercher des chansons sur YouTube, d'importer des playlists depuis Spotify, de créer vos propres playlists et d'écouter vos chansons en streaming directement depuis l'application ! 🎵  

![OpenMusicPlayer](https://i.ibb.co/tMsMkYtY/image.png)  

## 🚀 Fonctionnalités  
- 🔍 **Recherche Intelligente** : trouvez et écoutez vos morceaux préférés.  
- 🎶 **Importation Spotify** : intégrez facilement vos playlists Spotify.  
- ➕ **Playlists personnalisées** : créez, gérez et modifiez vos propres playlists.  
- 🎧 **Lecture en streaming** : écoutez de la musique directement depuis OpenMusicPlayer.  
- 💾 **Stockage local** : enregistrez vos playlists pour un accès rapide.  
- 🎨 **Personnalisation** : choisissez un thème (**clair/sombre**) et une couleur principale.  
- 📊 **Statistiques d'écoute** : suivez automatiquement votre activité musicale.  

---

## 📑 Configuration de l'intégration avec **Spotify** 🎵  

### 🎯 Étape 1 : Créez un compte **Spotify Developer**  

1. **Créez un compte Spotify Developer** :  
   - Allez sur le [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) et connectez-vous avec votre compte **Spotify**. *(Pas besoin d'un compte Premium !)*  

   > 🌟 *Si vous n'avez pas encore de compte Spotify, créez-en un gratuitement !* Vous aurez besoin de ce compte pour récupérer le nom des morceaux dans les playlists, ce qui permet d'intégrer correctement vos playlists Spotify dans **OpenMusicPlayer**.  

2. **Créez une application** :  
   - Cliquez sur **"Create an App"**, donnez un joli nom à votre application (par exemple, *OpenMusicPlayer*), puis sauvegardez les paramètres.  
   - Une fois l'application créée, vous pourrez accéder à vos identifiants **Client ID** et **Client Secret**.  

3. **Obtenez vos identifiants** :  
   - Après avoir créé l'application, vous trouverez votre **Client ID** et **Client Secret** dans les paramètres de l'application. 🆔  

![Playlist](https://i.ibb.co/tMsMkYtY/image.png)  

---

### ⚙️ Étape 2 : Configurez l'application  

1. **Mettez à jour votre code** :  
   Remplacez les valeurs `SPOTIFY_CLIENT_ID` et `SPOTIFY_CLIENT_SECRET` par vos propres identifiants dans le fichier `app.py`.  

   ```python
   # Configuration Spotify
   SPOTIFY_CLIENT_ID = 'votre_client_id_ici'  # Remplacer par votre Client ID
   SPOTIFY_CLIENT_SECRET = 'votre_client_secret_ici'  # Remplacer par votre Client Secret
