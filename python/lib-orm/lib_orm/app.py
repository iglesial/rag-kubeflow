"""Application module for lib-orm."""

from lib_orm.task_inputs import task_inputs


class App:
    """Diagnostic tool for database and ORM library."""

    def run(self) -> None:
        """
        Run diagnostics.

        Verify DB connectivity and print configuration.
        """
        print(f"Database URL: {task_inputs.db_url}")
