from __future__ import annotations
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine() -> Engine | None:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return None
    # Allow standard postgres URLs from common hosting providers.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800)


def initialize_database(engine: Engine) -> None:
    statements = [
        "CREATE TABLE IF NOT EXISTS bda_projects (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE TABLE IF NOT EXISTS bda_datasets (id BIGSERIAL PRIMARY KEY, project_id BIGINT REFERENCES bda_projects(id) ON DELETE CASCADE, file_name TEXT NOT NULL, row_count BIGINT NOT NULL DEFAULT 0, column_count INTEGER NOT NULL DEFAULT 0, file_size_bytes BIGINT NOT NULL DEFAULT 0, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE TABLE IF NOT EXISTS bda_processing_jobs (id BIGSERIAL PRIMARY KEY, dataset_id BIGINT REFERENCES bda_datasets(id) ON DELETE SET NULL, action TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'completed', details JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
