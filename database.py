from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utility.config import create_db_url

db_url = create_db_url()

engine = create_async_engine(db_url,
                            echo=True,
                            pool_size=10,
                            max_overflow=20,
                            pool_timeout=30,
                            pool_recycle=1800)

AsyncSessionLocal = sessionmaker(class_=AsyncSession, bind=engine, expire_on_commit=False)

Base = declarative_base()

