"""Tests for the eval-retriever App orchestration."""

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eval_retriever.app import App
from eval_retriever.eval_loader import EvalSample

CSV_HEADER = "ID,Requête (Query),Correspondance (Content Match),Nom du Document,Chunk ID\n"


def _write_eval_csv(path: Path, rows: list[tuple[str, str, str]]) -> Path:
    """
    Write a minimal eval CSV.

    Parameters
    ----------
    path : Path
        Destination path.
    rows : list[tuple[str, str, str]]
        Tuples of ``(id, query, expected_document)``.

    Returns
    -------
    Path
        The written CSV path.
    """
    body = "".join(f'{rid},{query},"""ref""",{doc},0\n' for rid, query, doc in rows)
    path.write_text(CSV_HEADER + body, encoding="utf-8")
    return path


@pytest.fixture
def fake_task_inputs(tmp_path: Path) -> tuple[MagicMock, Path, Path]:
    """
    Build a MagicMock for task_inputs plus eval CSV and results dir paths.

    Parameters
    ----------
    tmp_path : Path
        Pytest temp directory.

    Returns
    -------
    tuple[MagicMock, Path, Path]
        The mock task_inputs, the eval CSV path, and the results directory.
    """
    eval_csv = _write_eval_csv(
        tmp_path / "eval.csv",
        [
            ("1", "Qui est Pikachu", "025-pikachu.md"),
            ("2", "Qui est Bulbi", "001-bulbizarre.md"),
            ("3", "Qui est Carapuce", "007-carapuce.md"),
        ],
    )
    results_dir = tmp_path / "results"

    mock = MagicMock()
    mock.eval_csv_path = str(eval_csv)
    mock.retriever_url = "http://test"
    mock.top_k = 5
    mock.similarity_threshold = 0.0
    mock.approach_tag = "baseline"
    mock.mlflow_tracking_uri = "http://mlflow"
    mock.experiment_name = "test-experiment"
    mock.results_dir = str(results_dir)
    mock.request_timeout_s = 10.0
    return mock, eval_csv, results_dir


