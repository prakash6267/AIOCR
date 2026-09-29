import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("ai_osm.db")
logging.basicConfig(level=logging.INFO)

# Configurable MySQL URI with root:root default (found on machine)
MYSQL_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/ai_osm")
SQLITE_URL = "sqlite:///./ai_osm.db"

engine = None
active_db_type = "mysql"

try:
    # Test MySQL connection with a short connect timeout
    test_engine = create_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3}
    )
    with test_engine.connect() as conn:
        pass
    engine = test_engine
    active_db_type = "MySQL (ai_osm)"
    logger.info("Successfully connected to MySQL database: ai_osm")
except Exception as e:
    logger.warning(f"MySQL connection failed ({e}). Falling back smoothly to SQLite: {SQLITE_URL}")
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    active_db_type = "SQLite (ai_osm.db - Fallback)"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
