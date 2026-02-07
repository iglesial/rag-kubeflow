# CLAUDE.md

## Project

RAG retrieval system built with FastAPI, PostgreSQL+pgvector, and Kubeflow Pipelines. Designed to teach MLOps to data engineering students. Everything runs locally — no cloud services or paid APIs.

## Architecture

5 Python packages under `python/`, plus an example template (`package-1`):

| Package | Purpose |
|---------|---------|
| `rag-shared` | Shared library: async DB (SQLAlchemy+asyncpg), ORM models, Pydantic schemas, embedding client |
| `rag-loader` | Read documents from disk, chunk them, output JSON |
| `rag-embedder` | Read chunks, generate embeddings, insert into pgvector |
| `rag-retriever` | FastAPI service: embed queries, search pgvector, return ranked results |
| `rag-pipeline` | Kubeflow Pipeline definition orchestrating loader -> embedder |

Embedding model: `all-MiniLM-L6-v2` (384 dims, sentence-transformers, runs on CPU).
Database: PostgreSQL 16 with pgvector extension, table `document_chunks`.
Orchestration: Kind cluster with Kubeflow Pipelines standalone.

## Package Conventions

Every package MUST follow the `python/package-1/` pattern exactly:

```
python/<pkg-name>/
├── <pkg_name>/
│   ├── __init__.py          # version + public re-exports
│   ├── app.py               # App class with run() method — all business logic here
│   ├── main.py              # Projen-managed entry point — DO NOT EDIT
│   └── task_inputs.py       # Pydantic BaseSettings with SettingsConfigDict(cli_parse_args=True)
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml
├── justfile
├── README.md
└── uv.lock                  # committed
```

### main.py (projen-managed, do not edit)

```python
# Projen managed file. Do not edit directly.
from <pkg_name>.app import App

def main() -> None:
    app = App()
    app.run()

if __name__ == "__main__":
    main()
```

### task_inputs.py pattern

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class TaskInputs(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)
    # fields here with Field(description=...) and defaults

task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
```

### Entry point in pyproject.toml

```toml
[project.scripts]
main = "<pkg_name>.main:main"
```

## Code Quality

- **Ruff**: line-length=100, target-version="py313", rules: E, W, F, I, B, C4, UP, D
- **Pydocstyle**: numpy convention — every module, class, and public function needs a docstring
- **Mypy**: strict=true, ignore_missing_imports=true, disallow_subclassing_any=false
- **Pytest**: testpaths=["tests"], --strict-markers, --strict-config, --cov=<pkg_name>
- **Pre-commit**: ruff lint+format, mypy, trailing-whitespace, end-of-file-fixer, check-yaml, check-toml

## Tooling

- **Package manager**: uv (lock files committed)
- **Task runner**: justfile per package (Windows: `set shell := ["cmd", "/c"]`)
- **Python**: >=3.13
- **DB driver**: asyncpg (async SQLAlchemy)

## Common Commands

```bash
# Per-package (from python/<pkg-name>/)
just install-dev          # install all deps
just check-all            # ruff check + format check + mypy
just test                 # pytest
just run                  # run the app entry point

# Root level
just infra-up             # docker compose up -d (postgres)
just infra-down           # docker compose down
just test-all             # run tests across all packages
just check-all            # lint + typecheck all packages
```

## Key Files

- `.claude/plans/synchronous-tinkering-alpaca.md` — full PRD with 26 GitHub issues
- `docker-compose.yml` — PostgreSQL+pgvector on port 5432 (user: rag, pass: rag, db: rag)
- `infra/init.sql` — DB schema (document_chunks table, vector(384), IVFFlat index)
- `.pre-commit-config.yaml` — ruff + mypy + pre-commit-hooks

## GitHub Issues

26 issues (RAG-001 to RAG-026) across 7 epics. Use `gh issue list` to see current state.
