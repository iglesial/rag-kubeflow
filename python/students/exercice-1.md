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

Retourner un dict avec :

| Clé | Valeur |
|-----|--------|
| `recall_at_1` | fraction des requêtes avec `hit_at(1) == True` |
| `recall_at_3` | fraction des requêtes avec `hit_at(3) == True` |
| `recall_at_5` | fraction des requêtes avec `hit_at(5) == True` |
| `mrr` | moyenne de `query.score` sur toutes les requêtes |

> **Important** : noms avec underscores (`recall_at_k`), pas `@`. MLFlow rejette les `@`.

Vérifier :

```bash
just test-metrics -v   # doit être tout vert
```

---

## Tâche 2 — logging MLFlow (`eval_retriever/app.py`)

Implémenter `App._log_to_mlflow`. La docstring de la méthode liste les étapes exactes.
En résumé :

```python
mlflow.set_tracking_uri(task_inputs.mlflow_tracking_uri)
mlflow.set_experiment(task_inputs.experiment_name)

with mlflow.start_run(run_name=task_inputs.approach_tag):
    mlflow.set_tag("approach", task_inputs.approach_tag)
    mlflow.log_params({
        "retriever_url": task_inputs.retriever_url,
        "top_k": task_inputs.top_k,
        "similarity_threshold": task_inputs.similarity_threshold,
        "eval_csv_path": task_inputs.eval_csv_path,
        "n_samples": n_samples,
        "n_failures": n_failures,
    })
    mlflow.log_metrics(metrics)
    mlflow.log_artifact(str(results_csv))
```

Vérifier :

```bash
just test-app -v   # doit être tout vert
```

---

## Run baseline

```bash
just run
```

Ouvrir **http://localhost:5000** → expérience `rag-retrieval-comparison` → run `baseline`.

Vérifier que vous voyez :
- [ ] Les paramètres loggés
- [ ] Les métriques (`recall_at_1`, `recall_at_3`, `recall_at_5`, `mrr`)
- [ ] L'artifact `results_baseline.csv`

---

➡ Passez à **l'exercice 2** quand le run baseline est visible dans MLFlow.
