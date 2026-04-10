"""Application module for eval-retriever."""

import csv
from pathlib import Path

import mlflow

from eval_retriever.eval_loader import EvalSample, load_eval_samples
from eval_retriever.metrics import DEFAULT_KS, Query
from eval_retriever.retriever_client import RetrieverClient
from eval_retriever.task_inputs import task_inputs


class App:
    """Retrieval quality evaluation application."""

    def run(self) -> None:
        """
        Run the eval harness end-to-end.

        Reads the golden set, queries the retriever for each row, scores
        the results, logs params/metrics/artifact to MLFlow, and prints a
        summary table to stdout.
        """
        self._print_config()

        samples = load_eval_samples(task_inputs.eval_csv_path)
        print(f"Loaded {len(samples)} eval samples")
        if not samples:
            print("No samples to evaluate — aborting.")
            return

        with RetrieverClient(
            base_url=task_inputs.retriever_url,
            timeout_s=task_inputs.request_timeout_s,
        ) as client:
            queries, failures = self._score_all(client, samples)

        metrics = Query.aggregate(queries, ks=DEFAULT_KS)

        results_dir = Path(task_inputs.results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        results_csv = results_dir / f"results_{task_inputs.approach_tag}.csv"
        self._write_results_csv(results_csv, samples, queries)

        self._log_to_mlflow(
            metrics=metrics,
            n_samples=len(samples),
            n_failures=failures,
            results_csv=results_csv,
        )
        self._print_summary(metrics, failures)

    def _print_config(self) -> None:
        """Print the resolved task inputs for human inspection."""
        print(f"Eval CSV:            {task_inputs.eval_csv_path}")
        print(f"Retriever URL:       {task_inputs.retriever_url}")
        print(f"Top-k:               {task_inputs.top_k}")
        print(f"Similarity thresh.:  {task_inputs.similarity_threshold}")
        print(f"Approach tag:        {task_inputs.approach_tag}")
        print(f"MLFlow tracking URI: {task_inputs.mlflow_tracking_uri}")
        print(f"MLFlow experiment:   {task_inputs.experiment_name}")

    def _score_all(
        self,
        client: RetrieverClient,
        samples: list[EvalSample],
    ) -> tuple[list[Query], int]:
        """
        Query the retriever for each sample and score the response.

        Parameters
        ----------
        client : RetrieverClient
            Connected retriever client.
        samples : list[EvalSample]
            Eval samples to score.

        Returns
        -------
        tuple[list[Query], int]
            The list of scored queries, and the number of retriever failures
            that were recorded as empty retrieved lists.
        """
        queries: list[Query] = []
        failures = 0
        for idx, sample in enumerate(samples, start=1):
            try:
                retrieved = client.search(
                    query=sample.query,
                    top_k=task_inputs.top_k,
                    similarity_threshold=task_inputs.similarity_threshold,
                )
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"[{idx}/{len(samples)}] retriever error for id={sample.id}: {exc}")
                retrieved = []

            queries.append(
                Query(
                    query_id=sample.id,
                    expected_document=sample.expected_document,
                    retrieved_documents=tuple(retrieved),
                )
            )
            if idx % 25 == 0:
                print(f"  scored {idx}/{len(samples)}")
        return queries, failures

    def _write_results_csv(
        self,
        path: Path,
        samples: list[EvalSample],
        queries: list[Query],
    ) -> None:
        """
        Write a per-query results CSV for drill-down inspection.

        Parameters
        ----------
        path : Path
            Output CSV path.
        samples : list[EvalSample]
            The eval samples, zipped with ``queries`` by index.
        queries : list[Query]
            The scored queries.
        """
        with path.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.writer(fp)
            writer.writerow(
                [
                    "id",
                    "query",
                    "expected_document",
                    "retrieved_documents",
                    "hit@1",
                    "hit@3",
                    "hit@5",
                    "reciprocal_rank",
                ]
            )
            for sample, query in zip(samples, queries, strict=True):
                writer.writerow(
                    [
                        sample.id,
                        sample.query,
                        sample.expected_document,
                        "|".join(query.retrieved_documents),
                        int(query.hit_at(1)),
                        int(query.hit_at(3)),
                        int(query.hit_at(5)),
                        f"{query.score:.4f}",
                    ]
                )
        print(f"Per-query results written to {path}")

    def _log_to_mlflow(
        self,
        metrics: dict[str, float],
        n_samples: int,
        n_failures: int,
        results_csv: Path,
    ) -> None:
        """
        Log params, metrics, and the results CSV artifact to MLFlow.

        Parameters
        ----------
        metrics : dict[str, float]
            Aggregated metrics returned by ``Query.aggregate``.
        n_samples : int
            Total number of samples in the eval set.
        n_failures : int
            Number of samples that failed to reach the retriever.
        results_csv : Path
            Path to the per-query results CSV to upload as an artifact.
        """
        mlflow.set_tracking_uri(task_inputs.mlflow_tracking_uri)
        mlflow.set_experiment(task_inputs.experiment_name)

        with mlflow.start_run(run_name=task_inputs.approach_tag):
            mlflow.set_tag("approach", task_inputs.approach_tag)
            mlflow.log_params(
                {
                    "retriever_url": task_inputs.retriever_url,
                    "top_k": task_inputs.top_k,
                    "similarity_threshold": task_inputs.similarity_threshold,
                    "eval_csv_path": task_inputs.eval_csv_path,
                    "n_samples": n_samples,
                    "n_failures": n_failures,
                }
            )
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(results_csv))

    def _print_summary(self, metrics: dict[str, float], n_failures: int) -> None:
        """
        Print the aggregated metrics to stdout as a readable table.

        Parameters
        ----------
        metrics : dict[str, float]
            Aggregated metrics returned by ``Query.aggregate``.
        n_failures : int
            Number of retriever failures during the run.
        """
        print()
        print(f"=== {task_inputs.approach_tag} ===")
        for name, value in metrics.items():
            print(f"  {name:<12} {value:.4f}")
        if n_failures:
            print(f"  retriever failures: {n_failures}")
