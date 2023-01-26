from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import List
from jose import jwt

from dependencies import get_db
from crud import crud
from schemas import schemas


templates = Jinja2Templates(directory="frontend")

router = APIRouter(
    prefix = '/users',
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/register-user/", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    register_user = crud.create_user(db, user)
    return register_user


@router.get("/user-validation/", response_model=schemas.User)
def read_user(user_email: str, user_password: str, db: Session = Depends(get_db)):
    db_user = jwt.authenticate_user(db, username=user_email, password=user_password)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
