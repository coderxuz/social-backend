from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DB_URL = "postgresql+psycopg2://postgres:coderxuz@localhost/learn"
ASYNC_DB_URL = "postgresql+asyncpg://postgres:coderxuz@localhost/learn"
# DB_URL= "sqlite:///database.db"
engine = create_engine(DB_URL)
async_engine = create_async_engine(ASYNC_DB_URL)

SessionLocal = sessionmaker(bind=engine)

AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
