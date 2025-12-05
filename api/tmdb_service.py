"""
Service d'intégration avec l'API TMDB pour récupérer les affiches, trailers et informations de streaming.
"""
import os
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"


def search_movie(title: str, year: Optional[int] = None) -> Optional[Dict]:
    """Recherche un film sur TMDB."""
    if not TMDB_API_KEY:
        return None
    
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "fr-FR"
        }
        if year:
            params["year"] = year
        
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]
    except Exception as e:
        print(f"Erreur lors de la recherche TMDB: {e}")
    
    return None


def get_movie_details(tmdb_id: int) -> Optional[Dict]:
    """Récupère les détails complets d'un film depuis TMDB."""
    if not TMDB_API_KEY:
        return None
    
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "language": "fr-FR",
            "append_to_response": "videos,watch/providers"
        }
        
        response = requests.get(f"{TMDB_BASE_URL}/movie/{tmdb_id}", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération des détails TMDB: {e}")
    
    return None


def get_movie_poster_url(title: str, year: Optional[int] = None) -> Optional[str]:
    """Récupère l'URL de l'affiche d'un film."""
    movie = search_movie(title, year)
    if movie and movie.get("poster_path"):
        return f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}"
    return None


def get_movie_backdrop_url(title: str, year: Optional[int] = None) -> Optional[str]:
    """Récupère l'URL du backdrop d'un film."""
    movie = search_movie(title, year)
    if movie and movie.get("backdrop_path"):
        return f"{TMDB_BACKDROP_BASE_URL}{movie['backdrop_path']}"
    return None


def get_movie_trailer(title: str, year: Optional[int] = None) -> Optional[Dict]:
    """Récupère la bande annonce d'un film."""
    movie = search_movie(title, year)
    if not movie or not movie.get("id"):
        return None
    
    details = get_movie_details(movie["id"])
    if not details:
        return None
    
    # Chercher une bande annonce YouTube
    videos = details.get("videos", {}).get("results", [])
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            return {
                "youtube_id": video.get("key"),
                "url": f"https://www.youtube.com/watch?v={video.get('key')}",
                "name": video.get("name")
            }
    
    return None


def get_streaming_platforms(title: str, year: Optional[int] = None) -> List[Dict]:
    """Récupère les plateformes de streaming disponibles pour un film."""
    movie = search_movie(title, year)
    if not movie or not movie.get("id"):
        return []
    
    details = get_movie_details(movie["id"])
    if not details:
        return []
    
    platforms = []
    watch_providers = details.get("watch/providers", {}).get("results", {})
    
    # Logo des plateformes (mapping simplifié)
    platform_logos = {
        "Netflix": "https://www.themoviedb.org/assets/2/v4/logos/v2/Netflix_Logo_RGB.png",
        "Disney Plus": "https://www.themoviedb.org/assets/2/v4/logos/v2/Disney_Plus_Logo_RGB.png",
        "Amazon Prime Video": "https://www.themoviedb.org/assets/2/v4/logos/v2/Amazon_Prime_Video_Logo_RGB.png",
        "HBO": "https://www.themoviedb.org/assets/2/v4/logos/v2/HBO_Logo_RGB.png",
        "Apple TV Plus": "https://www.themoviedb.org/assets/2/v4/logos/v2/Apple_TV_Plus_Logo_RGB.png",
        "Paramount Plus": "https://www.themoviedb.org/assets/2/v4/logos/v2/Paramount_Plus_Logo_RGB.png",
        "Hulu": "https://www.themoviedb.org/assets/2/v4/logos/v2/Hulu_Logo_RGB.png",
        "Canal+": "https://www.themoviedb.org/assets/2/v4/logos/v2/Canal_Plus_Logo_RGB.png",
        "OCS": "https://www.themoviedb.org/assets/2/v4/logos/v2/OCS_Logo_RGB.png"
    }
    
    # FR (France) providers
    fr_providers = watch_providers.get("FR", {})
    flatrate = fr_providers.get("flatrate", [])
    
    for provider in flatrate:
        provider_name = provider.get("provider_name", "")
        logo_path = provider.get("logo_path", "")
        logo_url = f"https://image.tmdb.org/t/p/w45{logo_path}" if logo_path else platform_logos.get(provider_name, "")
        
        platforms.append({
            "name": provider_name,
            "logo_url": logo_url,
            "provider_id": provider.get("provider_id")
        })
    
    return platforms


def get_film_metadata(title: str, year: Optional[int] = None) -> Dict:
    """Récupère toutes les métadonnées d'un film (affiche, trailer, streaming)."""
    movie = search_movie(title, year)
    if not movie or not movie.get("id"):
        return {}
    
    details = get_movie_details(movie["id"])
    if not details:
        return {
            "poster_url": get_movie_poster_url(title, year),
            "backdrop_url": get_movie_backdrop_url(title, year),
            "trailer_url": None,
            "trailer_youtube_id": None,
            "streaming_platforms": []
        }
    
    # Poster
    poster_path = details.get("poster_path")
    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
    
    # Backdrop
    backdrop_path = details.get("backdrop_path")
    backdrop_url = f"{TMDB_BACKDROP_BASE_URL}{backdrop_path}" if backdrop_path else None
    
    # Trailer
    trailer_info = None
    videos = details.get("videos", {}).get("results", [])
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            trailer_info = {
                "youtube_id": video.get("key"),
                "url": f"https://www.youtube.com/watch?v={video.get('key')}"
            }
            break
    
    # Streaming platforms
    platforms = get_streaming_platforms(title, year)
    
    return {
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "trailer_url": trailer_info["url"] if trailer_info else None,
        "trailer_youtube_id": trailer_info["youtube_id"] if trailer_info else None,
        "streaming_platforms": platforms,
        "tmdb_id": movie["id"]
    }

