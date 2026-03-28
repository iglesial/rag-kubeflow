# Session 1 (7h) — Fondations

> Infrastructure, bibliothèques partagées et document loader

## Planning

| Horaire | Activité | Type |
|---------|----------|------|
| 0:00-0:45 | Introduction, architecture, vérification de l'environnement | Cours |
| 0:45-1:15 | Epic 1 : pre-commit, docker-compose, justfile | Guidé |
| 1:15-1:30 | Pause | |
| 1:30-2:00 | Démo : patron package-1, Pydantic BaseSettings | Cours |
| 2:00-3:30 | Epic 2 : découverte des bibliothèques partagées (fournies) | Lecture + exploration |
| 3:30-3:45 | Pause | |
| 3:45-5:45 | Epic 3 : implémentation de rag-loader | Hands-on |
| 5:45-6:30 | Exécution de `just load`, vérification du JSON, tests | Hands-on |
| 6:30-7:00 | Récapitulatif + Q&A | Cours |

**Livrable** : `just load` produit un fichier `data/chunks/chunks.json`. Tous les tests passent.

---

## Epic 1 — Infrastructure (guidé, ~30 min)

Ces fichiers sont **fournis dans le template**. L'enseignant les parcourt avec les étudiants.

### Tâche 1.1 : Vérifier l'environnement

```bash
docker --version          # Docker Desktop installé
python --version          # >= 3.13
uv --version              # uv installé
kind --version            # kind installé
kubectl version --client  # kubectl installé
git --version             # git installé
```

### Tâche 1.2 : Démarrer PostgreSQL

```bash
docker compose up -d
docker compose ps          # postgres healthy
```

Vérifier la connexion :

```bash
docker exec -it rag-postgres psql -U rag -d rag -c "\dt"
```

La table `document_chunks` doit apparaître (créée par `infra/init.sql`).

### Tâche 1.3 : Installer pre-commit

```bash
pip install pre-commit     # ou uv tool install pre-commit
pre-commit install
pre-commit run --all-files # tout doit passer
```

### Tâche 1.4 : Explorer le justfile racine

```bash
just --list                # voir toutes les recettes disponibles
```

Comprendre les recettes `infra-up`, `infra-down`, `load`, `embed`, `serve`, `query`.

---

## Epic 2 — Bibliothèques partagées (fournies, ~1h30)

Les 3 bibliothèques sont **fournies complètes**. L'objectif est de les comprendre car elles seront utilisées dans les packages suivants.

### Tâche 2.1 : Explorer lib-schemas

**Fichier** : `python/lib-schemas/lib_schemas/schemas.py`

Modèles Pydantic partagés entre les packages :

| Classe | Usage |
|--------|-------|
| `ChunkInput` | Chunk de texte (document_name, chunk_index, content, metadata) |
| `ChunkWithEmbedding` | ChunkInput + vecteur embedding (list[float]) |
| `SearchRequest` | Requête API (query, top_k, similarity_threshold) |
| `SearchResult` | Résultat de recherche (chunk_id, document_name, content, similarity_score) |
| `SearchResponse` | Réponse API (results, total_results, timings) |
| `StatsResponse` | Statistiques documents (total_documents, total_chunks, embedding_dimension, model_name) |

**Vérification** :

```bash
cd python/lib-schemas && just test
```

### Tâche 2.2 : Explorer lib-embedding

**Fichier** : `python/lib-embedding/lib_embedding/embedding.py`

- `EmbeddingClient(model_name)` — charge le modèle sentence-transformers
- `encode(texts: list[str]) -> list[list[float]]` — encode une liste de textes en vecteurs 384-dim
- `dimension` — propriété retournant la dimension du modèle

**Vérification** :

```bash
cd python/lib-embedding && just test
```

### Tâche 2.3 : Explorer lib-orm

**Fichiers** :
- `python/lib-orm/lib_orm/db.py` — `get_async_engine()`, `get_async_session()`
- `python/lib-orm/lib_orm/models.py` — ORM `DocumentChunk` (SQLAlchemy + pgvector)

