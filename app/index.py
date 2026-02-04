from fastapi import FastAPI , HTTPException , Response , status , Depends
from fastapi.params import Body
from pydantic import BaseModel , Field
from typing import Optional
from .database import engine , Base , get_db
from .model import Actor
from sqlalchemy.orm import Session
from sqlalchemy import select

Base.metadata.create_all(bind=engine)
app = FastAPI()


class ActorCreate(BaseModel):
    actor_name : str
    film_count : int = Field(default=0 , ge=0)
    actor_age :int = Field(ge=15 , le=90)

class ActorResponse(BaseModel):
    actor_id: int
    actor_name: str
    film_count: int
    actor_age: int

    class Config: #customize model's behaviour
        from_attributes = True #Pydantic expects dict {allows to retrieve data from objects}

class ActorUpdate(BaseModel):
    actor_name: Optional[str] = None
    film_count: Optional[int] = None
    actor_age: Optional[int] = None



@app.get("/")
def root():
    return {"welcome to my API"}




# create film
@app.post("/actors",status_code=status.HTTP_201_CREATED, response_model=ActorResponse)
def create_films(create_actor:ActorCreate, db: Session = Depends(get_db)):
    new_actor = Actor(
        actor_name = create_actor.actor_name,
        film_count=create_actor.film_count,
        actor_age=create_actor.actor_age
    )
    db.add(new_actor)
    db.commit()
    db.refresh(new_actor)
    return new_actor
    



# all film 
@app.get("/actors" , response_model=list[ActorResponse])
def get_films(db:Session = Depends(get_db)):
    query = select(Actor)
    actors = db.scalars(query).all()
    return actors




# update
@app.put("/actors/{actor_id}", response_model=ActorResponse)
def update_actor(actor_id: int, actor_update: ActorUpdate, db: Session = Depends(get_db)):
    actor_update = db.get(Actor, actor_id)
    if not actor_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id {actor_id} not found"
        )
    
    if actor_update.actor_name is not None:
        Actor.actor_name = actor_update.actor_name
    if actor_update.film_count is not None:
        Actor.film_count = actor_update.film_count
    if actor_update.actor_age is not None:
        Actor.actor_age = actor_update.actor_age
    
    db.commit()
    db.refresh(actor_update)
    return actor_update


@app.get("/actors/{actor_id}" , response_model=ActorResponse)
def get_actor(actor_id:int , db :Session = Depends(get_db)):
    get__actor = db.get(Actor , actor_id)
    if not get__actor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Actor not found")
    return get__actor




# delete film
@app.delete("/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_actor(actor_id: int, db: Session = Depends(get_db)):
    delete_actor = db.get(actor, actor_id)
    if not delete_actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id {actor_id} not found"
        )
    
    db.delete(delete_actor)
    db.commit()
    
    

    

 
