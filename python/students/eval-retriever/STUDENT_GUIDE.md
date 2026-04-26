# Student exercise: build the eval-retriever

## The big picture

Your job is to **measure how good a RAG retrieval system is** and log each
measurement to MLFlow so you can compare different configurations. You'll
run this harness against three different retriever setups during the
session: the baseline chunker, the name-injected chunker, and (later) the
fine-tuned embedder. MLFlow will hold all three runs and let you compare
them in one view.

Most of the package is already written for you (CSV loading, HTTP client,
orchestration, error handling). Your job is to write the **two interesting
parts**:

1. The **metric definitions** themselves — recall@k and MRR.
2. The **MLFlow logging** — turning your results into a tracked run.

That's it. ~30 lines of code total across two files.

## Setup

```bash
cd python/students/eval-retriever
just install-dev
just test-metrics -v
```

You should see ~7 test failures with `NotImplementedError`. That's your
starting point. Your goal: **turn every failing test green**.

## Task 1 — implement `Query.score` and `Query.aggregate`

File: `eval_retriever/metrics.py`

### What's already there

- The `Query` pydantic model with fields `query_id`, `query`,
  `expected_document`, `retrieved_documents`.
- `Query.hit_at(k)` — a helper that tells you whether the expected
  document is within the top k retrieved. **Use this.**
- `Query.from_sample(sample, retrieved)` — a constructor helper. You
  don't need to touch it.
- Input validation in `aggregate` (the `ks must be non-empty` and
  `all k values must be >= 1` checks). Already done for you.

### What you need to write

#### 1a. `Query.score` — the per-query reciprocal rank

It's a `@computed_field`, so you implement it as a property that returns
a float. The rule:

- Find the **1-based rank** of `self.expected_document` in
  `self.retrieved_documents` (first hit wins).
- Return `1.0 / rank`.
- If the expected document isn't in the list at all, return `0.0`.

Examples:

| retrieved_documents                          | expected        | score       |
| -------------------------------------------- | --------------- | ----------- |
| `("a.md", "b.md", "c.md")`                   | `"a.md"`        | `1.0`       |
| `("a.md", "b.md", "c.md")`                   | `"b.md"`        | `0.5`       |
| `("a.md", "b.md", "c.md")`                   | `"c.md"`        | `0.333...`  |
| `("a.md", "b.md", "c.md")`                   | `"z.md"`        | `0.0`       |
| `()`                                         | `"a.md"`        | `0.0`       |

**Hint:** `for rank, doc in enumerate(self.retrieved_documents, start=1):`
is a clean way to get 1-based ranks.

#### 1b. `Query.aggregate(queries, ks)` — the batch metrics

A `@staticmethod` that takes a list of `Query` objects and a list of
cutoff values `ks`, and returns a dict of metrics:

```python
{
    "recall_at_1": 0.42,
    "recall_at_3": 0.68,
    "recall_at_5": 0.81,
    "mrr": 0.57,
}
```

Rules:
- **`recall_at_k`** for each `k` in `ks`: fraction of queries where the
  expected document appeared in the top k. Use `query.hit_at(k)`.
- **`mrr`** (mean reciprocal rank): average of `query.score` across
  all queries.
- **Metric names use underscores**, not `@`. MLFlow rejects metric names
  with `@` characters, so use `recall_at_k` not `recall@k`.
- **Empty queries list**: return all zeros for each metric plus `mrr`.

### Run the tests as you go

```bash
just test-metrics -v
```

Each test tells you exactly what's expected. Fix one, re-run, watch it
turn green. This is your **instant feedback loop** — don't skip it.

When all 10 metrics tests pass, you're done with task 1. Move on.

## Task 2 — implement `App._log_to_mlflow`

File: `eval_retriever/app.py`

Once your metrics work, you need to persist them somewhere you can
**compare runs later**. That's what MLFlow does.

### What's already there

Everything else in `app.py`: the orchestration loop, the retriever
client, the CSV writer, the summary print. You just need to fill in
**one method** — `_log_to_mlflow` — which is called at the end of
`run()` with the computed metrics + results CSV path.

### What you need to write

