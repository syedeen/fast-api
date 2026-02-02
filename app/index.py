from fastapi import FastAPI , HTTPException , Response , status
from fastapi.params import Body
from fastapi import Depends
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool   
import time
import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager


connection_pool = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection_pool
    print("Creating connection pool...")

    required_variables = ["DB_USER","DB_PASSWORD","DB_NAME"]
    missing_variables = [var for var in required_variables if not os.getenv(var)]

    if missing_variables:
        raise ValueError(f"Missing required environment variables:{', '.join(missing_variables)}")
    
    try:
        #connection pool
        connection_pool = pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=20,
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
    
        
    except Exception as error:
        print("Failed to create connection pool")
        raise

    yield
    print("Closing connection pool...")
        

    if connection_pool:
        connection_pool.closeall()
        print("connection pool closed")

app = FastAPI(lifespan=lifespan)


#dependency
def get_db():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
        



@app.get("/")
def root():
    return {"welcome to my API"}





# No pydantic model 
# @app.post("/films")
# def get_posts(msg: dict = Body(...)):
#     return {"message":f"Hi {msg['name']}"}

# With pydantic model 

class films(BaseModel):
    title:str
    duration:float
    is_g:bool = True
    rating:Optional[float] = None
    released:bool




# create film
@app.post("/films",status_code=status.HTTP_201_CREATED)
def create_films(new_film:films, conn = Depends(get_db)):
    cursor = conn.cursor()
    my_film = new_film.model_dump()
    cursor.execute("""
       INSERT INTO 
       films("title","duration","is_g","rating","released") 
       values(%s,%s,%s,%s,%s) RETURNING *     
    """ , 
    (
        my_film["title"],
        my_film["duration"],
        my_film["is_g"],
        my_film["rating"],
        my_film["released"]
    )
    )
    created_film = cursor.fetchone()
    conn.commit()
    return { "message":"film created successfully" , "data" :created_film}
    



# all film 
@app.get("/films")
def get_films(conn = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute(""" 
        SELECT * 
        FROM films
    """)
        films = cursor.fetchall()
        if not films:
            raise HTTPException(status_code=404 , detail="No films available")
        return {"data":films}
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500 , detail=str(error))
    finally:
        cursor.close()




# latest film
@app.get("/films/latest_film")
def latest_post(conn = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT *
            FROM films where created_at = (
            SELECT MAX(created_at)
            FROM films)
    """)
        latest_film = cursor.fetchone()
        if not latest_film:
            raise HTTPException(status_code=404 , detail="No films available")
        return {"data":latest_film}
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500 , detail=str(error))
    finally:
        cursor.close()
    


# individual film
@app.get("/films/{film_id}")
def get_film_id(film_id:int,conn = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT * 
        FROM films 
        WHERE film_id = %s
    """, 
    (
        film_id, 
    )
    )
        film = cursor.fetchone()
        if not film:
            raise HTTPException(status_code=404 , detail="film not found")
        return {"data":film}
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500 , detail=str(error))
    finally:
        cursor.close()


# response
# @app.get("/films/{id}")
# def get_film_id(id:int , response:Response):
#     film = get_film(id)
#     if not film:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return {"message":f"film with id-{id} not found"}
#     return film




# delete film
@app.delete("/films/{film_id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_films(film_id:int,conn = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute("""
        DELETE FROM films WHERE film_id = %s RETURNING *
    """,(film_id,))
        deleted = cursor.fetchone()
        conn.commit()
        if not deleted:
            raise HTTPException(status_code=404 , detail="Film not found")
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500 , detail=str(error))
    finally:
        cursor.close()   

    

# update(put)
@app.put("/films/{film_id}" , status_code=status.HTTP_204_NO_CONTENT)
def update_film(film_id:int, film:films ,conn = Depends(get_db)):
    cursor = conn.cursor()
    film = film.model_dump()
    try:
        cursor.execute("""
   UPDATE films SET title = %s ,duration = %s ,is_g = %s, rating = %s, released = %s 
   WHERE film_id = %s RETURNING *
   """ , (
       film["title"],
       film["duration"],
       film["is_g"],
       film["rating"],
       film["released"],
       film_id
   ))
        updated = cursor.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=404 , detail="Film not found")
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500 , detail=str(error))
    finally:
        cursor.close()
    

 
