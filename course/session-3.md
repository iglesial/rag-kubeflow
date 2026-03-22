# Session 3 (7h) — Orchestration Kubernetes

> Kubeflow Pipelines sur Kind : du local au cluster

## Planning

| Horaire | Activité | Type |
|---------|----------|------|
| 0:00-0:45 | Crash course Kubernetes + KFP | Cours |
| 0:45-1:15 | Création du cluster Kind + déploiement KFP | Guidé |
| 1:15-1:30 | Pause (KFP se déploie en arrière-plan) | |
| 1:30-2:30 | Epic 6 partie 1 : scaffold rag-pipeline, composants KFP | Hands-on |
| 2:30-3:30 | Epic 6 partie 2 : définition du pipeline, Dockerfiles | Hands-on |
| 3:30-3:45 | Pause | |
| 3:45-5:00 | Epic 6 partie 3 : build images, chargement Kind, soumission | Guidé |
| 5:00-5:45 | Epic 7 : test d'intégration e2e | Hands-on |
| 5:45-6:30 | Explorer l'interface KFP, re-lancer le pipeline | Libre |
| 6:30-7:00 | Récapitulatif du cours, évaluation, Q&A | Cours |

**Livrable** : le pipeline KFP s'exécute sur le cluster Kind, le test e2e passe, l'interface KFP affiche le run.

---

## Crash course Kubernetes + KFP (cours, ~45 min)

### Kubernetes — concepts essentiels

| Concept | Explication |
|---------|------------|
| **Pod** | Plus petite unité exécutable. Contient un ou plusieurs conteneurs. |
| **Service** | Point d'accès réseau stable vers un ensemble de pods. |
| **Namespace** | Isolation logique dans un cluster (KFP utilise `kubeflow`). |
| **kubectl** | CLI pour interagir avec le cluster. |
| **Kind** | Kubernetes IN Docker — un cluster K8s complet dans des conteneurs Docker. |

Commandes utiles :

```bash
kubectl get pods -n kubeflow          # voir les pods KFP
kubectl get svc -n kubeflow           # voir les services
kubectl logs <pod-name> -n kubeflow   # logs d'un pod
kubectl describe pod <name> -n kubeflow  # détails d'un pod
```

### Kubeflow Pipelines — concepts essentiels

| Concept | Explication |
|---------|------------|
| **Component** | Étape élémentaire = un conteneur Docker avec des entrées/sorties. |
| **Pipeline** | Graphe acyclique de components avec dépendances de données. |
| **Artifact** | Donnée produite par un component et consommée par un autre. |
| **Run** | Exécution d'un pipeline avec des paramètres donnés. |
| **Compiler** | Traduit le code Python en YAML exécutable par KFP. |

### Architecture du pipeline RAG

```
┌──────────────┐   JSON chunks   ┌────────────────┐
│  rag-loader   │───────────────>│  rag-embedder   │
│  (chunk docs) │   (artifact)   │  (embed+store)  │
└──────────────┘                 └───────┬────────┘
                                         │ writes to
                                         v
                                 PostgreSQL+pgvector
                                 (host.docker.internal:5432)
```

Les pods dans Kind accèdent à PostgreSQL sur l'hôte via `host.docker.internal`.

---

## Création du cluster Kind (guidé, ~30 min)

> **Important** : le déploiement de KFP prend 5-10 minutes. Lancez-le tôt et travaillez sur le code pendant ce temps.

### Étape 1 : Créer le cluster

```bash
kind create cluster --name rag-kubeflow --config infra/kind-config.yaml --wait 60s
```

Vérifier :

```bash
kubectl cluster-info
kubectl get nodes   # doit montrer 1 nœud "Ready"
```

### Étape 2 : Déployer KFP

```bash
# Ressources cluster-scoped
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=2.3.0"
kubectl wait crd/applications.app.k8s.io --for condition=established --timeout=60s

# Environnement platform-agnostic
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=2.3.0"
```

Attendre que les pods soient prêts (5-10 min) :

```bash
kubectl wait pods -l application-crd-id=kubeflow-pipelines -n kubeflow \
  --for condition=Ready --timeout=600s
```

Ou surveiller en temps réel :

```bash
kubectl get pods -n kubeflow -w   # Ctrl+C pour arrêter
```

### Étape 3 : Accéder à l'interface KFP

```bash
just kfp-ui   # port-forward vers http://localhost:8080
```

Ouvrir `http://localhost:8080` dans le navigateur.

> **Alternative rapide** : `just infra-up` fait tout d'un coup (docker-compose + kind + KFP + images).

---

## Epic 6 — Kubeflow Pipeline (hands-on + guidé, ~3h30)

### Tâche 6.1 : Comprendre la structure du package

```
python/rag-pipeline/
├── rag_pipeline/
│   ├── __init__.py          # fourni
│   ├── main.py              # fourni (projen)
│   ├── task_inputs.py       # fourni
│   ├── app.py               # À IMPLÉMENTER
│   ├── pipeline.py          # À IMPLÉMENTER
│   └── components/
│       ├── __init__.py      # fourni
│       ├── loader.py        # À IMPLÉMENTER
│       └── embedder.py      # À IMPLÉMENTER
├── tests/                   # fournis
├── pyproject.toml           # fourni
├── justfile                 # fourni
└── uv.lock                  # fourni
```

