"""Retrieval quality metrics: recall@k and MRR — STUDENT STUB."""

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

        TODO (student exercise): return ``1 / rank`` of the first
        occurrence of ``self.expected_document`` in
        ``self.retrieved_documents``. If the expected document isn't
        present, return ``0.0``.

        Returns
        -------
        float
            ``1 / rank`` of the first correct hit, or ``0.0``.

        Raises
        ------
        NotImplementedError
            Until the student implements this method.

        Examples
        --------
        - retrieved=("a.md", "b.md", "c.md"), expected="a.md" → 1.0
        - retrieved=("a.md", "b.md", "c.md"), expected="b.md" → 0.5
        - retrieved=("a.md", "b.md", "c.md"), expected="z.md" → 0.0
        - retrieved=(),                       expected="a.md" → 0.0
        """
        raise NotImplementedError(
            "TODO: implement reciprocal rank — see docstring above for the rule."
        )

    def hit_at(self, k: int) -> bool:
        """
        Return whether the expected document is within the top ``k`` retrieved.

        Already implemented for you — use this as a helper in ``aggregate``.

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

        Already implemented for you.

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
        Aggregate per-query results into recall_at_k and MRR metrics.

        TODO (student exercise): return a dict with keys ``recall_at_1``,
        ``recall_at_3``, ``recall_at_5`` (or whatever values are in
        ``ks``), and ``mrr``.

        Input validation (already handled for you — do NOT remove):
        empty ``ks`` raises ``ValueError``; any ``k < 1`` raises ``ValueError``.

        Parameters
        ----------
        queries : Sequence[Query]
            Scored queries to aggregate over.
        ks : Sequence[int]
            Cutoff ranks for ``recall_at_k``. Defaults to ``(1, 3, 5)``.

        Returns
        -------
        dict[str, float]
            Mapping of metric name to value.

        Raises
        ------
        ValueError
            If ``ks`` is empty or contains a non-positive value.
        NotImplementedError
            Until the student implements the happy path below.

        Notes
        -----
        - **recall_at_k**: for each k in ``ks``, the fraction of queries
          whose expected_document is within the top k retrieved.
          Use ``query.hit_at(k)``.
        - **mrr**: mean of ``query.score`` across all queries.
          Use the ``score`` computed field you implemented.
        - **Metric names use underscores**, not "@". Use
          ``f"recall_at_{k}"``. MLFlow rejects "@" in metric names.
        """
        # --- Input validation (already done — don't touch) ---
        if not ks:
            msg = "ks must be non-empty"
            raise ValueError(msg)
        if any(k < 1 for k in ks):
            msg = f"all k values must be >= 1, got {list(ks)}"
            raise ValueError(msg)

        # --- Empty queries short-circuit (already done — don't touch) ---
        if not queries:
            zeros: dict[str, float] = {f"recall_at_{k}": 0.0 for k in ks}
            zeros["mrr"] = 0.0
            return zeros

        # --- TODO (student exercise): compute recall_at_k and mrr ---
        #
        # Build and return a dict like:
        #   {
        #       "recall_at_1": <fraction of queries with hit_at(1) True>,
        #       "recall_at_3": <fraction of queries with hit_at(3) True>,
        #       "recall_at_5": <fraction of queries with hit_at(5) True>,
        #       "mrr":         <average of query.score across queries>,
        #   }
        #
        # Use query.hit_at(k) and query.score.
        raise NotImplementedError(
            "TODO: compute recall_at_k and mrr — see docstring above for the rules."
        )
