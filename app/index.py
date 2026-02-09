from fastapi import FastAPI , HTTPException , Response , status , Depends 
from fastapi.params import Body
from typing import Optional , List
from .database import engine , Base , get_db
from .model import Actor , User , Films , Film_Actor , Film_votes
from sqlalchemy.orm import Session
from sqlalchemy import select , or_ , and_ , func
from sqlalchemy.exc import IntegrityError
from datetime import datetime , timedelta ,timezone
from .schema import ActorCreate , ActorUpdate , ActorResponse ,ActorResponseAll  ,FilmCreate , FilmResponse , FilmResponseAll,Film_Actor_create , Film_Actor_response
from .schema import UserCreate , UserLogin ,UserResponse ,Token , VotesCreate
from pwdlib import PasswordHash
from jose import JWTError, jwt
from passlib.context import CryptContext   
from fastapi.security import OAuth2PasswordRequestForm
from .auth import get_current_user
import os
from dotenv import load_dotenv
load_dotenv()
from .auth import (
    get_pass_hash ,
    verify_pass_hash,
    create_access_token,
    verify_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINS
)



Base.metadata.create_all(bind=engine)
app = FastAPI()

MAX_LOGIN_ATTEMPTS = 5
LOCKIN_DURATION_MINUTES = 15

@app.get("/")
def root():
    return {"welcome to my API"}




# create actor
@app.post("/actors",status_code=status.HTTP_201_CREATED, response_model=ActorResponse)
def create_films(create_actor:ActorCreate, db: Session = Depends(get_db) , user : User =  Depends(get_current_user)):
    new_actor = Actor(
        actor_name = create_actor.actor_name,
        film_count=create_actor.film_count,
        actor_age=create_actor.actor_age,
        owner_id = user.user_id
    )
    db.add(new_actor)
    db.commit()
    db.refresh(new_actor)
    return new_actor
    



# all actors    
@app.get("/actors" , response_model=list[ActorResponseAll])
def get_films(db:Session = Depends(get_db) , user : User =  Depends(get_current_user),limit:int=10,skip:int=0, search:Optional[str] = ""):
    query = select(Actor).filter(Actor.actor_name.contains(search)).limit(limit).offset(skip)   
    actors = db.scalars(query).all()
    if not actors:
        raise HTTPException(status_code=status.HTTP_200_OK , detail="No actors found")
    return actors




# update actor
@app.put("/actors/{actor_id}", response_model=ActorResponse)
def update_actor(actor_id: int, actor_update: ActorUpdate, db: Session = Depends(get_db) , user : User =  Depends(get_current_user)  ):
    actor_update = db.get(Actor, actor_id)
    if not actor_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id {actor_id} not found"
        )
    
    if user.user_id != actor_update.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail={"detail":"you don't own this actor"})
    
    if actor_update.actor_name is not None:
        Actor.actor_name = actor_update.actor_name
    if actor_update.film_count is not None:
        Actor.film_count = actor_update.film_count
    if actor_update.actor_age is not None:
        Actor.actor_age = actor_update.actor_age
    
    db.commit()
    db.refresh(actor_update)
    return actor_update



# get actor
@app.get("/actors/{actor_id}" , response_model=ActorResponse)
def get_actor(actor_id:int , db :Session = Depends(get_db)  , user : User =  Depends(get_current_user) ):
    get__actor = db.get(Actor , actor_id)
    if not get__actor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Actor not found")
    if user.user_id != get__actor.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail={"detail":"you don't own this actor"})
    # for actor in get__actor.films:
    #     print("defffwerfwewrefwre" , actor)
    return get__actor




# delete actor
@app.delete("/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_actor(actor_id: int, db: Session = Depends(get_db) , user : User =  Depends(get_current_user) ):
    delete_actor = db.get(Actor, actor_id)
    if not delete_actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id {actor_id} not found"
        ) 
    if user.user_id != delete_actor.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail={ "detail":"you don't own this actor"})
    
    db.delete(delete_actor)
    db.commit()
    
    


# create film
@app.post("/films" , response_model = FilmResponse)
def create_film(film:FilmCreate , db:Session = Depends(get_db) , user:User = Depends(get_current_user)):
    new_film = Films(
        title = film.title, 
        duration_in_mins = film.duration_in_mins,
        is_g = film.is_g,
        rating = film.rating,
        owner_id = user.user_id
    )
    db.add(new_film)
    db.commit()
    db.refresh(new_film)

    return new_film



