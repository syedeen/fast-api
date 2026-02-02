from fastapi import FastAPI , HTTPException , Response , status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


@app.get("/")
def root():
    return {"welcome to my API"}

while True:
    try:
        conn = psycopg2.connect(dbname="py_db" , user="postgres", host = "localhost" , port=5432 , password = "2005" ,  cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successfull")
        break
    except Exception as error:
        print("connection to database failed")
        print("Error :",error)
        time.sleep(2)

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



# get_film_by_id
def get_film(film_id:int):
    try:
        cursor.execute("""
        SELECT * 
        FROM films 
        WHERE film_id = %s
    """, 
    (
        film_id
    )
    )
        film = cursor.fetchone()
        if not film:
            raise HTTPException(status_code=404 , detail="film not found")
        return {"data":film}
    except Exception as error:
        raise HTTPException(status_code=500 , detail=str(error))





# create film
@app.post("/films",status_code=status.HTTP_201_CREATED)
def create_films(new_film:films):
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
def get_films():
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
        raise HTTPException(status_code=500 , detail=str(error))




# latest film
@app.get("/films/latest_film")
def latest_post():
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
        raise HTTPException(status_code=500 , detail=str(error))
        
    


# individual film
@app.get("/films/{id}")
def get_film_id(id:int):
    film = get_film(id)
    if not film:
        raise HTTPException(status_code = 404 , detail=f"film with id-{id} not found")
    return film


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
def delete_films(film_id:int):
    try:
        cursor.execute("""
        DELETE FROM films WHERE film_id = %s RETURNING *
    """,(film_id,))
        deleted = cursor.fetchone()
        conn.commit()
        if not deleted:
            raise HTTPException(status_code=404 , detail="Film not found")
    except Exception as error:
        raise HTTPException(status_code=500 , detail=str(error))
    

    

# update(put)
@app.put("/films/{film_id}" , status_code=status.HTTP_204_NO_CONTENT)
def update_film(film_id:int, film:films):
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
        raise HTTPException(status_code=500 , detail=str(error))
    
   

 
