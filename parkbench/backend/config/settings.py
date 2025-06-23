import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env file into environment variables

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://parkbenchuser:parkbenchpassword@localhost:5432/parkbenchdb")

# API Configuration
API_PREFIX = "/api/v1" # Example API prefix

# Agent Settings (can be expanded)
DEFAULT_AGENT_VERIFIED_STATUS = False
DEFAULT_AGENT_ACTIVE_STATUS = True

# JWT Settings (if you implement token-based auth for agents or users)
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Example of how to load other settings:
# SOME_OTHER_SETTING = os.getenv("SOME_OTHER_SETTING", "default_value")

# It's good practice to ensure critical environment variables are set
# if not DATABASE_URL:
#     raise ValueError("DATABASE_URL environment variable not set and no default provided.")
# if not JWT_SECRET_KEY and "your-secret-key" in JWT_SECRET_KEY: # Be careful with default secrets in prod
#     print("Warning: JWT_SECRET_KEY is using a default value. Set a strong secret in your environment.")
