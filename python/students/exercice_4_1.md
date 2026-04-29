# Exercice 1 — Évaluer le retriever baseline

## Objectif

Implémenter un harnais d'évaluation qui mesure la qualité de retrieval RAG et
enregistre les résultats dans MLFlow.

---

## Setup

```bash
cd python/students/eval-retriever
just install-dev
just test-metrics -v   # ~7 tests échouent — c'est normal
```

---

## Tâche 1 — métriques (`eval_retriever/metrics.py`)

Implémenter deux méthodes sur la classe `Query` :

### `score` (computed_field)

Rang réciproque du document attendu dans la liste retournée.

- Parcourir `self.retrieved_documents` avec un rang à base 1
- Retourner `1.0 / rang` à la première occurrence de `self.expected_document`
- Retourner `0.0` si le document n'est pas trouvé

### `aggregate(queries, ks)` (staticmethod)

Retourner un dict avec les métriques agrégées sur l'ensemble des requêtes :

| Clé | Formule | Ce que ça mesure |
|-----|---------|-----------------|
| `recall_at_1` | fraction avec `hit_at(1) == True` | Le bon document arrive-t-il **en première position** ? |
| `recall_at_3` | fraction avec `hit_at(3) == True` | Le bon document est-il dans le **top 3** ? |
| `recall_at_5` | fraction avec `hit_at(5) == True` | Le bon document est-il dans le **top 5** ? |
| `mrr` | moyenne de `query.score` | En moyenne, à quelle **position** se trouve le bon document ? |

`recall_at_k` répond à « est-ce que le retriever *trouve* le bon document ? », sans se
soucier de sa position exacte. `mrr` est plus exigeant : il pénalise les cas où le bon
document est trouvé mais relégué en position 3 ou 4 plutôt qu'en tête.

> **Important** : noms avec underscores (`recall_at_k`), pas `@`. MLFlow rejette les `@`.

Vérifier :

```bash
just test-metrics -v   # doit être tout vert
```

---

## Tâche 2 — logging MLFlow (`eval_retriever/app.py`)

Implémenter `App._log_to_mlflow`. La docstring de la méthode liste les étapes exactes.
En résumé :

1. Configurer le serveur et l'expérience avec `mlflow.set_tracking_uri` et `mlflow.set_experiment`
2. Ouvrir un run avec `mlflow.start_run(run_name=...)` dans un bloc `with`
3. À l'intérieur, logger avec :
   - `mlflow.set_tag` — le tag `approach`
   - `mlflow.log_params` — un dict avec `retriever_url`, `top_k`, `similarity_threshold`, `eval_csv_path`, `n_samples`, `n_failures`
   - `mlflow.log_metrics` — les métriques calculées
   - `mlflow.log_artifact` — le fichier CSV de résultats

Vérifier :

```bash
just test-app -v   # doit être tout vert
```

---

## Run baseline

```bash
uv run eval_retriever/main.py
```

Ouvrir **http://localhost:5000** → expérience `rag-retrieval-comparison` → run `baseline`.

Vérifier que vous voyez :
- [ ] Les paramètres loggés
- [ ] Les métriques (`recall_at_1`, `recall_at_3`, `recall_at_5`, `mrr`)
- [ ] L'artifact `results_baseline.csv`

---

➡ Passez à **l'exercice 2** quand le run baseline est visible dans MLFlow.
