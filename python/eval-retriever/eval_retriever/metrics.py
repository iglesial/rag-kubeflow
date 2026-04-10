"""Retrieval quality metrics: recall@k and MRR."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, computed_field

if TYPE_CHECKING:
    from eval_retriever.eval_loader import EvalSample

DEFAULT_KS: tuple[int, ...] = (1, 3, 5)


class Query(BaseModel):
    """
    A scored query: ground truth plus the ranked list of retrieved documents.

    Attributes
    ----------
    query_id : str
        Identifier of the query in the eval set.
    query : str
        The raw query text as it was sent to the retriever.
    expected_document : str
        Document filename the query was expected to retrieve.
    retrieved_documents : tuple[str, ...]
        Ranked document filenames returned by the retriever,
        highest-scoring first.
    """

    model_config = ConfigDict(frozen=True)

    query_id: str
    query: str
    expected_document: str
    retrieved_documents: tuple[str, ...]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def score(self) -> float:
        """
        Reciprocal rank of the expected document in the retrieved list.

        Returns ``0.0`` if the expected document is not present. This is
        the per-query contribution to MRR, and ``score > 0`` means the
        query is a hit at rank ``1 / score``.

        Returns
        -------
        float
            ``1 / rank`` of the first correct hit, or ``0.0``.
        """
        for rank, doc in enumerate(self.retrieved_documents, start=1):
            if doc == self.expected_document:
                return 1.0 / rank
        return 0.0

    def hit_at(self, k: int) -> bool:
        """
        Return whether the expected document is within the top ``k`` retrieved.

        Parameters
        ----------
        k : int
            Cutoff rank (must be ``>= 1``).

        Returns
        -------
        bool
            ``True`` if ``expected_document`` appears in the first ``k``
            entries of ``retrieved_documents``.

        Raises
        ------
        ValueError
            If ``k < 1``.
        """
        if k < 1:
            msg = f"k must be >= 1, got {k}"
            raise ValueError(msg)
        return self.expected_document in self.retrieved_documents[:k]

    @classmethod
    def from_sample(
        cls,
        sample: "EvalSample",
        retrieved_documents: Sequence[str],
    ) -> "Query":
        """
        Build a scored Query from an eval sample and the retriever's response.

        Parameters
        ----------
        sample : EvalSample
            The ground-truth eval sample this Query scores.
        retrieved_documents : Sequence[str]
            Ranked document names returned by the retriever,
            highest-scoring first.

        Returns
        -------
        Query
            A frozen scored Query carrying the eval metadata and the
            retrieved documents as a tuple.
        """
        return cls(
            query_id=sample.id,
            query=sample.query,
            expected_document=sample.expected_document,
            retrieved_documents=tuple(retrieved_documents),
        )

    @staticmethod
    def aggregate(
        queries: Sequence["Query"],
        ks: Sequence[int] = DEFAULT_KS,
    ) -> dict[str, float]:
        """
        Aggregate per-query results into recall@k and MRR metrics.

        Parameters
        ----------
        queries : Sequence[Query]
            Scored queries to aggregate over.
        ks : Sequence[int]
            Cutoff ranks for ``recall@k``. Defaults to ``(1, 3, 5)``.

        Returns
        -------
        dict[str, float]
            Mapping with keys ``recall@<k>`` for each ``k`` in ``ks`` and
            ``mrr``. Returns all zeros when ``queries`` is empty.

        Raises
        ------
        ValueError
            If ``ks`` is empty or contains a non-positive value.
        """
        if not ks:
            msg = "ks must be non-empty"
            raise ValueError(msg)
        if any(k < 1 for k in ks):
            msg = f"all k values must be >= 1, got {list(ks)}"
            raise ValueError(msg)

        if not queries:
            zeros: dict[str, float] = {f"recall@{k}": 0.0 for k in ks}
            zeros["mrr"] = 0.0
            return zeros

        n = len(queries)
        metrics: dict[str, float] = {
            f"recall@{k}": sum(1.0 for q in queries if q.hit_at(k)) / n for k in ks
        }
        metrics["mrr"] = sum(q.score for q in queries) / n
        return metrics
