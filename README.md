# Correcteur Python — Barème Genevois /6

Outil de correction automatique de code Python pour l'enseignement.  
Note finale sur **6** selon le **barème genevois** : `Note = (pts / max) × 5 + 1`

---

## Fonctionnalités

- Correction automatique de code élève (sans exécution de fenêtre graphique)
- **Questions composées** avec sous-parties (a · b · c) et feedback ciblé
- Distribution des points : Exécution · Affichage · Formule · Structure
- Barème genevois avec mention et grille de lecture
- Mode interactif (saisie en direct) ou mode script (correction en batch)

## Répartition des points

| Catégorie | Points | Évalué |
|-----------|--------|--------|
| EXÉCUTION | 2 pts | Le code tourne sans erreur |
| **AFFICHAGE** | **5 pts** ★ | Les résultats affichés sont corrects |
| FORMULE | 3 pts | Algorithme / logique / calcul juste |
| STRUCTURE | 2 pts | Boucles, fonctions, variables, style |

## Concepts couverts

| # | Concept | Exercice |
|---|---------|----------|
| 1 | Boucle `for` | Table de multiplication |
| 2 | Boucle `while` | Validation + compte à rebours |
| 3 | **Fonctions** | `est_pair` / `factorielle` / `maximum` |
| 4 | **Turtle** | Carré + triangle + couleurs |
| 5 | **Listes** | Moyenne / filtre / tri |

## Fichiers

```
correcteur_interactif.py   ← outil principal (interactif + script)
correcteur_universel.py    ← modèle générique (ajouter ses propres exercices)
bareme_turtle_genevois.py  ← barème turtle uniquement (spirale, polygone…)
```

## Utilisation

### Mode interactif
```bash
python correcteur_interactif.py
```
Le programme demande le nom de l'élève, les concepts à corriger, puis le code à coller.

### Mode script (correction en batch)
1. Ouvre `correcteur_interactif.py`
2. Remplis `NOM_ELEVE`, `CONCEPTS_SELECTIONNES` et `CODES_ELEVES` en bas du fichier
3. Lance :
```bash
python correcteur_interactif.py --script
```

### Ajouter un exercice personnalisé
Dans `correcteur_universel.py` :
```python
def eval_mon_exercice(code, succes, sortie, spy, erreur, input_vals=None):
    c = []
    sp = SousPartie("a", "Mon critère", 4)
    cr = Critere("Résultat affiché", 2, "aff")
    cr.ok() if "42" in sortie else cr.ko("42 absent")
    sp.criteres.append(cr)
    c.append(sp)
    return c
```

## Barème genevois — rappel

| Note /6 | % | Mention |
|---------|---|---------|
| 6.0 | 100% | Excellent |
| 5.5 | 90% | Très bien |
| 5.0 | 80% | Bien |
| 4.5 | 70% | Assez bien |
| 4.0 | 60% | Suffisant |
| 3.5 | 50% | Insuffisant |
| 3.0 | 40% | Insuffisant |
| 2.0 | 20% | Faible |
| 1.0 | 0% | Très faible |

## Prérequis

- Python 3.8+
- Aucune dépendance externe (bibliothèque standard uniquement)
- Turtle fonctionne sans `tkinter` (intercepteur intégré)

## Licence

MIT — libre d'utilisation pour l'enseignement.
