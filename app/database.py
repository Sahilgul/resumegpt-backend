import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from google.cloud import secretmanager
# Initialize Google Secret Manager client
def access_secret_version(secret_id: str, project_id="stalwart-star-448320-c8"):
    """
    Fetches a secret from Google Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    try:
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        return None
    


# Load secrets from Google Secret Manager
GCP_PROJECT_ID = "stalwart-star-448320-c8" 
os.environ["DATABASE_URL"] = access_secret_version("DATABASE_URL") or ""
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



from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


# # Dependency for async database session
# async def get_db():
#     async with AsyncSessionLocal() as db:
#         yield db  # Yield async session




