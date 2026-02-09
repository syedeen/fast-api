
from pydantic import BaseModel , Field , EmailStr ,conint , field_validator
from typing import Optional
from datetime import datetime
from pwdlib import PasswordHash

class FilmCreate(BaseModel):
    title : str
    duration_in_mins : int 
    is_g: bool 
    rating : float


class FilmResponse(BaseModel):
    film_id : int 
    title : str
    duration_in_mins : int 
    is_g: bool 
    rating : float


class FilmResponseAll(BaseModel):
    title : str
    duration_in_mins : int 
    is_g: bool 
    rating : float
    vote:int
    
    
  


class ActorCreate(BaseModel):
    actor_name : str
    film_count : int = Field(default=0 , ge=0)
    actor_age :int = Field(ge=15 , le=90)

class ActorResponse(BaseModel):
    actor_id: int
    actor_name: str
    actor_age: int
    created_at: datetime

    class ConfigDict: #customize model's behaviour
        from_attributes = True #Pydantic expects dict {allows to retrieve data from objects}


class ActorResponseAll(BaseModel):
    actor_name: str
    film_count: int
    actor_age: int





class ActorUpdate(BaseModel):
    actor_name: Optional[str] = None
    film_count: Optional[int] = None
    actor_age: Optional[int] = None


class Film_Actor_create(BaseModel):
    film_id: int 
    actor_id: int

class Film_Actor_response(BaseModel):
    film_id: int 
    actor_id: int




class UserCreate(BaseModel):
    email: EmailStr
    username : str
    password : str


class UserLogin(BaseModel):
    username :str
    password: str


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    created_at: datetime

    class ConfigDict:
        from_attributes = True

class Token(BaseModel):
    access_token:str
    token_type:str




# class method  (not instance method) 
class VotesCreate(BaseModel):
    film_id: int
    vote: int

    @field_validator("vote")
    @classmethod
    def validate_vote(cls, v):
        if v not in (-1, 1):
            raise ValueError("vote must be -1 or 1")
        return v

