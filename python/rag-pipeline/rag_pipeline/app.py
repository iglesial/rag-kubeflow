"""Application module for rag-pipeline."""

from kfp import compiler

from rag_pipeline.pipeline import rag_ingestion_pipeline
from rag_pipeline.task_inputs import task_inputs

PIPELINE_YAML = "rag-ingestion-pipeline.yaml"


class App:
    """Kubeflow Pipeline orchestration application."""

    def run(self) -> None:
        """
        Run the pipeline compiler or submitter.

        Compiles the pipeline to YAML if ``compile_only`` is True,
        otherwise submits it to the Kubeflow Pipelines API.
        """
        print(f"Pipeline name:   {task_inputs.pipeline_name}")
        print(f"Input directory:  {task_inputs.input_dir}")
        print(f"Kubeflow host:   {task_inputs.kubeflow_host}")
        print(f"Compile only:    {task_inputs.compile_only}")
        print(f"Chunk size:      {task_inputs.chunk_size}")
        print(f"Chunk overlap:   {task_inputs.chunk_overlap}")
        print(f"DB URL:          {task_inputs.db_url}")
        print(f"Embedding model: {task_inputs.embedding_model}")
        print(f"Batch size:      {task_inputs.batch_size}")

        # Compile pipeline to YAML
        compiler.Compiler().compile(
            pipeline_func=rag_ingestion_pipeline,
            package_path=PIPELINE_YAML,
        )
        print(f"Compiled pipeline to {PIPELINE_YAML}")

        if task_inputs.compile_only:
            return

        # Submit to Kubeflow Pipelines
        try:
            from kfp.client import Client

            client = Client(host=task_inputs.kubeflow_host)
            pipeline = client.upload_pipeline(
                pipeline_package_path=PIPELINE_YAML,
                pipeline_name=task_inputs.pipeline_name,
            )
            print(f"Registered pipeline: {pipeline.pipeline_id}")
            run = client.create_run_from_pipeline_package(
                PIPELINE_YAML,
                arguments={
                    "input_dir": task_inputs.input_dir,
                    "chunk_size": task_inputs.chunk_size,
                    "chunk_overlap": task_inputs.chunk_overlap,
                    "db_url": task_inputs.db_url,
                    "embedding_model": task_inputs.embedding_model,
                    "batch_size": task_inputs.batch_size,
                },
                run_name=task_inputs.pipeline_name,
            )
            print(f"Submitted pipeline run: {run.run_id}")
        except Exception as exc:  # noqa: BLE001
            print(f"Pipeline submission failed: {exc}")
            print("Use --compile_only to generate YAML without submitting")
