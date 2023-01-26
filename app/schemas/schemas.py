from typing import List
from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    description: str
    stock: int


class Book(BookCreate):
    id: int
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    books: List[Book] = []

    class Config:
        orm_mode = True


class IssueCreate(BaseModel):
    book_id: int


class ReturnBook(IssueCreate):
    return_date: str


class IssueBook(IssueCreate):
    issue_id: int
    issue_date: str
    last_date: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
