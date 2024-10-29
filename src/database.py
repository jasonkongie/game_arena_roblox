# src/database.py

import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList  # Import MutableList

import enum
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'game_arena.db')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GameState(enum.Enum):
    WIN = "win"
    LOSS = "loss"
    PLAYING = "playing"
    FORFEIT = "forfeit"

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID is 36 characters
    username = Column(String(), index=True)
    game_name = Column(String(), index=True)  # Akinator, Taboo, Bluffing
    state = Column(Enum(GameState), default=GameState.PLAYING)
    target_phrase = Column(String)
    model = Column(String)
    share = Column(Boolean, default=False)
    history = Column(MutableList.as_mutable(JSON), default_factory=list)
    timestamp = Column(DateTime, default=func.now())
    round = Column(Integer, default=0)
    game_over = Column(Boolean, default=False)
    game_status = Column(String)
    level = Column(Integer, default=1)  # Added level field

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "username": self.username,
            "game_name": self.game_name,
            "level": self.level,  # Include level in dict
            "state": self.state.value,
            "target_phrase": self.target_phrase,
            "model": self.model,
            "share": self.share,
            "history": self.history,
            "timestamp": self.timestamp.isoformat(),
            "round": self.round,
            "game_over": self.game_over,
            "game_status": self.game_status,
        }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)