# get all films
@app.get("/films",response_model= List[FilmResponseAll])
def get_films(db:Session = Depends(get_db) , user:User = Depends(get_current_user),limit:int=10,skip:int=0, search:Optional[str] = ""):

    query = (
    select(Films , func.count(Film_votes.film_id).label("votes"))
    .outerjoin(Film_votes,Film_votes.film_id == Films.film_id)
    .where(Films.title.contains(search))
    .group_by(Films.film_id)
    .limit(limit)
    .offset(skip)
    )

    films = db.execute(query).all()

    if not films:
        raise HTTPException(status_code=status.HTTP_200_OK , detail={"detail" :"No films found"})
  
    films_list = [
    FilmResponseAll(
        title=film.title,
        duration_in_mins=film.duration_in_mins,
        is_g=film.is_g,
        rating=film.rating,
        vote=votes,
    )
    for film, votes in films
]

    return films_list



@app.post("/films/film_actor")
def create_film_actor(film_actors:Film_Actor_create,db:Session = Depends(get_db) , user: User = Depends(get_current_user)):
   film = db.get(Films , film_actors.film_id)
   actor = db.get(Actor , film_actors.actor_id)
    

   
   if not film:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="film not found")
   
   if not actor:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="actor not found")
   
   stmt =   select(Film_Actor).where(and_(Film_Actor.film_id  == film.film_id, Film_Actor.actor_id == actor.actor_id))
   exists = db.scalars(stmt).first()

   if exists:
       raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="actor is already assigned to this film")
   
   if user.user_id != film.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail="you don't own this film")
   
   if user.user_id != actor.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail="you don't own this actor")
      
   film_actor = Film_Actor(
        film_id = film_actors.film_id,
        actor_id = film_actors.actor_id

    )
   
   
   
   db.add(film_actor)
   db.commit()
   db.refresh(film_actor)
   return {"data":"actor was linked to the film successfully"}

    

    
# register user
@app.post("/users/register",response_model=UserResponse)
def register_user(user:UserCreate,db:Session = Depends(get_db)):
    stmt1 = select(User).where(User.email == user.email)
    existing_email = db.scalars(stmt1).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Email already registered")
    
    stmt2 = select(User).where(User.username == user.username)
    existing_user_name = db.scalars(stmt2).first()
    if existing_user_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="username already taken") 

    new_user = User(
        email = user.email,
        username = user.username,
        password = get_pass_hash(user.password)
    )
        
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
        


# login user
@app.post("/users/login" , response_model=Token)
def login_user(form_data : OAuth2PasswordRequestForm = Depends() , db:Session = Depends(get_db)):
    stmt = select(User).where(
        or_(
            User.username == form_data.username,
            User.email == form_data.username
        )
    )
    existing_user = db.scalars(stmt).first()

    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid_credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not existing_user:
        verify_pass_hash("dummy_password",get_pass_hash("dummy_password"))
        raise invalid_credentials_exception
    

    if existing_user.locked_until and existing_user.locked_until > datetime.now(timezone.utc):
        remaining_time = (existing_user.locked_until - datetime.now(timezone.utc)).seconds // 60 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is locked. Try again in {remaining_time} minutes "
        )

    
    if not existing_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    if not verify_pass_hash(form_data.password , existing_user.password):
        existing_user.failed_login_attempts += 1

        if existing_user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            existing_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKIN_DURATION_MINUTES)
            db.commit()
            time_remaining = (existing_user.locked_until - datetime.now(timezone.utc)).seconds // 60
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked due to too many failed attempts  , Try again in {LOCKIN_DURATION_MINUTES} minutes"
            )
        
        db.commit()
        raise invalid_credentials_exception

    existing_user.failed_login_attempts = 0
    existing_user.locked_until = None 
    existing_user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(
        data = {"user_id" : existing_user.user_id} , 
        expire_data=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    )

    
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }



#get user
@app.get("/users/me")
def get_current_user_info(current_user : User = Depends(get_current_user)):
    return current_user



@app.post("/films/votes")
def vote_film(voted: VotesCreate , db:Session=Depends(get_db) , user:User = Depends(get_current_user)):
    if not voted.film_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Film not found")
    
    stmt = select(Film_votes).where(and_(Film_votes.film_id == voted.film_id ,  Film_votes.user_id == user.user_id))
    existing_vote = db.scalars(stmt).first()

    if existing_vote:
        if existing_vote.vote == voted.vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="You have already voted this way")
        existing_vote.vote = voted.vote
        db.commit()
        db.refresh(existing_vote)
        return {"message: vote changed" : existing_vote}
    
    films_vote = Film_votes(
        film_id = voted.film_id,
        user_id = user.user_id,
        vote = voted.vote
    )

    db.add(films_vote)
    db.commit()
    db.refresh(films_vote)

    return films_vote