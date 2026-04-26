# Exercice étudiant : construire l'eval-retriever

## Vue d'ensemble

Votre mission est de **mesurer la qualité d'un système de retrieval RAG** et de consigner chaque
mesure dans MLFlow pour pouvoir comparer différentes configurations. Vous ferez tourner ce
harnais contre trois configurations de retriever pendant la session : le chunker de base, le
chunker avec injection de noms, et (plus tard) l'embedder fine-tuné. MLFlow conservera les
trois runs et vous permettra de les comparer en un seul coup d'œil.

La majeure partie du package est déjà écrite (chargement CSV, client HTTP, orchestration,
gestion des erreurs). Votre travail consiste à écrire les **deux parties intéressantes** :

1. Les **définitions des métriques** elles-mêmes — recall@k et MRR.
2. Le **logging MLFlow** — transformer vos résultats en un run traçable.

C'est tout. ~30 lignes de code en tout, réparties sur deux fichiers.

## Installation

```bash
cd python/students/eval-retriever
just install-dev
just test-metrics -v
```

Vous devriez voir ~7 échecs de tests avec `NotImplementedError`. C'est votre point de départ.
Votre objectif : **faire passer tous les tests au vert**.

## Tâche 1 — implémenter `Query.score` et `Query.aggregate`

Fichier : `eval_retriever/metrics.py`

### Ce qui est déjà là

- Le modèle pydantic `Query` avec les champs `query_id`, `query`,
  `expected_document`, `retrieved_documents`.
- `Query.hit_at(k)` — un helper qui indique si le document attendu se trouve dans
  les k premiers résultats. **Utilisez-le.**
- `Query.from_sample(sample, retrieved)` — un helper de construction. Vous n'avez
  pas besoin d'y toucher.
- La validation des entrées dans `aggregate` (les vérifications `ks must be non-empty`
  et `all k values must be >= 1`). Déjà fait pour vous.

### Ce que vous devez écrire

#### 1a. `Query.score` — le rang réciproque par requête

C'est un `@computed_field`, vous l'implémentez donc comme une propriété qui retourne
un float. La règle :

- Trouvez le **rang à base 1** de `self.expected_document` dans
  `self.retrieved_documents` (la première occurrence compte).
- Retournez `1.0 / rang`.
- Si le document attendu n'est pas dans la liste, retournez `0.0`.

Exemples :

| retrieved_documents                          | expected        | score       |
| -------------------------------------------- | --------------- | ----------- |
| `("a.md", "b.md", "c.md")`                   | `"a.md"`        | `1.0`       |
| `("a.md", "b.md", "c.md")`                   | `"b.md"`        | `0.5`       |
| `("a.md", "b.md", "c.md")`                   | `"c.md"`        | `0.333...`  |
| `("a.md", "b.md", "c.md")`                   | `"z.md"`        | `0.0`       |
| `()`                                         | `"a.md"`        | `0.0`       |

#### 1b. `Query.aggregate(queries, ks)` — les métriques agrégées

Un `@staticmethod` qui prend une liste d'objets `Query` et une liste de seuils `ks`,
et retourne un dictionnaire de métriques :

```python
{
    "recall_at_1": 0.42,
    "recall_at_3": 0.68,
    "recall_at_5": 0.81,
    "mrr": 0.57,
}
```

Règles :
- **`recall_at_k`** pour chaque `k` dans `ks` : fraction des requêtes où le document
  attendu est apparu dans les k premiers résultats. Mesure si le retriever *trouve*
  le bon document, quelle que soit sa position exacte. Un `recall_at_1` élevé signifie
  que le bon document arrive souvent en tête ; `recall_at_5` est plus indulgent.
  Utilisez `query.hit_at(k)`.
- **`mrr`** (mean reciprocal rank) : moyenne de `query.score` sur toutes les requêtes.
  Tient compte de la *position* du bon document : arriver 1er vaut 1.0, 2e vaut 0.5,
  3e vaut 0.33, etc. Un MRR proche de 1 signifie que le retriever place quasi
  systématiquement le bon document en première position.
- **Les noms de métriques utilisent des underscores**, pas `@`. MLFlow rejette les `@`
  dans les noms de métriques, utilisez donc `recall_at_k` et non `recall@k`.
- **Liste de requêtes vide** : retournez des zéros pour chaque métrique et pour `mrr`.

### Lancez les tests au fur et à mesure

```bash
just test-metrics -v
```

Chaque test vous indique exactement ce qui est attendu. Corrigez un test, relancez,
regardez-le passer au vert. C'est votre **boucle de feedback instantanée** — ne la
sautez pas.

Quand les 10 tests de métriques passent, vous avez terminé la tâche 1. Passez à la suite.

## Tâche 2 — implémenter `App._log_to_mlflow`

Fichier : `eval_retriever/app.py`

Une fois vos métriques fonctionnelles, vous devez les persister quelque part pour pouvoir
**comparer les runs plus tard**. C'est le rôle de MLFlow.

### Ce qui est déjà là

