# Projen managed file. Do not edit directly.
"""Main module for rag-shared."""

from rag_shared.app import App


def main() -> None:
    """Execute main function."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
