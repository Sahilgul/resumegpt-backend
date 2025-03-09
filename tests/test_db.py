import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text  # ✅ Import text for raw queries

DATABASE_URL = "clea"

engine = create_async_engine(DATABASE_URL, echo=True)

@pytest.mark.asyncio
async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT NOW()"))  # ✅ Use text() here
            db_time = result.scalar()  # ✅ Fetch the first column value
            assert db_time is not None, "Database connection failed"
            print(f"✅ Database Time: {db_time}")
    except Exception as e:
        pytest.fail(f"❌ Database connection error: {e}")
