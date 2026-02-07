# Fluffy Cake RAG Builder

Fluffy Cake RAG Builder is a turnkey module for creating retrieval-augmented generation applications. It connects the vector store, embedding service, and an LLM endpoint into a single searchable knowledge base.

Users upload documents through the dashboard or API. Fluffy Cake automatically chunks the text, generates embeddings, and indexes them in the vector store. At query time, relevant chunks are retrieved and injected into the LLM prompt as context.

RAG Builder supports configurable chunking strategies (fixed-size, recursive, or semantic), adjustable retrieval parameters (top-k, similarity threshold), and prompt templates. It includes built-in evaluation metrics like answer relevance and faithfulness.
