# Session 2 (7h) — Embedding et API

> Embedder et Retriever : du texte aux vecteurs, des vecteurs à l'API

## Planning

| Horaire | Activité | Type |
|---------|----------|------|
| 0:00-0:30 | Récapitulatif Session 1, crash course pgvector | Cours |
| 0:30-2:15 | Epic 4 : implémentation de rag-embedder | Hands-on |
| 2:15-2:30 | Pause | |
| 2:30-3:00 | Démo : FastAPI patterns, injection de dépendances | Cours |
| 3:00-5:00 | Epic 5 : implémentation de rag-retriever | Hands-on |
| 5:00-5:15 | Pause | |
| 5:15-6:00 | Wire uvicorn, `just serve` + `just query` | Hands-on |
| 6:00-6:30 | Pipeline locale complète : `just pipeline && just serve` | Démo |
| 6:30-7:00 | `just test-all` + `just check-all`, correction | Hands-on |

**Livrable** : le système RAG fonctionne en local. `just query "qu'est-ce que le MLOps ?"` retourne des résultats classés par similarité.

---

## Crash course pgvector (cours, ~15 min)

Concepts clés à comprendre avant de coder :

- **Embedding** : représentation d'un texte sous forme de vecteur de 384 nombres flottants
- **pgvector** : extension PostgreSQL qui ajoute le type `vector(384)` et l'opérateur `<=>` (distance cosinus)
- **Similarité cosinus** : `1 - distance`. Plus le score est proche de 1, plus les textes sont similaires
- **IVFFlat** : index approximatif pour accélérer les recherches (pas exact, mais rapide)
- **Upsert** : `INSERT ... ON CONFLICT DO UPDATE` — évite les doublons

Schéma de la table (voir `infra/init.sql`) :

```sql
CREATE TABLE document_chunks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name VARCHAR(512) NOT NULL,
    chunk_index   INTEGER NOT NULL,
    content       TEXT NOT NULL,
    metadata      JSONB NOT NULL DEFAULT '{}',
    embedding     vector(384) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT uq_document_chunk UNIQUE (document_name, chunk_index)
);
```

---

## Epic 4 — Embedder (hands-on, ~1h45)

### Tâche 4.1 : Comprendre la structure du package

```
python/rag-embedder/
├── rag_embedder/
│   ├── __init__.py       # fourni
│   ├── main.py           # fourni (projen)
│   ├── task_inputs.py    # fourni
│   ├── app.py            # À IMPLÉMENTER
│   └── writer.py         # À IMPLÉMENTER
├── tests/                # fournis
├── pyproject.toml        # fourni
├── justfile              # fourni
└── uv.lock               # fourni
```

```bash
cd python/rag-embedder && just install-dev
just test   # voir ce qui échoue
```

**TaskInputs fournis** : `input_dir` (data/chunks), `output_dir` (data/embeddings), `db_url`, `embedding_model` (all-MiniLM-L6-v2), `batch_size` (32).

### Tâche 4.2 : Implémenter le writer (batch upsert)

**Fichier** : `python/rag-embedder/rag_embedder/writer.py`

**Fonction à implémenter** :

```python
async def write_chunks(session: AsyncSession, chunks: list[ChunkWithEmbedding]) -> int:
```

**Comportement attendu** :
1. Retourner `0` si la liste est vide
2. Pour chaque chunk, chercher un `DocumentChunk` existant par `(document_name, chunk_index)`
3. Si trouvé : mettre à jour `content`, `metadata_` et `embedding`
4. Si non trouvé : créer un nouveau `DocumentChunk` et l'ajouter à la session
5. Appeler `session.flush()` à la fin
6. Retourner le nombre total de lignes affectées