```bash
cd python/rag-pipeline && just install-dev
just test   # voir ce qui échoue
```

**TaskInputs fournis** : `pipeline_name` (rag-ingestion), `input_dir` (data/documents), `kubeflow_host` (http://localhost:8080), `compile_only` (False), `chunk_size` (512), `chunk_overlap` (64), `db_url`, `embedding_model`, `batch_size` (32).

### Tâche 6.2 : Implémenter le composant loader

**Fichier** : `python/rag-pipeline/rag_pipeline/components/loader.py`

Un **container component** KFP encapsule un conteneur Docker comme étape de pipeline.

```python
from kfp import dsl

LOADER_IMAGE = "rag-loader:local"

@dsl.container_component
def loader_component(
    input_dir: str,
    chunk_size: int,
    chunk_overlap: int,
    chunks_artifact: dsl.Output[dsl.Artifact],
) -> dsl.ContainerSpec:
```

**Comportement** : retourner un `dsl.ContainerSpec` qui :
1. Utilise l'image `rag-loader:local`
2. Exécute la commande `["python", "-m", "rag_loader.main"]`
3. Passe les arguments CLI : `--input-dir`, `--output-dir` (chemin de l'artifact), `--chunk-size`, `--chunk-overlap`

**Vérification** :

```bash
just test -- -k test_loader   # tests doivent passer
```

<details>
<summary>Indice : ContainerSpec</summary>

```python
return dsl.ContainerSpec(
    image=LOADER_IMAGE,
    command=["python", "-m", "rag_loader.main"],
    args=[
        "--input-dir", input_dir,
        "--output-dir", chunks_artifact.path,
        "--chunk-size", str(chunk_size),
        "--chunk-overlap", str(chunk_overlap),
    ],
)
```

</details>

### Tâche 6.3 : Implémenter le composant embedder

**Fichier** : `python/rag-pipeline/rag_pipeline/components/embedder.py`

```python
from kfp import dsl

EMBEDDER_IMAGE = "rag-embedder:local"

@dsl.container_component
def embedder_component(
    chunks_artifact: dsl.Input[dsl.Artifact],
    db_url: str,
    embedding_model: str,
    batch_size: int,
    embeddings_artifact: dsl.Output[dsl.Artifact],
) -> dsl.ContainerSpec:
```

Même structure que le loader : image `rag-embedder:local`, commande `python -m rag_embedder.main`, arguments CLI.

**Vérification** :

```bash
just test -- -k test_embedder   # tests doivent passer
```

### Tâche 6.4 : Implémenter la définition du pipeline

**Fichier** : `python/rag-pipeline/rag_pipeline/pipeline.py`

```python
from kfp import dsl
from rag_pipeline.components.embedder import embedder_component
from rag_pipeline.components.loader import loader_component

@dsl.pipeline(
    name="RAG Ingestion Pipeline",
    description="Load documents, chunk, embed, and store in pgvector.",
)
def rag_ingestion_pipeline(
    input_dir: str = "/data/documents",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    db_url: str = "postgresql+asyncpg://rag:rag@host.docker.internal:5432/rag",
    embedding_model: str = "all-MiniLM-L6-v2",
    batch_size: int = 32,
) -> None:
```

**Comportement** :
1. Appeler `loader_component()` avec `input_dir`, `chunk_size`, `chunk_overlap`
2. Récupérer l'artifact de sortie du loader (`chunks_artifact`)
3. Appeler `embedder_component()` avec l'artifact du loader en entrée + `db_url`, `embedding_model`, `batch_size`

Le chaînage des composants via artifacts crée automatiquement la dépendance d'exécution.

**Vérification** :

```bash
just test -- -k test_pipeline   # 5 tests doivent passer
```

<details>
<summary>Indice : chaînage des composants</summary>

```python
loader_task = loader_component(
    input_dir=input_dir,
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)

embedder_component(
    chunks_artifact=loader_task.outputs["chunks_artifact"],
    db_url=db_url,
    embedding_model=embedding_model,
    batch_size=batch_size,
)
```

</details>

### Tâche 6.5 : Implémenter App.run()

**Fichier** : `python/rag-pipeline/rag_pipeline/app.py`

**Méthode à implémenter** : `App.run(self) -> None`

**Comportement** :
1. Afficher la configuration de `task_inputs`
2. Compiler le pipeline en YAML avec `kfp.compiler.Compiler().compile()`
3. Si `compile_only=True` : afficher le chemin du YAML et retourner
4. Sinon : créer un `kfp.client.Client(host=kubeflow_host)` et soumettre le pipeline
5. Gérer les erreurs de soumission gracieusement

**Imports** :

```python
from kfp import compiler, client
from rag_pipeline.pipeline import rag_ingestion_pipeline
from rag_pipeline.task_inputs import task_inputs
```

**Vérification** :

```bash
just test -- -k test_app       # 2 tests doivent passer
just test                       # TOUS les tests
just check-all                  # ruff + mypy clean
```

### Tâche 6.6 : Créer les Dockerfiles

**Fichier** : `python/rag-loader/Dockerfile`

Structure multi-stage :

```dockerfile
# --- Builder ---
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier les dépendances partagées
COPY python/lib-schemas python/lib-schemas

# Copier le package
COPY python/rag-loader python/rag-loader

# Installer
RUN cd python/rag-loader && uv sync --no-dev --frozen

# --- Runtime ---
FROM python:3.13-slim
COPY --from=builder /python/rag-loader/.venv /python/rag-loader/.venv
COPY --from=builder /python/rag-loader/rag_loader /python/rag-loader/rag_loader
COPY --from=builder /python/lib-schemas/lib_schemas /python/rag-loader/lib_schemas

# Données sample baked dans l'image
COPY data/documents /data/documents

ENV PATH="/python/rag-loader/.venv/bin:$PATH"
ENTRYPOINT ["python", "-m", "rag_loader.main"]
```

**Fichier** : `python/rag-embedder/Dockerfile`

Même structure, mais avec 3 libs partagées (lib-schemas, lib-embedding, lib-orm).

### Tâche 6.7 : Build + chargement dans Kind

```bash
# Depuis la racine
just build-images              # build les 3 images Docker
just kfp-load-images           # charger loader + embedder dans Kind
```

Vérifier que les images sont dans le cluster :

```bash
docker exec rag-kubeflow-control-plane crictl images | grep rag
```

### Tâche 6.8 : Soumettre le pipeline

```bash
# Compiler uniquement (pour vérifier le YAML)
cd python/rag-pipeline
just run -- --compile-only

# Soumettre au cluster (KFP UI doit être accessible)
just run
```

Ouvrir `http://localhost:8080` et observer le pipeline dans l'interface KFP :
- Vérifier que les deux étapes (loader, embedder) apparaissent
- Cliquer sur chaque étape pour voir les logs
- Vérifier que le run est vert (succès)

---

## Epic 7 — Test d'intégration e2e (hands-on, ~45 min)

### Tâche 7.1 : Exécuter le test e2e

Le test d'intégration est **fourni** dans `tests/e2e/test_full_pipeline.py`. Il vérifie le pipeline complet : load → embed → search.

```bash
# Depuis la racine (PostgreSQL doit tourner)
just e2e
```

Le test :
1. Exécute le loader sur des documents de test
2. Exécute l'embedder pour vectoriser les chunks
3. Lance une requête de recherche via l'API
4. Vérifie que les résultats sont pertinents

### Tâche 7.2 : Déboguer les problèmes éventuels

Problèmes courants et solutions :

| Problème | Solution |
|----------|---------|
| `Connection refused` (DB) | Vérifier `docker compose ps` — PostgreSQL doit tourner |
| `ImagePullBackOff` dans KFP | Les images ne sont pas dans Kind → `just kfp-load-images` |
| Pipeline timeout | Les pods prennent du temps à démarrer → vérifier `kubectl get pods -n kubeflow` |
| `host.docker.internal` ne résout pas | Vérifier `infra/kind-config.yaml` — le mapping doit exister |

---

## Explorer l'interface KFP (libre, ~45 min)

Activités suggérées :

1. **Re-lancer le pipeline** avec des paramètres différents (chunk_size, chunk_overlap)
2. **Explorer les artifacts** : voir le JSON produit par le loader
3. **Consulter les logs** de chaque étape
4. **Comparer des runs** avec des paramètres différents
5. **Vérifier la base** : combien de chunks après un nouveau run ?

```bash
docker exec -it rag-postgres psql -U rag -d rag -c \
  "SELECT document_name, count(*) FROM document_chunks GROUP BY document_name;"
```

---

## Récapitulatif Session 3 (et du cours)

À la fin de cette session, vous avez :

- [ ] Cluster Kind fonctionnel avec KFP
- [ ] Implémenté les composants KFP (loader + embedder)
- [ ] Implémenté la définition du pipeline (chaînage via artifacts)
- [ ] Implémenté App.run() pour compiler et soumettre
- [ ] Créé les Dockerfiles multi-stage
- [ ] Chargé les images dans Kind
- [ ] Soumis et exécuté le pipeline via KFP
- [ ] Test e2e passe (`just e2e`)
- [ ] `just test-all` passe pour tous les packages
- [ ] `just check-all` passe pour tous les packages

### Ce que vous avez construit en 21 heures

```
Documents .md/.txt
    │
    ▼
[rag-loader]  ──── chunk_text() ────> chunks.json
    │                                      │
    │              KFP Pipeline (Kind)     │
    ▼                                      ▼
[rag-embedder] ── encode() + upsert ──> PostgreSQL+pgvector
                                              │
                                              ▼
                                        [rag-retriever]
                                         POST /search
                                         FastAPI :8000
```

Un système RAG complet, orchestré par Kubernetes, avec tests, linting, et typage strict.
