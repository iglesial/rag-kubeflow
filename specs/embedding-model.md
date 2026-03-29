# Embedding Model

## `sentence-transformers/all-MiniLM-L6-v2`

| Property | Value |
|----------|-------|
| Dimensions | 384 |
| Model size | ~80 MB |
| Speed | ~14,000 sentences/sec on CPU |
| License | Apache 2.0 |
| API key required | No |
| GPU required | No |

Chosen because it runs fast on CPU, requires no API key, downloads automatically on first use (~80 MB to `~/.cache/huggingface/`), and produces good quality embeddings for its size.

Configurable via `task_inputs.embedding_model` for alternatives like `paraphrase-MiniLM-L3-v2` (128-dim, smaller) on constrained hardware.

## Model Serving via KServe

The embedding model is served as a standalone KServe InferenceService using the built-in HuggingFace runtime (no custom model server needed):

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: embedding-model
  namespace: kubeflow
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      args:
        - --model_name=all-MiniLM-L6-v2
        - --task=text_embedding
        - --backend=huggingface
      storageUri: "hf://sentence-transformers/all-MiniLM-L6-v2"
```

KServe Standard mode (no Knative) exposes an **OpenAI-compatible** endpoint at `/openai/v1/embeddings`:

```json
// Request
{"model": "all-MiniLM-L6-v2", "input": ["query text"]}

// Response
{"data": [{"embedding": [0.1, ...], "index": 0}], "model": "all-MiniLM-L6-v2"}
```

The retriever falls back to local in-process embedding when KServe is not configured (backward compatibility).

## Model Registry

Kubeflow Model Registry (v0.3.5) provides a central catalog for model versions. The pipeline registers the model on submit:

```python
from model_registry import ModelRegistry

registry = ModelRegistry(server_address="model-registry-service.kubeflow:8080", author="pipeline")
registry.register_model(
    "all-MiniLM-L6-v2",
    uri="hf://sentence-transformers/all-MiniLM-L6-v2",
    model_format_name="sentence-transformers",
    model_format_version="3",
    version="v1",
)
```
