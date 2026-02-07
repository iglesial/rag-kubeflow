"""Application module for lib-schemas."""

from lib_schemas.schemas import (
    ChunkInput,
    ChunkWithEmbedding,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StatsResponse,
)


class App:
    """Diagnostic tool for lib-schemas library."""

    def run(self) -> None:
        """
        Run diagnostics.

        Print all available schema names.
        """
        schemas = [
            ChunkInput,
            ChunkWithEmbedding,
            SearchRequest,
            SearchResult,
            SearchResponse,
            StatsResponse,
        ]
        print("Available schemas:")
        for schema in schemas:
            print(f"  - {schema.__name__}")
