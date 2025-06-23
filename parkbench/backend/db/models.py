import uuid
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from ..config.settings import DATABASE_URL # We'll create this settings file soon

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agentName = Column(String(255), unique=True, nullable=False, index=True)
    certificatePEM = Column(String, nullable=False) # TEXT equivalent, String without length for most DBs
    metadata_ = Column("metadata", JSON, nullable=False) # Renamed to avoid conflict with SQLAlchemy internal
    verified = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('agentName', name='uq_agent_name'),)

    def __repr__(self):
        return f"<Agent(agent_id='{self.agent_id}', agentName='{self.agentName}')>"

# Basic database connection setup (can be expanded in a dedicated db module)
engine = None
SessionLocal = None

def init_db(db_url: str = DATABASE_URL):
    global engine, SessionLocal
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine) # Creates tables if they don't exist

def get_db():
    if SessionLocal is None:
        # This is a fallback for scenarios where init_db might not have been called,
        # though in a FastAPI app, it's typically called at startup.
        # Consider raising an error or ensuring init_db is called.
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example of how to use:
# from .models import SessionLocal, Agent
# db = SessionLocal()
# new_agent = Agent(agentName="test.agent", certificatePEM="...", metadata={"key": "value"})
# db.add(new_agent)
# db.commit()
# db.close()