**Imports nécessaires** :

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from lib_orm.models import DocumentChunk
from lib_schemas.schemas import ChunkWithEmbedding
```

**Vérification** :

```bash
just test -- -k test_writer   # 5 tests doivent passer
```

<details>
<summary>Indice 1 : recherche d'un chunk existant</summary>

```python
stmt = select(DocumentChunk).where(
    DocumentChunk.document_name == chunk.document_name,
    DocumentChunk.chunk_index == chunk.chunk_index,
)
result = await session.execute(stmt)
existing = result.scalar_one_or_none()
```

</details>

<details>
<summary>Indice 2 : création d'un nouveau DocumentChunk</summary>

```python
row = DocumentChunk(
    document_name=chunk.document_name,
    chunk_index=chunk.chunk_index,
    content=chunk.content,
    metadata_=chunk.metadata,
    embedding=chunk.embedding,
)
session.add(row)
```

</details>

### Tâche 4.3 : Implémenter App.run()

**Fichier** : `python/rag-embedder/rag_embedder/app.py`

**Méthode à implémenter** : `App.run(self) -> None`

**Comportement attendu** :
1. Afficher la configuration de `task_inputs`
2. Charger les chunks depuis les fichiers JSON dans `input_dir` (`Path.glob("*.json")`)
3. Valider les chunks comme liste de `ChunkInput`
4. Créer un `EmbeddingClient(task_inputs.embedding_model)` et encoder les textes
5. Construire des objets `ChunkWithEmbedding` avec les embeddings
6. Sauvegarder en JSON dans `output_dir/embeddings.json`
7. Écrire dans la base de données via `_write_to_db()` (méthode statique async, appelée via `asyncio.run()`)

**Méthode statique `_write_to_db`** :
1. Obtenir une session async via `get_async_session(task_inputs.db_url)`
2. Appeler `write_chunks(session, results)`
3. Gérer les erreurs de connexion gracieusement (print, pas crash)

**Imports nécessaires** :

```python
import asyncio
import json
from pathlib import Path
from lib_embedding.embedding import EmbeddingClient
from lib_orm.db import get_async_session
from lib_schemas.schemas import ChunkInput, ChunkWithEmbedding
from rag_embedder.task_inputs import task_inputs
from rag_embedder.writer import write_chunks
```

**Vérification** :

```bash
just test -- -k test_app   # 3 tests doivent passer
just test                   # TOUS les tests
just check-all              # ruff + mypy clean
```

<details>
<summary>Indice : chargement des chunks JSON</summary>

```python
all_chunks: list[ChunkInput] = []
for json_file in Path(task_inputs.input_dir).glob("*.json"):
    data = json.loads(json_file.read_text())
    all_chunks.extend([ChunkInput(**item) for item in data])
```

</details>

### Tâche 4.4 : Exécuter l'embedder

Assurez-vous que PostgreSQL tourne et que les chunks existent :

```bash
# Depuis la racine
just load     # produit data/chunks/chunks.json
just embed    # lit les chunks, génère les embeddings, écrit dans pgvector
```

Vérifier dans la base :

```bash
docker exec -it rag-postgres psql -U rag -d rag -c "SELECT count(*) FROM document_chunks;"
```

---

## Epic 5 — Retriever API (hands-on, ~2h30)

### Tâche 5.1 : Comprendre la structure du package

```
python/rag-retriever/
├── rag_retriever/
│   ├── __init__.py          # fourni
│   ├── main.py              # fourni (projen)
│   ├── task_inputs.py       # fourni
│   ├── app.py               # À IMPLÉMENTER
│   ├── api.py               # À IMPLÉMENTER
│   ├── dependencies.py      # À IMPLÉMENTER
│   └── routes/
│       ├── __init__.py      # fourni
│       ├── health.py        # À IMPLÉMENTER
│       ├── search.py        # À IMPLÉMENTER
│       └── documents.py     # À IMPLÉMENTER
├── tests/                   # fournis
├── pyproject.toml           # fourni
├── justfile                 # fourni
└── uv.lock                  # fourni
```

```bash
cd python/rag-retriever && just install-dev
just test   # voir ce qui échoue
```

**TaskInputs fournis** : `host` (0.0.0.0), `port` (8000), `db_url`, `embedding_model`, `top_k` (5).

### Tâche 5.2 : Implémenter les dépendances (DI)

**Fichier** : `python/rag-retriever/rag_retriever/dependencies.py`

Ce module gère les ressources partagées (engine DB + client embedding) comme singletons.

**Variables globales** :

```python
_engine: AsyncEngine | None = None
_embedding_client: EmbeddingClient | None = None
```

**Fonctions à implémenter** :

| Fonction | Rôle |
|----------|------|
| `async init_dependencies()` | Initialise `_engine` et `_embedding_client` |
| `async shutdown_dependencies()` | Dispose `_engine`, remet les globals à `None` |
| `async get_db_session()` | Générateur async qui yield une `AsyncSession` (commit/rollback) |
| `get_embedding_client()` | Retourne le client, `RuntimeError` si non initialisé |
| `async check_db_health()` | Exécute `SELECT 1`, retourne `bool` |
| `check_model_health()` | Retourne `True` si le client existe |

**Vérification** :

```bash
just test -- -k test_dependencies   # 7 tests doivent passer
```

<details>
<summary>Indice : init_dependencies</summary>

```python
async def init_dependencies() -> None:
    global _engine, _embedding_client
    _engine = get_async_engine(task_inputs.db_url)
    _embedding_client = EmbeddingClient(task_inputs.embedding_model)
