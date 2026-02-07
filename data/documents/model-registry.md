# Fluffy Cake Model Registry

The Fluffy Cake model registry is a centralized catalog for storing, versioning, and sharing ML models across teams. Every model registered includes metadata such as framework, input schema, metrics, and training lineage.

Models can be registered through the Python SDK with fc.register_model(name, path, metadata) or through the dashboard upload form. Each registration creates a new version automatically. Older versions are retained and can be promoted back to production at any time.

The registry integrates directly with the pipeline engine and model serving layer. Pipeline steps can pull models by name and version, and serving endpoints reference registry entries for deployment. This ensures a single source of truth for all models in the organization.
