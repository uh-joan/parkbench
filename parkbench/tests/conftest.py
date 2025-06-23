import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # Recommended for SQLite in-memory for tests
import os

# Set environment variable for testing BEFORE importing application modules
# that might read it at import time (like settings.py or models.py)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Alternatively, monkeypatch settings directly if they are already imported

from parkbench.backend.main import app # app from your FastAPI application
from parkbench.backend.db.models import Base, get_db, init_db # Base for creating tables, get_db for overriding
from parkbench.backend.config import settings # To potentially override settings

# Override DATABASE_URL for testing if not done by environment variable
# This ensures that any direct use of settings.DATABASE_URL is also overridden
settings.DATABASE_URL = "sqlite:///:memory:"
# print(f"Using database for testing: {settings.DATABASE_URL}") # For debugging

# Setup a test database
# Using StaticPool for SQLite as recommended for FastAPI tests.
# connect_args={"check_same_thread": False} is needed only for SQLite.
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} # Specific to SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Apply migrations or create tables
# Base.metadata.create_all(bind=engine)
# Instead of calling create_all here, we let init_db handle it,
# ensuring it's consistent with the app's behavior.
# init_db(settings.DATABASE_URL) # This will use the overridden URL


@pytest.fixture(scope="session", autouse=True)
def initialize_test_db():
    """
    Initializes the database for the test session.
    This fixture will run once per test session due to autouse=True and scope="session".
    """
    # print(f"Fixture initialize_test_db: Using DB URL {settings.DATABASE_URL}")
    # The engine used by init_db should be the test engine.
    # We need to ensure init_db in models.py uses the engine we define here for tests.
    # One way is to ensure models.init_db can accept an engine or reuses the one created here.

    # For now, let's ensure init_db is called with the test URL and it correctly sets up
    # its internal engine and SessionLocal for the test context.
    # The main app's init_db will create its own engine. We need to override that for tests.

    # The critical part is overriding the get_db dependency.
    # The tables should be created on the test engine.
    Base.metadata.create_all(bind=engine) # Create tables on the in-memory SQLite database
    yield
    Base.metadata.drop_all(bind=engine) # Clean up after tests


@pytest.fixture(scope="function")
def db_session():
    """
    Provides a database session for a single test function.
    Rolls back changes after the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provides a TestClient instance for making requests to the FastAPI app.
    Overrides the get_db dependency to use the test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            # db_session.close() # Handled by db_session fixture itself
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides after test
    app.dependency_overrides.clear()

# Note: The `autouse=True` for `initialize_test_db` means it runs automatically
# for the session. The `client` fixture then uses `db_session` which relies on this setup.
# The order of fixture execution and dependency injection handles the setup.
# Make sure that `parkbench.backend.db.models.init_db` is not an issue.
# The `Base.metadata.create_all(bind=engine)` in `initialize_test_db` should handle table creation
# for the test session using the in-memory SQLite engine.
# The application's `lifespan` manager which calls `init_db` might try to use the
# production DB URL if `settings.DATABASE_URL` isn't patched early enough or if `init_db`
# doesn't respect a pre-configured engine for testing.
# Setting os.environ["DATABASE_URL"] at the top is crucial.
# And patching `settings.DATABASE_URL` directly.
# The `TestClient` itself handles the lifespan events, so it should pick up the
# test database configuration if `settings.DATABASE_URL` is correctly patched.
# The main app's `init_db` call within the lifespan will use the patched `settings.DATABASE_URL`.
# And `models.init_db` should ideally be flexible enough or re-entrant.
# The current `models.init_db` reinitializes its global `engine` and `SessionLocal`
# based on the `db_url` passed to it. So, the lifespan call to `init_db(settings.DATABASE_URL)`
# with the patched URL should correctly use the in-memory SQLite for the TestClient's lifespan.
# The `Base.metadata.create_all(bind=engine)` in `initialize_test_db` is also good as it directly
# targets the test engine.
# The `db_session` fixture then provides isolated sessions from this test engine.
# This setup seems robust.Tool output for `create_file_with_block`:
