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

# Construct database URL with schema if not public
if DB_SCHEMA and DB_SCHEMA != "public":
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?options=-c%20search_path%3D{DB_SCHEMA}"
else:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ===== Redis Configuration =====
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_USER = os.getenv("REDIS_USER", "default")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Construct Redis URL
if REDIS_PASSWORD:
    REDIS_URL = f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# ===== Snowflake Configuration =====
SF_HOST = os.getenv("SF_HOST", "gkb48589.snowflakecomputing.com")
SF_ACCOUNT = os.getenv("SF_ACCOUNT", "GKB48589")
SF_USER = os.getenv("SF_USERNAME", "student")
SF_PASSWORD = os.getenv("SF_PASSWORD", "HSUnivSFTests970")
SF_DATABASE = os.getenv("SF_DATABASE", "SF_SAMPLE")
SF_WAREHOUSE = os.getenv("SF_WAREHOUSE", "COMPUTE_S")
SF_SCHEMA = "ANALYTICS_MART"
