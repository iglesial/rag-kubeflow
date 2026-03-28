# Quickstart — De l'infrastructure au query

> Guide pas-a-pas pour lancer le RAG de bout en bout.
> Pre-requis : avoir suivi le [guide d'installation](setup-guide.md).

## 1. Demarrer l'infrastructure

```bash
# Demarre Docker Desktop, PostgreSQL, Kind cluster, KFP
just infra-up
```

Cela fait, dans l'ordre :

1. Docker Desktop (si pas deja lance)
2. PostgreSQL + pgvector via `docker compose up -d`
3. Creation du cluster Kind `rag-kubeflow`
4. Deploiement de Kubeflow Pipelines (KFP standalone)
5. Chargement des images Docker dans Kind

Verifier que tout est en place :

```bash
just infra-status
```

Tous les pods doivent etre en `Running`.

## 2. Preparer les documents

Placer vos fichiers `.md` ou `.txt` dans le dossier `data/documents/` a la racine du projet :

```
data/
  documents/
    mon-document.md
    autre-fichier.txt
```

## 3. Construire les images Docker

```bash
just build-images
```

Cela construit les images `rag-loader`, `rag-embedder` et `rag-retriever`.

## 4. Charger les images dans Kind

```bash
just kfp-load-images
```

Les images sont maintenant disponibles dans le cluster Kind.

## 5. Lancer le pipeline sur KFP

### Option A : via KFP (Kubeflow Pipelines)

Ouvrir **deux terminaux** :

```bash
# Terminal 1 — port-forward du KFP UI
just kfp-ui
```

```bash
# Terminal 2 — soumettre le pipeline
just kfp-submit
```

Suivre l'execution dans le navigateur : http://localhost:8080

### Option B : en local (sans Kubernetes)

```bash
just pipeline
```

Cela execute le loader puis l'embedder directement sur votre machine.

## 6. Verifier l'execution (KFP)

```bash
# Voir les pods du pipeline
kubectl get pods -n kubeflow --context kind-rag-kubeflow

# Voir le statut de l'infra
just kfp-status
```

Les pods `rag-ingestion-*` apparaissent pendant l'execution et passent en `Completed` une fois termines.

## 7. Demarrer le serveur de recherche

```bash
just serve
```

Le serveur FastAPI demarre sur http://localhost:8000.

- Documentation API : http://localhost:8000/docs
- Health check : http://localhost:8000/health

## 8. Lancer une requete

```bash
just query "qu'est-ce que le machine learning?"
```

Ou directement avec curl :

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "qu est-ce que le machine learning", "top_k": 5}'
```

## 9. Arreter l'infrastructure

```bash
just infra-down
```

Cela supprime le cluster Kind et arrete PostgreSQL.

## Resume des commandes

| Etape | Commande |
|-------|----------|
| Demarrer l'infra | `just infra-up` |
| Verifier l'infra | `just infra-status` |
| Construire les images | `just build-images` |
| Charger les images dans Kind | `just kfp-load-images` |
| Ouvrir le KFP UI | `just kfp-ui` |
| Soumettre le pipeline | `just kfp-submit` |
| Pipeline local (sans K8s) | `just pipeline` |
| Demarrer le retriever | `just serve` |
| Requete | `just query "ma question"` |
| Arreter l'infra | `just infra-down` |
