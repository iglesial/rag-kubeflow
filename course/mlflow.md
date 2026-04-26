# MLFlow — guide formateur

Ce document couvre les quatre étapes nécessaires pour préparer et animer la session de
comparaison de retrievers avec MLFlow.

---

## 1. Démarrer le serveur MLFlow

MLFlow est déjà dans `docker-compose.yml`. Il suffit de le démarrer avec le reste de
l'infrastructure :

```bash
docker compose up -d
```

Ou uniquement MLFlow si PostgreSQL tourne déjà :

```bash
docker compose up -d mlflow
```

Vérifier que le serveur est prêt :

```bash
docker compose ps   # mlflow doit être "healthy"
```

Interface accessible sur `http://localhost:5000`.

> Le backend SQLite (`mlflow.db`) supporte le Model Registry. Sans lui, les appels à
> `mlflow.register_model()` échouent — ne pas changer le `backend-store-uri`.

---

## 2. Modifier le chunker pour inclure le nom du Pokémon

Le flag `--inject_document_name` est déjà implémenté dans `rag-loader`. Il préfixe chaque
chunk par `Pokémon: {nom}` extrait du nom de fichier (`025-pikachu.md` → `pikachu`).

Pour générer les chunks enrichis **sans écraser les chunks de base**, on pointe vers un
répertoire de sortie différent :

```bash
cd python/rag-loader
uv run main \
  --input_dir ../../data/documents \
  --output_dir ../../data/chunks-name-injection \
  --inject_document_name True
```

Les chunks de base (`data/chunks/chunks.json`) restent intacts.
Les nouveaux chunks sont dans `data/chunks-name-injection/chunks.json`.

---

## 3. Générer les embeddings sans écraser le baseline

L'embedder a deux sorties : le fichier JSON local et la base pgvector. Pour le JSON, on
utilise un répertoire différent. Pour pgvector, il faut **vider la table avant** de charger
les nouveaux embeddings (voir étape suivante).

Générer les embeddings des chunks enrichis :

```bash
cd python/rag-embedder
uv run main \
  --input_dir ../../data/chunks-name-injection \
  --output_dir ../../data/embeddings-name-injection
```

Les embeddings baseline restent dans `data/embeddings/embeddings.json`.
Les nouveaux sont dans `data/embeddings-name-injection/embeddings.json`.

---

## 4. Vider pgvector et charger les nouveaux embeddings

La table `document_chunks` a une contrainte `UNIQUE (document_name, chunk_index)`. Tenter
de charger deux ensembles d'embeddings pour les mêmes documents échouerait. Il faut donc
**vider la table avant chaque rechargement**.

### Vider la table

```bash
docker exec rag-postgres psql -U rag -d rag -c "TRUNCATE document_chunks;"
```

Vérifier que la table est vide :

```bash
docker exec rag-postgres psql -U rag -d rag -c "SELECT count(*) FROM document_chunks;"
# → count = 0
```

### Charger les embeddings name-injection

```bash
cd python/rag-embedder
uv run main \
  --input_dir ../../data/chunks-name-injection \
  --output_dir ../../data/embeddings-name-injection
```

Vérifier le chargement :

```bash
docker exec rag-postgres psql -U rag -d rag \
  -c "SELECT document_name, count(*) FROM document_chunks GROUP BY document_name ORDER BY document_name;"
```

---

## Workflow complet de la session de comparaison

```
Baseline (déjà fait en début de session)
─────────────────────────────────────────
  just load              → data/chunks/chunks.json
  just embed             → pgvector + data/embeddings/embeddings.json
  just serve             → retriever sur :8000
  cd python/students/eval-retriever
  uv run eval_retriever/main.py --approach_tag baseline
                         → run MLFlow "baseline"

Name injection
──────────────────────────────────────────────────
  [loader avec inject]   → data/chunks-name-injection/chunks.json
  TRUNCATE document_chunks
  [embedder name-inj]    → pgvector + data/embeddings-name-injection/embeddings.json
  (just serve tourne déjà)
  uv run eval_retriever/main.py --approach_tag name-injection
                         → run MLFlow "name-injection"

Comparaison dans l'UI MLFlow
─────────────────────────────
  http://localhost:5000
  Expérience : rag-retrieval-comparison
  Sélectionner les deux runs → Compare
```

### Commandes enchaînées pour aller vite

```bash
# Préparer les chunks name-injection
cd python/rag-loader && uv run main --input_dir ../../data/documents --output_dir ../../data/chunks-name-injection --inject_document_name True

# Vider la base et recharger
docker exec rag-postgres psql -U rag -d rag -c "TRUNCATE document_chunks;"
cd python/rag-embedder && uv run main --input_dir ../../data/chunks-name-injection --output_dir ../../data/embeddings-name-injection

# Lancer l'évaluation name-injection
cd python/students/eval-retriever && uv run eval_retriever/main.py --approach_tag name-injection
```

### Pour revenir au baseline si besoin

```bash
docker exec rag-postgres psql -U rag -d rag -c "TRUNCATE document_chunks;"
cd python/rag-embedder && uv run main
# (recharge depuis data/chunks/chunks.json par défaut)
```
