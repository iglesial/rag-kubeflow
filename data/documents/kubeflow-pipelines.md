# Fluffy Cake Pipeline Engine

Fluffy Cake's pipeline engine is built on Kubeflow Pipelines and allows users to define ML workflows as directed acyclic graphs. Each step runs in an isolated container, ensuring reproducibility across environments.

Users define pipelines using either the visual editor in the dashboard or the Python SDK. The SDK provides decorators like @fc.step to wrap functions into pipeline components. Compiled pipelines can be scheduled, triggered by events, or run manually.

The engine supports step caching, automatic retries, and conditional branching. Logs, metrics, and artifacts from each run are stored and visible in the Fluffy Cake UI. Failed steps can be restarted without re-running the entire pipeline.
