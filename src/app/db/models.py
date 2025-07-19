from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crypto:strongpassword123@postgres/signals_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    action = Column(String)
    indicators = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
