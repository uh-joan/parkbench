#!/usr/bin/env python3
"""
Standalone script to create database tables on Railway
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from db.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        # Get DATABASE_URL from environment
        database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://parkbenchuser:parkbenchpassword@localhost:5432/parkbenchdb"
        )
        
        logger.info(f"Connecting to database...")
        logger.info(f"Database URL: {database_url[:50]}...")  # Log partial URL for debugging
        
        # Create engine
        engine = create_engine(
            database_url,
            echo=True,  # Show SQL statements
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "application_name": "parkbench-table-creator"
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1) 