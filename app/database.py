from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = "postgresql+psycopg2://postgres:coderxuz@localhost/learn"
DB_URL= "sqlite:///database.db"
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
