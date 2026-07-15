import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, event, Column, Integer, String, Float, Index
from sqlalchemy.orm import declarative_base, sessionmaker

# -------------------------------------------------------
# ENGINE CONFIGURATION & CONCURRENCY TUNING
# -------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "predictions.db")
    DATABASE_URL = f"sqlite:///{db_path}"

# Setup Engine with proper connection pools
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"timeout": 30},  # Wait up to 30s for locked database files
    )
    
    # Configure WAL (Write-Ahead Logging) and Normal sync mode to avoid locks during concurrent writes
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 mins to avoid stale sockets
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------------------------------------
# DATA MODEL & SCHEMAS
# -------------------------------------------------------
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, nullable=False)
    temp_c = Column(Float, nullable=False)
    predicted_kwh = Column(Float, nullable=False)
    created_at = Column(String, nullable=False)

# Optimize querying speeds by indexing fields
Index("idx_predictions_timestamp", Prediction.timestamp)
Index("idx_predictions_created_at", Prediction.created_at)

# -------------------------------------------------------
# CORE DATABASE OPERATIONS
# -------------------------------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)

def save_prediction(timestamp: str, temp_c: float, predicted_kwh: float):
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    session = SessionLocal()
    try:
        new_row = Prediction(
            timestamp=timestamp,
            temp_c=temp_c,
            predicted_kwh=predicted_kwh,
            created_at=now_iso
        )
        session.add(new_row)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_history(limit: int = 10):
    session = SessionLocal()
    try:
        rows = session.query(Prediction).order_by(Prediction.id.desc()).limit(limit).all()
        return [
            {
                "timestamp": r.timestamp,
                "temp_c": r.temp_c,
                "predicted_kwh": r.predicted_kwh
            }
            for r in rows
        ]
    finally:
        session.close()
