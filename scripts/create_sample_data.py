"""
Script pour créer des données d'exemple dans la base de données.
Utile pour tester le système sans avoir besoin d'un gros dataset.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection
from psycopg2.extras import execute_values

# Films d'exemple
SAMPLE_FILMS = [
    {
        "title": "The Matrix",
        "year": 1999,
        "genres": ["Sci-Fi", "Action"],
        "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
        "synopsis": "A computer hacker learns about the true nature of reality and his role in the war against its controllers."
    },
    {
        "title": "Inception",
        "year": 2010,
        "genres": ["Sci-Fi", "Thriller"],
        "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Tom Hardy"],
        "synopsis": "A skilled thief enters people's dreams to steal secrets from their subconscious."
    },
    {
        "title": "The Dark Knight",
        "year": 2008,
        "genres": ["Action", "Crime", "Drama"],
        "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
        "synopsis": "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."
    },
    {
        "title": "Interstellar",
        "year": 2014,
        "genres": ["Sci-Fi", "Drama"],
        "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
        "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    },
    {
        "title": "Pulp Fiction",
        "year": 1994,
        "genres": ["Crime", "Drama"],
        "cast": ["John Travolta", "Samuel L. Jackson", "Uma Thurman"],
        "synopsis": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption."
    },
    {
        "title": "The Matrix Reloaded",
        "year": 2003,
        "genres": ["Sci-Fi", "Action"],
        "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
        "synopsis": "Neo and his allies race against time before the machines discover the city of Zion and destroy it. Meanwhile, Neo must decide how he can save Trinity from a dark fate."
    },
    {
        "title": "Blade Runner 2049",
        "year": 2017,
        "genres": ["Sci-Fi", "Thriller"],
        "cast": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"],
        "synopsis": "A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard, who's been missing for thirty years."
    },
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genres": ["Drama"],
        "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
        "synopsis": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
    },
    {
        "title": "Fight Club",
        "year": 1999,
        "genres": ["Drama", "Thriller"],
        "cast": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
        "synopsis": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more."
    },
    {
        "title": "Memento",
        "year": 2000,
        "genres": ["Mystery", "Thriller"],
        "cast": ["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano"],
        "synopsis": "A man with short-term memory loss attempts to track down his wife's murderer."
    }
]


def create_sample_data():
    """Crée des données d'exemple dans la base de données."""
    print("Création des données d'exemple...")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Préparer les données
    rows = []
    for film in SAMPLE_FILMS:
        rows.append((
            film["title"],
            film["year"],
            film["genres"],
            film["cast"],
            film["synopsis"],
            None  # meta
        ))
    
    # Insérer
    execute_values(
        cur,
        """
        INSERT INTO films (title, year, genres, cast, synopsis, meta)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        rows
    )
    
    inserted = cur.rowcount
    conn.commit()
    
    print(f"✓ {inserted} films d'exemple insérés")
    
    # Compter le total
    cur.execute("SELECT COUNT(*) FROM films")
    total = cur.fetchone()[0]
    print(f"✓ Total de films dans la base: {total}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_sample_data()

