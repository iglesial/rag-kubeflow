# eval-retriever

Retrieval quality evaluation harness for the RAG system. Loads a ground-truth
eval set, queries the running `rag-retriever` service, computes recall@k and
MRR metrics, and logs each run to MLFlow so multiple retrieval configurations
(baseline chunker, name-injected chunker, fine-tuned embedder) can be compared
side-by-side.

## Quick start

```bash
# 1. Bring up infra (postgres + mlflow)
just infra-up

# 2. Ingest + embed your documents (from repo root)
cd python/rag-loader && just run
cd ../rag-embedder && just run

# 3. Start the retriever
cd ../rag-retriever && just run

# 4. Evaluate against the golden set, logging to MLFlow
cd ../eval-retriever
APPROACH_TAG=baseline just run

# 5. Open the MLFlow UI
open http://localhost:5000
```

## Configuration

All inputs are plain `pydantic-settings` env vars or CLI flags:

| Name                   | Default                               | Description                                                 |
| ---------------------- | ------------------------------------- | ----------------------------------------------------------- |
| `eval_csv_path`        | `../../data/eval/eval_set.csv`        | Path to the ground-truth eval set                           |
| `retriever_url`        | `http://localhost:8000`               | Base URL of the running `rag-retriever` service             |
| `top_k`                | `5`                                   | Number of chunks to retrieve per query                      |
| `approach_tag`         | `baseline`                            | MLFlow tag identifying the retrieval configuration          |
| `mlflow_tracking_uri`  | `http://localhost:5000`               | MLFlow server URL                                           |
| `experiment_name`      | `rag-retrieval-comparison`            | MLFlow experiment name                                      |
| `results_dir`          | `../../data/eval-results`             | Where to write per-query `results.csv` before MLFlow upload |

## Eval set format

CSV with columns (the Pokémon-course eval set, but the format is generic):

- `ID` — row id
- `Requête (Query)` — query text
- `Correspondance (Content Match)` — expected passage (human reference, not scored)
- `Nom du Document` — ground-truth document filename (used for scoring)
- `Chunk ID` — ground-truth chunk index (informational, not scored)

## Metrics

- **recall@1 / recall@3 / recall@5** — fraction of queries whose expected
  document is retrieved in the top k
- **MRR** — mean reciprocal rank of the first correct document (0 if missing)

Per-query results are written to `results.csv` and logged as an MLFlow
artifact for drill-down in the UI.
