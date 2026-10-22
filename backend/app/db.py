from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# Search SQL is re-executed with very different LIKE patterns; a cached generic plan picked for one
# pattern can turn a 2-character prefix into a full trigram-index scan, so always plan per query.
# Search takes the first RANK_WINDOW hits of a scan: synchronized seq scans would start each scan at
# a random block, making results non-deterministic and sometimes scanning most of a large table.
engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"options": "-c plan_cache_mode=force_custom_plan -c synchronize_seqscans=off"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