Look at the docstring of `_log_to_mlflow` for the exact steps. The
short version:

1. **Tell MLFlow where the server is**:
   ```python
   mlflow.set_tracking_uri(task_inputs.mlflow_tracking_uri)
   mlflow.set_experiment(task_inputs.experiment_name)
   ```

2. **Open a run** (use a `with` block):
   ```python
   with mlflow.start_run(run_name=task_inputs.approach_tag):
       ...
   ```

3. **Inside the run**, log four things:
   - A **tag**: `approach` = `task_inputs.approach_tag`
     (use `mlflow.set_tag(key, value)`)
   - **Params** (dict): `retriever_url`, `top_k`, `similarity_threshold`,
     `eval_csv_path`, `n_samples`, `n_failures`
     (use `mlflow.log_params(dict)`)
   - **Metrics** (dict): pass the `metrics` argument directly
     (use `mlflow.log_metrics(dict)`)
   - **Artifact**: the `results_csv` file
     (use `mlflow.log_artifact(str(results_csv))`)

### Run the app tests

```bash
just test-app -v
```

The `test_run_scores_queries_and_logs_to_mlflow` test asserts every
MLFlow call was made with the right arguments. When it passes, you're
done.

## End-to-end run

Once both tasks are done, run the harness against the real stack:

```bash
# (Your instructor will have postgres, mlflow, and the retriever running)
just run
```

Then open http://localhost:5000 in a browser, click the
**`rag-retrieval-comparison`** experiment, and find your `baseline` run.
You should see:

- Parameters you logged
- Metrics (`recall_at_1`, `recall_at_3`, `recall_at_5`, `mrr`)
- An artifact called `results_baseline.csv` — click it to see per-query
  hits/misses

## Doing the full session comparison

Once you've confirmed the baseline works, your instructor will walk you
through re-running the pipeline with name injection:

```bash
# Set a different tag so MLFlow keeps your runs separate
# Windows PowerShell:
$env:APPROACH_TAG = "name-injection"
just run
Remove-Item env:APPROACH_TAG
```

Then in the MLFlow UI, **select both runs** and click **Compare**. You
should see `recall_at_k` jump — that's the "cheap data fix beats the
ML fix" moment.

## Hints, gotchas, and common mistakes

- **"My metrics test says 'expected recall_at_1 but got recall@1'"**:
  read the "metric names use underscores" rule again. Use
  `f"recall_at_{k}"` not `f"recall@{k}"`.

- **"NotImplementedError in test_hit_at_invalid_k_raises"**: don't
  panic, this test passes without you implementing anything. If it
  fails, you probably deleted the `hit_at` helper by accident.

- **"test_aggregate_empty_ks_raises fails with ValueError, not
  NotImplementedError"**: the input validation is already done for
  you at the top of `aggregate`. Don't remove it. Put your logic
  after the existing `if not ks:` / `if any(k < 1 ...)` checks.

- **"MLFlow run shows up but has no metrics"**: you probably caught an
  exception and returned early. Make sure `log_metrics` is actually
  reached.

- **"mlflow.start_run() returns something I don't understand"**: treat
  it as a context manager. `with mlflow.start_run(run_name=...) as run:`
  just opens and closes a run scope.

- **"Can I use a `for` loop inside aggregate?"**: yes. Use whatever is
  clearest. A dict comprehension is fine but not required.

## Bonus exercise (if you finish early)

Add a **per-difficulty breakdown** to `aggregate`. Give it an optional
parameter `group_by: Callable[[Query], str] | None = None` and, when
provided, return a nested dict like:

```python
{
    "easy": {"recall_at_1": 0.95, "recall_at_3": 0.98, ...},
    "hard": {"recall_at_1": 0.42, "recall_at_3": 0.61, ...},
}
```

This requires extending the eval CSV with a `difficulty` column and
wiring it through to `EvalSample`. Talk to your instructor about how
to structure it.

## Where to find the reference solution

Your instructor has a reference implementation at
`python/eval-retriever/` (one level up). Try to complete the exercise
without peeking — but if you're stuck for more than 10 minutes, the
reference is there.
