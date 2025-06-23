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
import logging

# Database setup
Base = declarative_base()

class SessionStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"

class Agent(Base):
    """Agent registration table"""
    __tablename__ = "agents"
    
    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(255), unique=True, nullable=False, index=True)
    certificate_pem = Column(Text, nullable=False)
    a2a_descriptor = Column(JSONB, nullable=False)  # Updated to match frontend expectations
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
_db_initialized = False

def init_db():
    """Initialize database connection with error handling"""
    global engine, SessionLocal, _db_initialized
    
    if _db_initialized:
        return
    
    try:
        settings = get_settings()
        logging.info(f"Initializing database connection...")
        
        engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args={
                "connect_timeout": 10,
                "application_name": "parkbench-api"
            }
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        _db_initialized = True
        logging.info("Database initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    if not _db_initialized:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Don't initialize database on module import - let it be lazy
