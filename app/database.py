
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import DeclarativeBase , sessionmaker
from sqlalchemy import create_engine



database_url = URL.create(
    drivername="postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME")
)

engine = create_engine(
    url=database_url ,
    echo=True ,  
    pool_pre_ping=True, 
    pool_size=10,
    max_overflow=20
    )


session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)



class Base(DeclarativeBase):
    pass


#dependency
def get_db():
    db = session_local()
    try:
        yield db 
    finally:
        db.close()
        

