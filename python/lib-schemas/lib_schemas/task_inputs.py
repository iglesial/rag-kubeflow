"""Task inputs module for lib-schemas."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """Task inputs for lib-schemas diagnostics."""

    model_config = SettingsConfigDict(cli_parse_args=True)


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
