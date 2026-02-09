from jose import jwt , JWTError 
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordBearer ,OAuth2PasswordRequestForm
from datetime import datetime , timezone , timedelta
from typing import Optional
from fastapi import Depends
from fastapi import HTTPException , status
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv
load_dotenv()
from .database import get_db
from .model import User


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") #hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login") #token authentication

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINS = 35




def get_pass_hash(password):
    return pwd_context.hash(password)

def verify_pass_hash(password:str, hashed_password:str):
    return pwd_context.verify(password,hashed_password)

def create_access_token(data:dict , expire_data:Optional[timedelta]):
    to_encode = data.copy()
    if expire_data:
        expire = datetime.now(timezone.utc) + expire_data
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        user_id :str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        
        return user_id
    except JWTError:
        raise credentials_exception
    


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_access_token(token, credentials_exception)
    user = db.query(User).filter(User.user_id == int(user_id)).first()

    
    if user is None:
        raise credentials_exception
    
    return user 