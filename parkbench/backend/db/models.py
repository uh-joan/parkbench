# Placeholder for database models

from sqlalchemy import create_engine, Column, String, Boolean, Text, TIMESTAMP, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from typing import Generator
from config.settings import get_settings

# Database setup
Base = declarative_base()

class SessionStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class Agent(Base):
    """Agent registration table"""
    __tablename__ = "agents"
    
    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(255), unique=True, nullable=False, index=True)
    certificate_pem = Column(Text, nullable=False)
    agent_metadata = Column(JSONB, nullable=False)  # Renamed from metadata to avoid SQLAlchemy conflict
    verified = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class A2ASession(Base):
    """A2A session management table"""
    __tablename__ = "a2a_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiating_agent = Column(String(255), nullable=False)
    target_agent = Column(String(255), nullable=False)
    task = Column(String(255), nullable=False)
    session_token = Column(Text, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    context = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

# Database engine and session
engine = None
SessionLocal = None

def init_db():
    """Initialize database connection"""
    global engine, SessionLocal
    settings = get_settings()
    
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on module import
init_db()
