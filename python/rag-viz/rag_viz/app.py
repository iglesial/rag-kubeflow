"""Application module for rag-viz."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from lib_schemas.schemas import ChunkWithEmbedding, SearchResponse
from umap import UMAP

from rag_viz.task_inputs import task_inputs


class App:
    """UMAP embedding visualization application."""

    def run(self) -> None:
        """
        Run the UMAP visualization pipeline.

        Load embeddings from JSON, reduce to 2D with UMAP,
        and generate an interactive HTML scatter plot. Optionally overlay
        a query point and highlight retrieved chunks from a SearchResponse.
        """
        print(f"Input file:  {task_inputs.input_file}")
        print(f"Output file: {task_inputs.output_file}")

        # Load embeddings
        input_path = Path(task_inputs.input_file)
        data = json.loads(input_path.read_text(encoding="utf-8"))
        chunks = [ChunkWithEmbedding(**item) for item in data]
        print(f"Loaded {len(chunks)} chunks")

        # Build embedding matrix
        embedding_matrix = np.array([c.embedding for c in chunks])
        print(f"Embedding matrix shape: {embedding_matrix.shape}")

        # UMAP reduction
        reducer = UMAP(
            n_neighbors=task_inputs.n_neighbors,
            min_dist=task_inputs.min_dist,
            metric=task_inputs.metric,
            n_components=2,
            random_state=task_inputs.random_state,
        )
        coords = reducer.fit_transform(embedding_matrix)
        print("UMAP reduction complete")

        # Build dataframe for plotly
        max_len = task_inputs.content_truncate_length
        df = pd.DataFrame(
            {
                "UMAP-1": coords[:, 0],
                "UMAP-2": coords[:, 1],
                "document_name": [c.document_name for c in chunks],
                "chunk_index": [c.chunk_index for c in chunks],
                "content_preview": [
                    c.content[:max_len].replace("\n", " ")
                    + ("..." if len(c.content) > max_len else "")
                    for c in chunks
                ],
            }
        )

        # Create interactive scatter plot
        fig = px.scatter(
            df,
            x="UMAP-1",
            y="UMAP-2",
            color="document_name",
            hover_data=["document_name", "chunk_index", "content_preview"],
            title=task_inputs.plot_title,
        )
        fig.update_traces(marker={"size": task_inputs.point_size})
        fig.update_layout(legend_title_text="Document")

        # Overlay query and retrieved chunks if query_file is provided
        if task_inputs.query_file:
            self._overlay_query(fig, reducer, chunks, coords, df)

        # Write HTML
        output_path = Path(task_inputs.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path), full_html=True, include_plotlyjs=True)
        print(f"Visualization saved to {output_path}")

    def _overlay_query(
        self,
        fig: go.Figure,
        reducer: UMAP,
        chunks: list[ChunkWithEmbedding],
        coords: np.ndarray,
        df: pd.DataFrame,
    ) -> None:
        """
        Overlay query point and highlight retrieved chunks on the figure.

        Parameters
        ----------
        fig : go.Figure
            The plotly figure to add traces to.
        reducer : UMAP
            Fitted UMAP reducer for transforming the query embedding.
        chunks : list[ChunkWithEmbedding]
            All corpus chunks.
        coords : np.ndarray
            UMAP 2D coordinates for all chunks.
        df : pd.DataFrame
            DataFrame with chunk metadata.
        """
        query_path = Path(task_inputs.query_file)
        query_data = json.loads(query_path.read_text(encoding="utf-8"))
        search_response = SearchResponse(**query_data)
        print(f"Query: {search_response.query!r} ({search_response.total_results} results)")

        # Build index of (document_name, chunk_index) -> position for retrieved chunks
        retrieved_keys = {(r.document_name, r.content) for r in search_response.results}
        retrieved_indices = [
            i for i, c in enumerate(chunks) if (c.document_name, c.content) in retrieved_keys
        ]

        # Highlight retrieved chunks with rings
        if retrieved_indices:
            ret_df = df.iloc[retrieved_indices]
            fig.add_trace(
                go.Scatter(
                    x=ret_df["UMAP-1"],
                    y=ret_df["UMAP-2"],
                    mode="markers",
                    name="Retrieved chunks",
                    marker={
                        "size": task_inputs.point_size + 8,
                        "color": "rgba(0,0,0,0)",
                        "line": {"color": "red", "width": 2},
                    },
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Chunk: %{customdata[1]}<br>"
                        "%{customdata[2]}"
                        "<extra>Retrieved</extra>"
                    ),
                    customdata=list(
                        zip(
                            ret_df["document_name"],
                            ret_df["chunk_index"],
                            ret_df["content_preview"],
                            strict=True,
                        )
                    ),
                )
            )
            print(f"Highlighted {len(retrieved_indices)} retrieved chunks")

        # Plot query point
        if search_response.query_embedding:
            query_vec = np.array([search_response.query_embedding])
            query_coords = reducer.transform(query_vec)
            max_len = task_inputs.content_truncate_length
            query_preview = search_response.query[:max_len]

            fig.add_trace(
                go.Scatter(
                    x=[query_coords[0, 0]],
                    y=[query_coords[0, 1]],
                    mode="markers",
                    name="Query",
                    marker={
                        "size": 14,
                        "color": "black",
                        "symbol": "star",
                        "line": {"color": "white", "width": 1},
                    },
                    hovertemplate=(f"<b>Query</b><br>{query_preview}<extra></extra>"),
                )
            )
            print("Query point plotted")
