"""Application module for rag-pipeline."""

from rag_pipeline.task_inputs import task_inputs


class App:
    """Kubeflow Pipeline orchestration application."""

    def run(self) -> None:
        """
        Run the pipeline compiler or submitter.

        Compiles the pipeline to YAML if ``compile_only`` is True,
        otherwise submits it to the Kubeflow Pipelines API.
        """
        print(f"Pipeline name:  {task_inputs.pipeline_name}")
        print(f"Input directory: {task_inputs.input_dir}")
        print(f"Kubeflow host:  {task_inputs.kubeflow_host}")
        print(f"Compile only:   {task_inputs.compile_only}")
        print("rag-pipeline: pipeline not yet implemented")
