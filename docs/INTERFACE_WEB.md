# 🌐 Interface Web - Application de Recommandation de Films

## ✨ Fonctionnalités

L'interface web offre une expérience utilisateur moderne et intuitive pour :

- 🔍 **Recherche sémantique** : Recherchez des films en langage naturel
- 📊 **Statistiques** : Consultez les statistiques de la base de données
- 🎬 **Détails des films** : Explorez les informations complètes de chaque film
- 💡 **Recommandations** : Découvrez des films similaires en un clic
- 🎨 **Design moderne** : Interface sombre et élégante

## 🚀 Accéder à l'Interface

1. **Démarrer l'API** :
   ```powershell
   .\venv\Scripts\Activate.ps1
   uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Ouvrir dans le navigateur** :
   - Interface web : `http://127.0.0.1:8000`
   - Documentation API : `http://127.0.0.1:8000/docs`

## 📖 Guide d'Utilisation

### Recherche de Films

1. Dans le champ de recherche, décrivez le type de film que vous cherchez
   - Exemple : "film de science-fiction avec des voyages dans l'espace"
   - Exemple : "comédie romantique des années 2000"

2. Optionnellement, utilisez les filtres :
   - **Année min/max** : Limiter la recherche par période
   - **Genres** : Filtrer par genres (séparés par virgules)
   - **Nombre de résultats** : Choisir combien de films afficher

3. Cliquez sur "Rechercher" ou appuyez sur Entrée

### Explorer un Film

1. Cliquez sur une carte de film dans les résultats
2. Une fenêtre modale s'ouvre avec :
   - Les détails complets du film
   - Les genres et le cast
   - Le synopsis complet
3. Les films similaires s'affichent automatiquement en dessous

### Films Similaires

- Après avoir cliqué sur un film, des recommandations apparaissent
- Cliquez sur une recommandation pour explorer ce film
- Le score de similarité est affiché sur chaque carte

## 🎨 Caractéristiques du Design

- **Thème sombre** : Interface élégante avec thème sombre
- **Responsive** : S'adapte à tous les écrans (desktop, tablette, mobile)
- **Animations fluides** : Transitions et effets visuels soignés
- **Cartes interactives** : Effet hover et clics intuitifs
- **Modal moderne** : Fenêtres popup élégantes pour les détails

## 🔧 Structure des Fichiers

```
static/
├── index.html      # Structure HTML de l'application
├── styles.css      # Styles CSS modernes
└── app.js          # Logique JavaScript et interactions API
```

## 🛠️ Personnalisation

### Modifier les Couleurs

Éditez `static/styles.css` et modifiez les variables CSS :

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --background: #0f172a;
    /* ... autres variables */
}
```

### Ajouter des Fonctionnalités

Modifiez `static/app.js` pour ajouter :
- Nouveaux filtres
- Autres visualisations
- Fonctionnalités supplémentaires

## 📱 Compatibilité Navigateurs

- ✅ Chrome/Edge (recommandé)
- ✅ Firefox
- ✅ Safari
- ✅ Opéra

## ⚡ Performance

- **Chargement rapide** : Assets optimisés
- **Recherche instantanée** : Requêtes API asynchrones
- **Cache intelligent** : Réduction des appels API inutiles

## 🐛 Dépannage

### L'interface ne charge pas

1. Vérifiez que l'API est démarrée
2. Vérifiez que le dossier `static/` existe
3. Consultez la console du navigateur (F12) pour les erreurs

### Les recherches ne fonctionnent pas

1. Vérifiez la connexion à la base de données
2. Assurez-vous que les embeddings sont générés
3. Vérifiez les logs de l'API dans le terminal

### Erreurs dans la console

- Vérifiez que l'API répond sur `http://127.0.0.1:8000`
- Vérifiez que les endpoints sont accessibles
- Consultez `http://127.0.0.1:8000/docs` pour tester l'API

## 🎯 Prochaines Améliorations Possibles

- [ ] Pagination des résultats
- [ ] Filtres avancés par acteur
- [ ] Visualisation des similarités (graphique)
- [ ] Historique des recherches
- [ ] Favoris et collections
- [ ] Mode clair/sombre (toggle)
- [ ] Export des résultats

---

**Profitez de votre interface de recommandation de films ! 🎬✨**

