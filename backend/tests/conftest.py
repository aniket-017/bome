import pytest


def _db_available() -> bool:
    try:
        import psycopg

        from app.config import get_settings

        with psycopg.connect(get_settings().psycopg_dsn, connect_timeout=5) as conn:
            return conn.execute("SELECT to_regclass('stock_txns') IS NOT NULL").fetchone()[0]
    except Exception:  # pragma: no cover - environment without DB
        return False


HAS_ERP_DB = _db_available()
requires_erp_db = pytest.mark.skipif(not HAS_ERP_DB, reason="database migrated to 0004_erp_phase1 required")


@pytest.fixture
def tx_client():
    """TestClient whose requests share one database transaction that is rolled back afterwards.

    Endpoints that match BOM lines open their own sessions and cannot see this transaction's rows,
    so tests using this client create BOM lines with matched_part_id set and auto_match off."""
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session

    from app.db import engine, get_db
    from app.main import app

    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint", autoflush=False, expire_on_commit=False)

    def override():
        try:
            yield session
        finally:
            session.rollback()

    app.dependency_overrides[get_db] = override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        trans.rollback()
        conn.close()
