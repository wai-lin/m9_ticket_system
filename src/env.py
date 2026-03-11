"""Environment variable configuration"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===== Database Configuration =====
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "ticket_system")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
DB_ISOLATION_LEVEL = os.getenv("DB_ISOLATION_LEVEL", "READ COMMITTED")

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Add schema to search_path if specified
if DB_SCHEMA:
    DATABASE_URL += f"?options=-csearch_path%3D{DB_SCHEMA}"

# ===== Redis Configuration =====
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
