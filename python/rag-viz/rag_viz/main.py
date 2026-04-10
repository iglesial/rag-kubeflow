"""Main module for rag-viz."""

# Projen managed file. Do not edit directly.

from rag_viz.app import App


def main() -> None:
    """Execute main function."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
