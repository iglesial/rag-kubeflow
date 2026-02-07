# Fluffy Cake Model Serving

Fluffy Cake provides managed model serving powered by KServe. Users deploy models with a single API call or button click, and Fluffy Cake handles containerization, routing, and autoscaling.

Supported frameworks include HuggingFace Transformers, PyTorch, TensorFlow, and ONNX. Models are loaded from the Fluffy Cake model registry, which tracks versions, metadata, and lineage. Canary deployments allow gradual traffic shifting between model versions.

Each inference endpoint gets a stable URL with built-in load balancing. Fluffy Cake monitors latency, throughput, and error rates. Alerts fire when performance degrades below configurable thresholds.
