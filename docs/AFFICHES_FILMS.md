# 🎬 Affichage des Affiches de Films

## ✨ Nouveautés

L'interface affiche maintenant les affiches de films de manière visuellement attrayante lorsque vous effectuez une recherche !

## 🎨 Caractéristiques

### Design des Cartes de Films

- **Affiches en images** : Chaque film s'affiche avec une grande image d'affiche
- **Design moderne** : Cartes avec images en haut et informations en bas
- **Effet hover** : Zoom et overlay au survol
- **Badges informatifs** : Année et pourcentage de similarité affichés en overlay
- **Images placeholder** : Si aucune affiche n'est trouvée, une image élégante avec le titre est générée

### Affichage

1. **Recherche** : Tapez votre recherche (ex: "film d'action")
2. **Résultats visuels** : Les films s'affichent sous forme de cartes avec images
3. **Cliquez** : Cliquez sur une carte pour voir les détails et les recommandations
4. **Images chargées** : Les affiches sont chargées automatiquement de manière asynchrone

## 🔧 Fonctionnement Technique

### Récupération des Affiches

L'application utilise plusieurs méthodes pour obtenir les affiches :

1. **Base de données** : Si une URL d'affiche est stockée dans `meta.poster_url`
2. **API endpoint** : Endpoint `/api/poster/{title}` pour récupérer les affiches
3. **Placeholder** : Si aucune affiche n'est trouvée, génération d'une image avec le titre

### Endpoint API

```
GET /api/poster/{title}?year=2020
```

Retourne :
```json
{
  "poster_url": "https://..."
}
```

## 📝 Améliorations Futures

Pour améliorer encore plus l'affichage des affiches, vous pouvez :

### Intégrer TMDB (The Movie Database)

1. Obtenir une clé API TMDB gratuite sur [TMDB](https://www.themoviedb.org/)
2. Modifier l'endpoint `/api/poster/{title}` pour utiliser l'API TMDB
3. Ajouter la clé API dans votre fichier `.env`

Exemple d'intégration TMDB :
```python
# Dans api/main.py
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.get("/api/poster/{title}")
async def get_poster_tmdb(title: str, year: Optional[int] = None):
    # Recherche sur TMDB
    # Retourne l'URL de l'affiche
```

### Ajouter des Affiches Manuellement

Vous pouvez ajouter des URLs d'affiches dans votre base de données :

```sql
UPDATE films 
SET meta = jsonb_set(COALESCE(meta, '{}'), '{poster_url}', '"https://example.com/poster.jpg"')
WHERE title = 'Nom du Film';
```

## 🎯 Utilisation

1. **Recherchez** : "film d'action", "comédie romantique", etc.
2. **Visualisez** : Les films apparaissent avec leurs affiches
3. **Explorez** : Cliquez sur un film pour plus de détails
4. **Découvrez** : Les recommandations s'affichent aussi avec des images

## 📱 Responsive

Les cartes s'adaptent automatiquement :
- **Desktop** : 3-4 colonnes
- **Tablette** : 2-3 colonnes  
- **Mobile** : 1 colonne

## 🎨 Personnalisation

Vous pouvez personnaliser les cartes dans `static/styles.css` :

- Taille des affiches : Modifiez `padding-top` dans `.film-poster-container`
- Effets hover : Modifiez les transformations dans `.film-card:hover`
- Couleurs des badges : Modifiez `--primary-color` et `--success`

---

**Profitez de votre interface visuelle de recommandation de films ! 🎬✨**

