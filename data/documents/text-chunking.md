# Fluffy Cake Chunking Strategies

Fluffy Cake offers three built-in chunking strategies for document processing. The choice of strategy affects retrieval quality and is configurable per collection.

Fixed-size chunking splits text into segments of a set character count with overlap. It is fast and predictable but may cut sentences mid-thought. Recursive chunking tries paragraph boundaries first, then sentences, then words, preserving natural text structure. Semantic chunking uses an embedding model to detect topic shifts and places boundaries where the meaning changes.

The default configuration uses recursive chunking with 512-character chunks and 64-character overlap. Users can adjust these parameters through the API or the collection settings page in the dashboard.
