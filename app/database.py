import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get DATABASE_URL from .env (default to SQLite if not found)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create async database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Define Base for ORM models
Base = declarative_base()

# Dependency for async database session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db  # Yield async session