```

</details>

<details>
<summary>Indice : get_db_session (générateur async)</summary>

```python
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    async with AsyncSession(_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

</details>

### Tâche 5.3 : Implémenter les endpoints de santé

**Fichier** : `python/rag-retriever/rag_retriever/routes/health.py`

**Endpoints** :

| Méthode | Route | Réponse |
|---------|-------|---------|
| GET | `/health` | `{"status": "ok"}` — toujours 200 |
| GET | `/ready` | Vérifie DB + modèle. 200 si tout OK, 503 sinon |

`/ready` retourne :

```json
{"status": "ready", "db": true, "model": true}
```

ou (avec status code 503) :

```json
{"status": "not_ready", "db": false, "model": true}
```

**Vérification** :

```bash
just test -- -k test_health   # 4 tests doivent passer
```

### Tâche 5.4 : Implémenter POST /search

**Fichier** : `python/rag-retriever/rag_retriever/routes/search.py`

C'est l'endpoint principal du système RAG.

**Signature** :

```python
@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    session: AsyncSession = Depends(get_db_session),
    client: EmbeddingClient = Depends(get_embedding_client),
) -> SearchResponse:
```

**Algorithme** :
1. Encoder la query avec `client.encode([body.query])` → vecteur 384-dim
2. Mesurer le temps d'embedding (en ms)
3. Construire la requête SQL pgvector :
   - `1 - (embedding <=> query_embedding)` comme score de similarité
   - Filtrer par `similarity >= body.similarity_threshold`
   - Trier par similarité décroissante
   - Limiter à `body.top_k`
4. Mesurer le temps de recherche (en ms)
5. Construire les `SearchResult` et retourner `SearchResponse`

**Vérification** :

```bash
just test -- -k test_search   # 5 tests doivent passer
```

<details>
<summary>Indice : requête pgvector avec SQLAlchemy</summary>

```python
import time
from sqlalchemy import select, literal_column

query_vector = client.encode([body.query])[0]
similarity = (
    literal_column("1") - DocumentChunk.embedding.cosine_distance(query_vector)
).label("similarity_score")

stmt = (
    select(DocumentChunk, similarity)
    .where(similarity >= body.similarity_threshold)
    .order_by(similarity.desc())
    .limit(body.top_k)
)

start = time.perf_counter()
result = await session.execute(stmt)
rows = result.all()
search_ms = (time.perf_counter() - start) * 1000
```

</details>

### Tâche 5.5 : Implémenter GET /documents/stats

**Fichier** : `python/rag-retriever/rag_retriever/routes/documents.py`

**Endpoint** : `GET /documents/stats`

Retourne un `StatsResponse` :

```json
{
  "total_documents": 5,
  "total_chunks": 42,
  "embedding_dimension": 384,
  "model_name": "all-MiniLM-L6-v2"
}
```

**SQL** : `SELECT count(DISTINCT document_name), count(*) FROM document_chunks`

**Vérification** :

```bash
just test -- -k test_documents   # 2 tests doivent passer
```

### Tâche 5.6 : Implémenter l'API factory

**Fichier** : `python/rag-retriever/rag_retriever/api.py`

**Fonctions** :

1. `lifespan(app)` — context manager async qui appelle `init_dependencies()` au démarrage et `shutdown_dependencies()` à l'arrêt
2. `create_app()` — crée l'app FastAPI avec titre, description, version, lifespan, et enregistre les 3 routers

```python
from rag_retriever.routes.health import router as health_router
from rag_retriever.routes.search import router as search_router
from rag_retriever.routes.documents import router as documents_router
```

### Tâche 5.7 : Implémenter App.run()

**Fichier** : `python/rag-retriever/rag_retriever/app.py`

Démarre uvicorn en mode factory :

```python
uvicorn.run(
    "rag_retriever.api:create_app",
    host=task_inputs.host,
    port=task_inputs.port,
    factory=True,
)
```

**Vérification finale** :

```bash
just test                     # TOUS les tests
just check-all                # ruff + mypy clean
```

### Tâche 5.8 : Tester le système complet

```bash
# Depuis la racine
just pipeline                 # load + embed
just serve                    # démarre l'API sur http://localhost:8000

# Dans un autre terminal
just query "what is MLOps?"
# ou avec curl :
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is MLOps?", "top_k": 5}'
```

Tester aussi les autres endpoints :
- `http://localhost:8000/health`
- `http://localhost:8000/ready`
- `http://localhost:8000/documents/stats`
- `http://localhost:8000/docs` (Swagger UI auto-généré par FastAPI)

---

## Récapitulatif Session 2

À la fin de cette session, vous avez :

- [ ] Implémenté `writer.py` — batch upsert dans pgvector
- [ ] Implémenté `app.py` du rag-embedder — chargement, embedding, sauvegarde
- [ ] `just embed` insère des vecteurs dans PostgreSQL
- [ ] Implémenté `dependencies.py` — injection de dépendances FastAPI
- [ ] Implémenté `routes/health.py` — endpoints /health et /ready
- [ ] Implémenté `routes/search.py` — recherche sémantique avec pgvector
- [ ] Implémenté `routes/documents.py` — statistiques
- [ ] Implémenté `api.py` — application factory FastAPI
- [ ] `just serve` démarre l'API, `just query` retourne des résultats
- [ ] `just test-all` passe pour tous les packages
- [ ] `just check-all` passe pour tous les packages