Tout le reste dans `app.py` : la boucle d'orchestration, le client retriever, l'écriture
CSV, l'affichage du résumé. Vous devez uniquement remplir **une méthode** — `_log_to_mlflow`
— qui est appelée à la fin de `run()` avec les métriques calculées et le chemin du CSV.

### Ce que vous devez écrire

Regardez la docstring de `_log_to_mlflow` pour les étapes exactes. En résumé :

1. **Indiquez à MLFlow où se trouve le serveur** :
   ```python
   mlflow.set_tracking_uri(task_inputs.mlflow_tracking_uri)
   mlflow.set_experiment(task_inputs.experiment_name)
   ```

2. **Ouvrez un run** (utilisez un bloc `with`) :
   ```python
   with mlflow.start_run(run_name=task_inputs.approach_tag):
       ...
   ```

3. **À l'intérieur du run**, loggez quatre choses :
   - Un **tag** : `approach` = `task_inputs.approach_tag`
     (utilisez `mlflow.set_tag(key, value)`)
   - Des **params** (dict) : `retriever_url`, `top_k`, `similarity_threshold`,
     `eval_csv_path`, `n_samples`, `n_failures`
     (utilisez `mlflow.log_params(dict)`)
   - Des **métriques** (dict) : passez l'argument `metrics` directement
     (utilisez `mlflow.log_metrics(dict)`)
   - Un **artifact** : le fichier `results_csv`
     (utilisez `mlflow.log_artifact(str(results_csv))`)

### Lancez les tests de l'application

```bash
just test-app -v
```

Le test `test_run_scores_queries_and_logs_to_mlflow` vérifie que chaque appel MLFlow
a été fait avec les bons arguments. Quand il passe, vous avez terminé.

## Run de bout en bout

Une fois les deux tâches terminées, lancez le harnais contre la vraie stack :

```bash
# (Votre formateur aura démarré postgres, mlflow et le retriever)
just run
```

Puis ouvrez http://localhost:5000 dans un navigateur, cliquez sur l'expérience
**`rag-retrieval-comparison`** et trouvez votre run `baseline`. Vous devriez voir :

- Les paramètres que vous avez loggés
- Les métriques (`recall_at_1`, `recall_at_3`, `recall_at_5`, `mrr`)
- Un artifact appelé `results_baseline.csv` — cliquez dessus pour voir les hits/miss
  par requête

## Comparaison complète de la session

Une fois le baseline validé, votre formateur vous guidera pour relancer le pipeline
avec injection de noms :

```bash
# Passez le tag directement en argument CLI
uv run eval_retriever/main.py --approach_tag "name-injection"
```

Puis dans l'interface MLFlow, **sélectionnez les deux runs** et cliquez sur **Compare**.
Vous devriez voir le `recall_at_k` progresser — c'est le moment « un correctif de données
bon marché bat le correctif ML ».

## Conseils, pièges et erreurs fréquentes

- **"Mon test de métriques dit 'expected recall_at_1 but got recall@1'"** :
  relisez la règle sur les underscores. Utilisez `f"recall_at_{k}"` et non `f"recall@{k}"`.

- **"NotImplementedError dans test_hit_at_invalid_k_raises"** : ne paniquez pas, ce test
  passe sans que vous n'implémentiez quoi que ce soit. S'il échoue, vous avez probablement
  supprimé le helper `hit_at` par accident.

- **"test_aggregate_empty_ks_raises échoue avec ValueError, pas NotImplementedError"** :
  la validation des entrées est déjà faite pour vous en haut de `aggregate`. Ne la supprimez
  pas. Placez votre logique après les vérifications `if not ks:` / `if any(k < 1 ...)`.

- **"Le run MLFlow apparaît mais n'a pas de métriques"** : vous avez probablement levé une
  exception et êtes sorti tôt. Assurez-vous que `log_metrics` est bien atteint.

- **"mlflow.start_run() retourne quelque chose que je ne comprends pas"** : traitez-le comme
  un context manager. `with mlflow.start_run(run_name=...) as run:` ouvre et ferme simplement
  un scope de run.

- **"Puis-je utiliser une boucle `for` dans aggregate ?"** : oui. Utilisez ce qui est le plus
  clair. Une dict comprehension fonctionne aussi mais n'est pas obligatoire.

## Exercice bonus (si vous avez terminé en avance)

Ajoutez un **découpage par difficulté** à `aggregate`. Donnez-lui un paramètre optionnel
`group_by: Callable[[Query], str] | None = None` et, lorsqu'il est fourni, retournez un
dict imbriqué comme :

```python
{
    "easy": {"recall_at_1": 0.95, "recall_at_3": 0.98, ...},
    "hard": {"recall_at_1": 0.42, "recall_at_3": 0.61, ...},
}
```

Cela nécessite d'ajouter une colonne `difficulty` au CSV d'évaluation et de la câbler
jusqu'à `EvalSample`. Parlez à votre formateur de la façon de le structurer.

## Où trouver la solution de référence

Votre formateur dispose d'une implémentation de référence dans
`python/eval-retriever/` (un niveau au-dessus). Essayez de terminer l'exercice sans
regarder — mais si vous êtes bloqué depuis plus de 10 minutes, la référence est là.
