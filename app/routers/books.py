from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from typing import List
from sqlalchemy.orm import Session
from crud import crud
from schemas import schemas


router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db)):
    books = crud.get_books(db)
    return books


@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
    return db_book


@router.post("/insert-book/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)


@router.post("/issue-book/", response_model=schemas.IssueBook)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    return crud.create_issue(db=db, issue=issue)


@router.get("/issues/", response_model=List[schemas.IssueBook])
def issue(db: Session = Depends(get_db)):
    return crud.get_issues(db=db)
