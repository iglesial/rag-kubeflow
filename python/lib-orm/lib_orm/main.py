# Projen managed file. Do not edit directly.
"""Main module for lib-orm."""

from lib_orm.app import App


def main() -> None:
    """Execute main function."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
