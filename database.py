from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./chat_sessions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # "user" or "bot"
    message = Column(Text)
    confidence = Column(String, nullable=True)   # ✅ Add this line
    source = Column(String, nullable=True)        # ✅ Add this line
    timestamp = Column(DateTime, default=datetime.now)

# Create table
Base.metadata.create_all(bind=engine)
