"""Application module for package-1."""

from package_1.task_inputs import task_inputs


class App:
    """Main application class for package-1."""

    def run(self) -> None:
        """
        Run the application.

        Execute main application logic and print job run ID.
        """
        print(f"Running package-1 with job_run_id: {task_inputs.job_run_id}")
