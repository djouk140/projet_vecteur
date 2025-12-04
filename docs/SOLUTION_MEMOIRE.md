# Solution au problème de mémoire insuffisante (Erreur 1455)

## Problème

L'erreur "Le fichier de pagination est insuffisant pour terminer cette opération. (os error 1455)" se produit lorsque Windows manque de mémoire virtuelle lors du chargement du modèle SentenceTransformer.

## Solutions

### Solution 1 : Augmenter le fichier de pagination Windows (Recommandé)

1. Ouvrez **Paramètres système avancés** :
   - Appuyez sur `Win + R`
   - Tapez `sysdm.cpl` et appuyez sur Entrée
   - Allez dans l'onglet **Avancé**
   - Cliquez sur **Paramètres** dans la section "Performances"

2. Dans l'onglet **Avancé**, cliquez sur **Modifier** dans la section "Mémoire virtuelle"

3. Décochez **"Gérer automatiquement la taille du fichier d'échange pour tous les lecteurs"**

4. Sélectionnez votre lecteur système (généralement C:)

5. Sélectionnez **"Taille personnalisée"** et définissez :
   - **Taille initiale** : 4096 MB (ou plus si vous avez beaucoup de RAM)
   - **Taille maximale** : 8192 MB (ou plus)

6. Cliquez sur **Définir** puis **OK**

7. **Redémarrez votre ordinateur** pour que les changements prennent effet

### Solution 2 : Utiliser un modèle plus léger

Modifiez votre fichier `.env` pour utiliser un modèle plus léger :

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

**Note** : Si vous changez le modèle, vous devrez :
1. Modifier le schéma SQL pour utiliser 384 dimensions au lieu de 768
2. Régénérer tous les embeddings avec le nouveau modèle

### Solution 3 : Libérer de la mémoire

1. Fermez les applications inutiles
2. Fermez les onglets de navigateur non utilisés
3. Redémarrez votre ordinateur
4. Vérifiez qu'aucun autre processus ne consomme beaucoup de mémoire

### Solution 4 : Vérifier la mémoire disponible

```powershell
# Vérifier la mémoire disponible
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
```

### Solution 5 : Utiliser un modèle pré-téléchargé

Si le modèle doit être téléchargé à chaque fois, téléchargez-le manuellement une fois :

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
# Le modèle sera sauvegardé dans le cache
```

## Modèles recommandés par taille mémoire

| Modèle | Dimensions | Taille mémoire | Qualité |
|--------|------------|----------------|---------|
| `all-MiniLM-L6-v2` | 384 | ~80 MB | Bonne |
| `all-mpnet-base-v2` | 768 | ~420 MB | Excellente |
| `paraphrase-multilingual-mpnet-base-v2` | 768 | ~420 MB | Excellente (multilingue) |

## Vérification après correction

Après avoir appliqué une solution, testez à nouveau l'API :

```bash
python -m uvicorn api.main:app --reload
```

Puis testez une recherche dans l'interface web.

