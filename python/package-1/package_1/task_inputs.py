"""Task inputs module for package-1."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """Task inputs class for package-1."""

    model_config = SettingsConfigDict(cli_parse_args=True)

    job_run_id: int = Field(description="Databricks job run ID")


# Global task inputs instance
task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
