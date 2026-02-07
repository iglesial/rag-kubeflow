"""Health and readiness probe endpoints."""

from typing import Any

from fastapi import APIRouter, Response

from rag_retriever.dependencies import check_db_health, check_model_health

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """
    Return basic health status.

    Returns
    -------
    dict[str, str]
        Always returns ``{"status": "ok"}``.
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response) -> dict[str, Any]:
    """
    Check readiness of all dependencies.

    Parameters
    ----------
    response : Response
        FastAPI response object for setting status code.

    Returns
    -------
    dict[str, Any]
        Readiness status including database and model health.
    """
    db_ok = await check_db_health()
    model_ok = check_model_health()
    is_ready = db_ok and model_ok

    if not is_ready:
        response.status_code = 503

    return {
        "status": "ready" if is_ready else "not_ready",
        "db": db_ok,
        "model": model_ok,
    }