La table `document_chunks` correspond au schéma dans `infra/init.sql` :
- `id` (UUID), `document_name`, `chunk_index`, `content`, `metadata` (JSONB), `embedding` (vector(384))

**Vérification** :

```bash
cd python/lib-orm && just test
```

---

## Epic 3 — Document Loader (hands-on, ~2h)

C'est le premier package que les étudiants **implémentent eux-mêmes**.

### Tâche 3.1 : Comprendre la structure du package

```
python/rag-loader/
├── rag_loader/
│   ├── __init__.py       # fourni
│   ├── main.py           # fourni (projen, ne pas modifier)
│   ├── task_inputs.py    # fourni
│   ├── app.py            # À IMPLÉMENTER
│   ├── reader.py         # À IMPLÉMENTER
│   └── chunker.py        # À IMPLÉMENTER
├── tests/                # fournis
├── pyproject.toml        # fourni
├── justfile              # fourni
└── uv.lock               # fourni
```

Installer les dépendances :

```bash
cd python/rag-loader && just install-dev
```

Exécuter les tests pour voir ce qui échoue :

```bash
just test   # tout doit être rouge sauf test_init et test_task_inputs
```

### Tâche 3.2 : Implémenter le lecteur de documents

**Fichier** : `python/rag-loader/rag_loader/reader.py`

**Fonction à implémenter** :

```python
SUPPORTED_EXTENSIONS = {".txt", ".md"}

def read_documents(input_dir: str) -> list[dict[str, object]]:
```

**Comportement attendu** :
1. Vérifier que `input_dir` existe et est un dossier (sinon `FileNotFoundError` / `NotADirectoryError`)
2. Lister les fichiers `.md` et `.txt` uniquement (non récursif)
3. Trier les fichiers par nom avant traitement
4. Lire chaque fichier en UTF-8 (utiliser `encoding="utf-8-sig"` pour gérer le BOM)
5. Retourner une liste de dicts avec les clés : `document_name`, `content`, `metadata`
6. `metadata` contient `file_size` (int) et `extension` (str)

**Vérification** :

```bash
just test -- -k test_reader   # 8 tests doivent passer
```

<details>
<summary>Indice 1 : structure de base</summary>

```python
from pathlib import Path

def read_documents(input_dir: str) -> list[dict[str, object]]:
    path = Path(input_dir)
    if not path.exists():
        raise FileNotFoundError(...)
    if not path.is_dir():
        raise NotADirectoryError(...)

    documents = []
    for file_path in sorted(path.iterdir()):
        if file_path.suffix in SUPPORTED_EXTENSIONS:
            # lire le fichier et construire le dict
            ...
    return documents
```

</details>

<details>
<summary>Indice 2 : construction du dict retourné</summary>

```python
content = file_path.read_text(encoding="utf-8-sig")
documents.append({
    "document_name": file_path.name,
    "content": content,
    "metadata": {
        "file_size": file_path.stat().st_size,
        "extension": file_path.suffix,
    },
})
```

</details>

### Tâche 3.3 : Implémenter le chunker

**Fichier** : `python/rag-loader/rag_loader/chunker.py`

C'est l'algorithme le plus intéressant de la session : un **recursive character splitter** (~50 lignes).

**Fonctions à implémenter** :

```python
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    ...

def _split_recursive(text: str, chunk_size: int, sep_idx: int) -> list[str]:
    ...

def _merge_with_overlap(segments: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    ...
```

**Algorithme de `chunk_text`** :
1. Lever `ValueError` si `chunk_overlap >= chunk_size`
2. Retourner `[]` si le texte est vide ou ne contient que des espaces
3. Appeler `_split_recursive(text, chunk_size, 0)` pour obtenir des segments
4. Appeler `_merge_with_overlap(segments, chunk_size, chunk_overlap)` pour fusionner avec recouvrement

