from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from .config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    if connection_record.info.get("pool_disconnect"):
        import redis
        connection_record.info["pool_disconnect"] = False
        raise redis.exceptions.ConnectionError("Connection was invalidated")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
