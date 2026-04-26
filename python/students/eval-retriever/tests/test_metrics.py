"""Tests for eval-retriever metrics."""

import pytest

from eval_retriever.eval_loader import EvalSample
from eval_retriever.metrics import DEFAULT_KS, Query


def test_score_hit_at_rank_1() -> None:
    """A perfect hit at rank 1 gives score 1.0 and hit@k=True for all k."""
    q = Query(
        query_id="q1",
        query="Qui est Pikachu ?",
        expected_document="025-pikachu.md",
        retrieved_documents=("025-pikachu.md", "001-bulbizarre.md", "004-salameche.md"),
    )
    assert q.score == 1.0
    assert q.hit_at(1) is True
    assert q.hit_at(3) is True
    assert q.hit_at(5) is True


def test_score_hit_at_rank_2() -> None:
    """A hit at rank 2 gives score 0.5 and hit@1=False, hit@3=True."""
    q = Query(
        query_id="q1",
        query="Qui est Pikachu ?",
        expected_document="025-pikachu.md",
        retrieved_documents=("001-bulbizarre.md", "025-pikachu.md", "004-salameche.md"),
    )
    assert q.score == 0.5
    assert q.hit_at(1) is False
    assert q.hit_at(3) is True


def test_score_miss() -> None:
    """A query with no match has score 0.0 and hit@k=False for all k."""
    q = Query(
        query_id="q1",
        query="Qui est Pikachu ?",
        expected_document="025-pikachu.md",
        retrieved_documents=("001-bulbizarre.md", "004-salameche.md"),
    )
    assert q.score == 0.0
    assert q.hit_at(1) is False
    assert q.hit_at(5) is False


def test_score_empty_retrieved() -> None:
    """An empty retrieved list scores 0 and misses everything."""
    q = Query(
        query_id="q1",
        query="Qui est Pikachu ?",
        expected_document="025-pikachu.md",
        retrieved_documents=(),
    )
    assert q.score == 0.0
    assert q.hit_at(1) is False


def test_hit_at_invalid_k_raises() -> None:
    """The ``hit_at`` method rejects ``k < 1``."""
    q = Query(
        query_id="q1",
        query="q",
        expected_document="a.md",
        retrieved_documents=("a.md",),
    )
    with pytest.raises(ValueError, match="k must be >= 1"):
        q.hit_at(0)


def test_aggregate_mixed_queries() -> None:
    """Aggregate computes recall@k and MRR over a mix of hits and misses."""
    queries = [
        # Hit at rank 1 -> score 1.0, hit@1/3/5 = True
        Query(
            query_id="q1",
            query="find a",
            expected_document="a.md",
            retrieved_documents=("a.md", "b.md", "c.md"),
        ),
        # Hit at rank 3 -> score 1/3, hit@1 = False, hit@3/5 = True
        Query(
            query_id="q2",
            query="find d",
            expected_document="d.md",
            retrieved_documents=("b.md", "c.md", "d.md", "e.md", "f.md"),
        ),
        # Miss -> score 0, hit@1/3/5 = False
        Query(
            query_id="q3",
            query="find g",
            expected_document="g.md",
            retrieved_documents=("b.md", "c.md"),
        ),
    ]
    metrics = Query.aggregate(queries, ks=DEFAULT_KS)
    assert metrics["recall_at_1"] == pytest.approx(1 / 3)
    assert metrics["recall_at_3"] == pytest.approx(2 / 3)
    assert metrics["recall_at_5"] == pytest.approx(2 / 3)
    assert metrics["mrr"] == pytest.approx((1.0 + 1 / 3 + 0.0) / 3)


def test_aggregate_empty_queries() -> None:
    """Aggregate returns zero metrics for an empty query list."""
    metrics = Query.aggregate([], ks=DEFAULT_KS)
    assert metrics == {
        "recall_at_1": 0.0,
        "recall_at_3": 0.0,
        "recall_at_5": 0.0,
        "mrr": 0.0,
    }


def test_aggregate_empty_ks_raises() -> None:
    """Aggregate rejects an empty ks list."""
    with pytest.raises(ValueError, match="ks must be non-empty"):
        Query.aggregate([], ks=[])


def test_aggregate_bad_k_raises() -> None:
    """Aggregate rejects non-positive k values."""
    with pytest.raises(ValueError, match="all k values must be >= 1"):
        Query.aggregate([], ks=[0, 1])


def test_query_is_frozen() -> None:
    """Query instances are immutable (frozen model)."""
    q = Query(
        query_id="q1",
        query="q",
        expected_document="a.md",
        retrieved_documents=("a.md",),
    )
    with pytest.raises(ValueError, match="frozen"):
        q.query_id = "q2"  # type: ignore[misc]


def test_from_sample_builds_scored_query() -> None:
    """``Query.from_sample`` copies sample fields and coerces retrieved to a tuple."""
    sample = EvalSample(
        id="42",
        query="Quel est le pouvoir de Pikachu ?",
        expected_document="025-pikachu.md",
        expected_chunk_id="0",
        reference_passage="Pikachu dispose de petites poches...",
    )

    q = Query.from_sample(sample, ["001-bulbizarre.md", "025-pikachu.md"])

    assert q.query_id == "42"
    assert q.query == "Quel est le pouvoir de Pikachu ?"
    assert q.expected_document == "025-pikachu.md"
    assert q.retrieved_documents == ("001-bulbizarre.md", "025-pikachu.md")
    assert isinstance(q.retrieved_documents, tuple)
    # Scoring still works — expected doc is at rank 2.
    assert q.score == 0.5
    assert q.hit_at(1) is False
    assert q.hit_at(3) is True