**Algorithme de `_split_recursive`** :
1. Si `len(text) <= chunk_size` : retourner `[text]`
2. Si `sep_idx >= len(SEPARATORS)` : retourner `[text]` (dernier recours)
3. Séparer le texte avec `SEPARATORS[sep_idx]`
4. Pour le séparateur `""` : découper caractère par caractère (`text[i:i+chunk_size]`)
5. Si le split ne produit qu'un seul morceau : essayer le séparateur suivant
6. Pour `". "` : rattacher le `.` à la fin de chaque segment
7. Filtrer les segments vides, et récurser sur les segments trop longs

**Algorithme de `_merge_with_overlap`** :
1. Fusionner les segments tant que `len(merged) + 1 + len(next) <= chunk_size`
2. Quand la limite est atteinte : sauvegarder le chunk courant, calculer le recouvrement depuis la fin
3. Le recouvrement = derniers `chunk_overlap` caractères du chunk qui vient d'être sauvegardé

**Vérification** :

```bash
just test -- -k test_chunker   # 13 tests doivent passer
```

<details>
<summary>Indice 1 : _split_recursive cas de base</summary>

```python
def _split_recursive(text: str, chunk_size: int, sep_idx: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    if sep_idx >= len(SEPARATORS):
        return [text]

    sep = SEPARATORS[sep_idx]
    if sep == "":
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    ...
```

</details>

<details>
<summary>Indice 2 : _merge_with_overlap boucle principale</summary>

```python
def _merge_with_overlap(segments, chunk_size, chunk_overlap):
    if not segments:
        return []
    chunks = []
    current = segments[0]
    for seg in segments[1:]:
        candidate = current + " " + seg
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            overlap_text = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = (overlap_text + " " + seg).strip() if overlap_text else seg
    chunks.append(current)
    return chunks
```

</details>

### Tâche 3.4 : Implémenter App.run()

**Fichier** : `python/rag-loader/rag_loader/app.py`

**Méthode à implémenter** : `App.run(self) -> None`

**Comportement attendu** :
1. Afficher la configuration de `task_inputs` (input_dir, output_dir, chunk_size, chunk_overlap)
2. Appeler `read_documents(task_inputs.input_dir)`
3. Pour chaque document : appeler `chunk_text()` et créer des objets `ChunkInput` (de `lib_schemas`)
4. Créer le dossier de sortie (`output_dir`) s'il n'existe pas
5. Écrire la liste de chunks en JSON dans `output_dir/chunks.json`
6. Afficher des messages de progression ("Read N documents", "Generated N chunks")

**Imports nécessaires** :

```python
import json
from pathlib import Path
from lib_schemas.schemas import ChunkInput
from rag_loader.chunker import chunk_text
from rag_loader.reader import read_documents
from rag_loader.task_inputs import task_inputs
```

**Vérification** :

```bash
just test -- -k test_app     # 2 tests doivent passer
just test                     # TOUS les tests doivent passer
just check-all                # ruff + mypy clean
```

### Tâche 3.5 : Exécuter le loader

```bash
just run   # depuis python/rag-loader/
# ou depuis la racine :
just load
```

Vérifier le fichier `data/chunks/chunks.json` :

```bash
python -c "import json; chunks = json.load(open('data/chunks/chunks.json')); print(f'{len(chunks)} chunks')"
```

---

## Récapitulatif Session 1

À la fin de cette session, vous avez :

- [ ] PostgreSQL + pgvector fonctionnel (`docker compose ps`)
- [ ] Pre-commit installé et fonctionnel
- [ ] Compris les 3 bibliothèques partagées (lib-schemas, lib-embedding, lib-orm)
- [ ] Implémenté `reader.py` — lecture de fichiers .md/.txt
- [ ] Implémenté `chunker.py` — recursive character splitter
- [ ] Implémenté `app.py` — orchestration du loader
- [ ] `just load` produit `data/chunks/chunks.json`
- [ ] `just test` passe dans `python/rag-loader/`
- [ ] `just check-all` passe dans `python/rag-loader/`
