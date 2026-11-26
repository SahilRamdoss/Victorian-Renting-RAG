from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
Sessionlocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    with Sessionlocal() as db:
        yield db