def test_run_scores_queries_and_logs_to_mlflow(
    fake_task_inputs: tuple[MagicMock, Path, Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    End-to-end orchestration: score 3 queries, write CSV, call MLFlow.

    Parameters
    ----------
    fake_task_inputs : tuple
        Fake task_inputs mock and paths from the fixture.
    capsys : pytest.CaptureFixture[str]
        Captures stdout for assertion.
    """
    mock_inputs, _, results_dir = fake_task_inputs

    # First query: perfect hit at rank 1
    # Second query: hit at rank 2
    # Third query: miss (empty retrieval)
    retriever_responses = {
        "Qui est Pikachu": ["025-pikachu.md", "002-herbizarre.md"],
        "Qui est Bulbi": ["002-herbizarre.md", "001-bulbizarre.md", "003-florizarre.md"],
        "Qui est Carapuce": [],
    }

    fake_client = MagicMock()
    fake_client.search.side_effect = lambda query, top_k, similarity_threshold: (  # noqa: ARG005
        retriever_responses[query]
    )
    fake_client.__enter__ = lambda self: self  # noqa: ARG005
    fake_client.__exit__ = lambda self, *a: None  # noqa: ARG005

    with (
        patch("eval_retriever.app.task_inputs", mock_inputs),
        patch("eval_retriever.app.RetrieverClient", return_value=fake_client) as client_cls,
        patch("eval_retriever.app.mlflow") as mock_mlflow,
    ):
        mock_mlflow.start_run.return_value.__enter__ = lambda self: self  # noqa: ARG005
        mock_mlflow.start_run.return_value.__exit__ = lambda self, *a: None  # noqa: ARG005

        App().run()

    # Retriever client was constructed with the configured URL + timeout
    client_cls.assert_called_once_with(base_url="http://test", timeout_s=10.0)

    # MLFlow was configured and populated
    mock_mlflow.set_tracking_uri.assert_called_once_with("http://mlflow")
    mock_mlflow.set_experiment.assert_called_once_with("test-experiment")
    mock_mlflow.start_run.assert_called_once_with(run_name="baseline")
    mock_mlflow.set_tag.assert_called_once_with("approach", "baseline")

    # Params contain the expected keys
    params = mock_mlflow.log_params.call_args.args[0]
    assert params["retriever_url"] == "http://test"
    assert params["top_k"] == 5
    assert params["n_samples"] == 3
    assert params["n_failures"] == 0

    # Metrics computed correctly:
    # Hit@1: 1/3 (only Pikachu); Hit@3: 2/3; Hit@5: 2/3; MRR: (1 + 0.5 + 0)/3
    metrics = mock_mlflow.log_metrics.call_args.args[0]
    assert metrics["recall@1"] == pytest.approx(1 / 3)
    assert metrics["recall@3"] == pytest.approx(2 / 3)
    assert metrics["recall@5"] == pytest.approx(2 / 3)
    assert metrics["mrr"] == pytest.approx((1.0 + 0.5 + 0.0) / 3)

    # Results CSV was created with a row per query
    results_csv = results_dir / "results_baseline.csv"
    assert results_csv.exists()
    with results_csv.open(encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    assert len(rows) == 3
    assert rows[0]["id"] == "1"
    assert rows[0]["hit@1"] == "1"
    assert rows[1]["hit@1"] == "0"
    assert rows[1]["hit@3"] == "1"
    assert rows[2]["hit@1"] == "0"
    assert rows[2]["retrieved_documents"] == ""

    # Artifact was logged
    mock_mlflow.log_artifact.assert_called_once()
    assert str(results_csv) in mock_mlflow.log_artifact.call_args.args[0]

    # Summary was printed
    out = capsys.readouterr().out
    assert "=== baseline ===" in out
    assert "recall@1" in out


def test_run_records_retriever_errors_as_empty_results(
    fake_task_inputs: tuple[MagicMock, Path, Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Retriever failures are logged, recorded as misses, and counted.

    Parameters
    ----------
    fake_task_inputs : tuple
        Fake task_inputs mock and paths from the fixture.
    capsys : pytest.CaptureFixture[str]
        Captures stdout.
    """
    mock_inputs, _, _ = fake_task_inputs

    fake_client = MagicMock()
    fake_client.search.side_effect = RuntimeError("retriever down")
    fake_client.__enter__ = lambda self: self  # noqa: ARG005
    fake_client.__exit__ = lambda self, *a: None  # noqa: ARG005

    with (
        patch("eval_retriever.app.task_inputs", mock_inputs),
        patch("eval_retriever.app.RetrieverClient", return_value=fake_client),
        patch("eval_retriever.app.mlflow") as mock_mlflow,
    ):
        mock_mlflow.start_run.return_value.__enter__ = lambda self: self  # noqa: ARG005
        mock_mlflow.start_run.return_value.__exit__ = lambda self, *a: None  # noqa: ARG005
        App().run()

    params = mock_mlflow.log_params.call_args.args[0]
    assert params["n_failures"] == 3

    metrics = mock_mlflow.log_metrics.call_args.args[0]
    assert metrics["recall@1"] == 0.0
    assert metrics["mrr"] == 0.0

    out = capsys.readouterr().out
    assert "retriever error" in out
    assert "retriever failures: 3" in out


def test_run_aborts_on_empty_eval_set(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    An eval CSV with only the header prints and exits without touching MLFlow.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory.
    capsys : pytest.CaptureFixture[str]
        Captures stdout.
    """
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text(CSV_HEADER, encoding="utf-8")

    mock = MagicMock()
    mock.eval_csv_path = str(empty_csv)
    mock.results_dir = str(tmp_path / "results")
    mock.approach_tag = "baseline"
    mock.retriever_url = "http://test"
    mock.top_k = 5
    mock.similarity_threshold = 0.0
    mock.mlflow_tracking_uri = "http://mlflow"
    mock.experiment_name = "exp"
    mock.request_timeout_s = 10.0

    with (
        patch("eval_retriever.app.task_inputs", mock),
        patch("eval_retriever.app.RetrieverClient") as client_cls,
        patch("eval_retriever.app.mlflow") as mock_mlflow,
    ):
        App().run()

    # No HTTP client was ever constructed, and MLFlow was not touched.
    client_cls.assert_not_called()
    mock_mlflow.start_run.assert_not_called()

    out = capsys.readouterr().out
    assert "No samples to evaluate" in out


def test_eval_sample_shape() -> None:
    """Regression: EvalSample exposes the expected fields as attributes."""
    sample = EvalSample(
        id="42",
        query="qq",
        expected_document="d.md",
        expected_chunk_id="1",
        reference_passage="ref",
    )
    assert sample.id == "42"
    assert sample.expected_chunk_id == "1"
