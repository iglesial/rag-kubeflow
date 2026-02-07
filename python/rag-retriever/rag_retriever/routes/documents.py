"""Document stats endpoint."""

from fastapi import APIRouter, Depends
from lib_orm.models import DocumentChunk
from lib_schemas.schemas import StatsResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag_retriever.dependencies import get_db_session
from rag_retriever.task_inputs import task_inputs

router = APIRouter(prefix="/documents")


@router.get("/stats")
async def stats(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> StatsResponse:
    """
    Return document and chunk statistics.

    Parameters
    ----------
    session : AsyncSession
        Injected database session.

    Returns
    -------
    StatsResponse
        Counts of documents and chunks, plus model metadata.
    """
    result = await session.execute(
        select(
            func.count(func.distinct(DocumentChunk.document_name)),
            func.count(),
        )
    )
    row = result.one()
    total_documents: int = row[0]
    total_chunks: int = row[1]

    return StatsResponse(
        total_documents=total_documents,
        total_chunks=total_chunks,
        embedding_dimension=384,
        model_name=task_inputs.embedding_model,
    )
