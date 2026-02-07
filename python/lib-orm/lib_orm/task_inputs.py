"""Task inputs module for lib-orm."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """Task inputs for lib-orm diagnostics."""

    model_config = SettingsConfigDict(cli_parse_args=True)

    db_url: str = Field(
        default="postgresql+asyncpg://rag:rag@localhost:5432/rag",
        description="Database connection URL",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
