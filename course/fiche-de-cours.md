# Fiche de cours

## 1. Identification

| | |
|---|---|
| **Intitulé** | Système RAG et MLOps avec Kubeflow Pipelines |
| **Volume horaire** | 21 heures (3 séances de 7 heures) |
| **Modalité** | Travaux pratiques (100 % hands-on) |
| **Langue** | Français (outils et code en anglais) |
| **Niveau** | M1/M2 — Data Engineering |
| **Enseignant(s)** | _À compléter_ |

## 2. Prérequis

| Domaine | Niveau attendu |
|---------|---------------|
| Python | Intermédiaire : classes, async/await, décorateurs, type hints |
| SQL | SELECT, INSERT, JOIN, index, création de tables |
| Git / GitHub | clone, branch, commit, push, pull request |
| Ligne de commande | Navigation, variables d'environnement, scripts |
| Docker | Images, conteneurs, `docker compose up/down` |
| Kubernetes | _Souhaitable_ : notions de pods, services, kubectl |

## 3. Objectifs pédagogiques

À l'issue de ce cours, l'étudiant sera capable de :

1. **Concevoir un pipeline d'ingestion de données textuelles** — lecture de documents, découpage en chunks avec recouvrement, sérialisation JSON.
2. **Stocker et rechercher des vecteurs avec pgvector** — utiliser PostgreSQL comme base de données vectorielle, effectuer des recherches par similarité cosinus.
3. **Développer une API REST avec FastAPI** — application factory, injection de dépendances, endpoints asynchrones pour la recherche sémantique.
4. **Orchestrer un pipeline ML avec Kubeflow Pipelines sur Kubernetes** — définir des composants KFP, compiler un pipeline, le soumettre à un cluster Kind local.
5. **Appliquer les bonnes pratiques MLOps** — conteneurisation Docker, tests automatisés, linting (ruff), typage strict (mypy), pre-commit hooks.
6. **Structurer un projet Python multi-packages** — gestion des dépendances avec uv, justfile, pyproject.toml, bibliothèques partagées.

## 4. Compétences visées

| Code | Compétence | Objectif(s) |
|------|-----------|-------------|
| C1 | Pipeline de données et traitement de texte | 1 |
| C2 | Bases de données vectorielles et recherche sémantique | 2 |
| C3 | Développement d'API REST (FastAPI, Python asynchrone) | 3 |
| C4 | Orchestration ML (Kubeflow Pipelines, Kubernetes) | 4 |
| C5 | Pratiques MLOps (conteneurisation, qualité de code, tests) | 5, 6 |

## 5. Contenu des séances

### Séance 1 (7h) — Fondations : Infrastructure, bibliothèques partagées et loader

- Mise en place de l'environnement : Docker, pre-commit, `docker compose`, justfile
- Découverte des bibliothèques partagées : schémas Pydantic (`lib-schemas`), client d'embedding (`lib-embedding`), ORM asynchrone (`lib-orm`)
- Implémentation du pipeline de chargement (`rag-loader`) : lecture de fichiers, découpage en chunks (algorithme récursif ~50 lignes), écriture JSON

**Livrable** : `just load` produit un fichier JSON de chunks. Tous les tests des bibliothèques passent.

### Séance 2 (7h) — Embedding et API : Embedder et Retriever

- Vectorisation et stockage dans pgvector : batch upsert asynchrone avec gestion des conflits
- API FastAPI (`rag-retriever`) : factory pattern, injection de dépendances, `POST /search`, `GET /documents/stats`
- Pipeline locale complète : chargement → embedding → recherche sémantique

**Livrable** : le système RAG fonctionne en local. Une requête `just query "qu'est-ce que le MLOps ?"` retourne des résultats pertinents classés par score.

### Séance 3 (7h) — Orchestration : Kubeflow Pipelines sur Kubernetes

- Cluster Kind et déploiement Kubeflow Pipelines (standalone)
- Composants KFP (`@dsl.container_component`), définition du pipeline, compilation YAML
- Conteneurisation (Dockerfiles multi-stage), chargement d'images dans Kind
- Test d'intégration de bout en bout

**Livrable** : le pipeline KFP s'exécute sur le cluster Kind, le test e2e passe, l'interface KFP affiche le run.

## 6. Méthodes pédagogiques

| Méthode | Description |
|---------|------------|
| **TP guidé par issues GitHub** | Chaque tâche est décrite dans une issue GitHub avec objectif, fichiers à modifier, commande de vérification et indices progressifs. |
| **Approche TDD** | Les tests unitaires sont fournis. L'étudiant implémente le code jusqu'à ce que les tests passent. |
| **Démonstrations live** | L'enseignant démontre les concepts complexes (architecture, pgvector, FastAPI, KFP) avant chaque bloc pratique. |
| **Squelettes typés** | Les signatures de fonctions avec type hints sont fournies. L'étudiant implémente les corps de fonctions. |
| **Repository template GitHub** | Les étudiants partent d'un repo template contenant le scaffolding, les bibliothèques partagées, les tests et la configuration. |

## 7. Matériel requis

### Logiciels à installer avant la première séance

| Outil | Version | Usage |
|-------|---------|-------|
| Docker Desktop | Dernière version | Conteneurs, PostgreSQL |
| Python | >= 3.13 | Langage principal |
| uv | Dernière version | Gestionnaire de paquets Python |
| kind | Dernière version | Cluster Kubernetes local |
| kubectl | Dernière version | CLI Kubernetes |
| Git | Dernière version | Versionnement |
| VS Code | Dernière version | Éditeur recommandé (extensions : Python, Ruff) |

### Matériel

- Ordinateur portable (8 Go RAM minimum, 16 Go recommandé)
- Connexion internet (téléchargement des images Docker et du modèle d'embedding lors de la 1re séance)
- Compte GitHub

## 8. Évaluation

### Modalité : évaluation continue

| Critère | Pondération | Détail |
|---------|-------------|--------|
| Progression sur les issues | 40 % | Épiques 1-5 = minimum attendu |
| Qualité du code | 30 % | Tests passants (`just test-all`), lint propre (`just check-all`), pre-commit |
| Pipeline Kubeflow fonctionnel | 20 % | Épique 6 : pipeline soumis et exécuté sur Kind |
| Test d'intégration | 10 % | Épique 7 : test e2e passe (`just e2e`) |

### Rendu

- Repository GitHub avec code source, tests passants, README
- Démonstration live du pipeline complet (5 minutes par étudiant/binôme)

## 9. Ressources

| Ressource | Lien |
|-----------|------|
| Repository template | _À compléter (rag-kubeflow-starter)_ |
| FastAPI | https://fastapi.tiangolo.com |
| pgvector | https://github.com/pgvector/pgvector |
| Kubeflow Pipelines | https://www.kubeflow.org/docs/components/pipelines/ |
| sentence-transformers | https://www.sbert.net |
| uv | https://docs.astral.sh/uv/ |
| kind | https://kind.sigs.k8s.io |
| SQLAlchemy async | https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html |
