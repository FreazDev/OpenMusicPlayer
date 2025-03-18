OpenMusicPlayer basé sur YouTube et Spotify
OpenMusicPlayer est une application gratuite et open-source qui permet aux utilisateurs de créer, importer et gérer des playlists musicales en utilisant à la fois YouTube et Spotify. L'application utilise Flask pour créer une interface web simple et des APIs pour interagir avec les services externes, notamment yt-dlp pour récupérer des vidéos audio de YouTube et Spotipy pour interagir avec l'API de Spotify.

Fonctionnalités principales :
Recherche de Musique (YouTube) : Les utilisateurs peuvent rechercher des chansons via YouTube en utilisant un mot-clé. L'application renvoie une liste de résultats de recherche avec les titres et identifiants de vidéo.

Importation de Playlists Spotify : Les utilisateurs peuvent importer des playlists depuis Spotify en fournissant l'URL de la playlist. L'application extrait les chansons de la playlist et les recherche sur YouTube pour trouver les versions audio correspondantes.

Création et gestion de playlists personnalisées : Les utilisateurs peuvent créer des playlists personnalisées, y ajouter des chansons manuellement, ou supprimer des chansons et des playlists.

Lecture de Musiques : L'application permet de lire les chansons directement à partir de YouTube, en récupérant l'URL du flux audio pour la lecture en streaming.

Support pour Playlists longues : Les playlists de plus de 100 morceaux sont gérées correctement grâce à la pagination de l'API Spotify.

Stockage local de Playlists : Toutes les playlists créées ou importées sont stockées localement dans un fichier playlists.json.

Fonctionnement du Code :
Flask gère l'ensemble des requêtes HTTP et fournit une interface utilisateur via des routes définies dans le code.
yt-dlp (un fork de youtube-dl) est utilisé pour rechercher et extraire des informations sur les vidéos YouTube. Ce module permet de récupérer des flux audio des vidéos sans télécharger les fichiers.
Spotipy est utilisé pour interagir avec l'API de Spotify. Il permet d'extraire des informations de playlists, de morceaux, et d'artistes sur Spotify.
Gestion asynchrone avec ThreadPoolExecutor : Le traitement des recherches et des ajouts de chansons aux playlists se fait de manière asynchrone pour optimiser la performance de l'application, notamment lors de la recherche sur YouTube pour chaque chanson.
Routes principales de l'application :
/ : Page d'accueil.
/search : Rechercher des chansons sur YouTube avec un mot-clé.
/import-spotify : Importer une playlist Spotify à partir de son URL.
/play/<video_id> : Lire une chanson en streaming depuis YouTube.
/playlist : Créer une nouvelle playlist.
/playlists : Lister toutes les playlists.
/playlist/<name> : Obtenir les détails d'une playlist spécifique.
/playlist/<name>/add : Ajouter une chanson à une playlist spécifique.
/playlist/<name>/remove/<song_id> : Retirer une chanson d'une playlist.
/playlist/<name> : Supprimer une playlist.
Exemple de fonctionnement :
L'utilisateur peut créer une playlist, y ajouter des chansons recherchées sur YouTube ou importées depuis Spotify, puis les lire en streaming directement depuis l'application.
Les playlists sont stockées en local, ce qui permet de garder une trace des chansons ajoutées.
Dépendances :
Flask : pour la création de l'application web.
yt-dlp : pour l'extraction d'audio depuis YouTube.
Spotipy : pour recupéré le nom des musiques dans une playlist.
