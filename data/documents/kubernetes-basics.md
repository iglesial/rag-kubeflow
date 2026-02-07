# Fluffy Cake Infrastructure

Fluffy Cake runs on Kubernetes and abstracts away all cluster management. Each customer workspace maps to a Kubernetes namespace with resource quotas and network policies enforced automatically.

Under the hood, Fluffy Cake uses Kind clusters for development environments and managed Kubernetes (EKS, GKE, AKS) for production. The platform handles node scaling, pod scheduling, and health monitoring. Users never interact with kubectl or YAML manifests directly.

For on-premise deployments, Fluffy Cake provides a Helm chart that installs the entire platform into an existing Kubernetes cluster. Air-gapped installations are supported with a bundled container registry.
