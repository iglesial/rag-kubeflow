# rag-loader — student version

Exercice : ajouter l'injection du nom du Pokémon dans les chunks.

## Démarrage rapide

```bash
just install-dev
just test-verbose   # 2 tests échouent — c'est votre point de départ
```

## Ce que vous devez implémenter

1. **`task_inputs.py`** — ajouter le champ `inject_document_name: bool` (défaut `False`).

2. **`app.py`** — utiliser ce flag pour préfixer le contenu de chaque chunk avec
   `"Pokémon: {pokemon_name}\n\n"` quand il est activé.
   La fonction `_extract_pokemon_name` est déjà implémentée pour vous.

## Vérification

```bash
just test           # tous les tests doivent passer
```

Puis lancer avec injection :

```bash
just run-inject
```
