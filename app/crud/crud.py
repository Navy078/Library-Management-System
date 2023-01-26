from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta

from models import models
from schemas import schemas
from hashing import hashing

def get_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hashing.Hasher.get_hash(user.password)
    query = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(query)
    db.commit()
    return query


def get_books(db: Session):
    return db.query(models.Book).all()


def get_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    return db_book


def get_issues(db: Session):
    return db.query(models.Issue).all()


def get_issue(db: Session, issue_id: int):
    db_issue = db.query(models.Issue).filter(models.Issue.issue_id == issue_id).first()
    return db_issue


def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, description=book.description, stock=book.stock)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def is_book_available(db: Session, book_id: int):
    issue=db.query(models.Book).filter(book_id==models.Book.id).first()
    if issue.stock>0:
        return True
    return False


def create_issue(db: Session, issue: schemas.IssueCreate):
    # user_id=issue.user_id
    book_id=issue.book_id
    curDate = date.today()
    issue_date=date.isoformat(curDate)
    last_date=date.isoformat(curDate + timedelta(days=7))

    user = db.query(models.User)

    if is_book_available(db, book_id):
        db_issue = models.Issue(issue_date=issue_date, book_id=book_id, last_date=last_date)
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not available")
    return db_issue


def return_book(issue_id: int, db: Session):
    issue=db.query(models.Issue).filter(models.Issue.issue_id==issue_id).first()

    if not issue or issue.is_bought==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Issue not available")

    issue.return_date = date.isoformat(date.today())
    req_book=db.query(models.Book).filter(issue.book_id==models.Book.id).first()
    db.commit()
    req_book.stock=req_book.stock+1
    db.commit()
    return req_book


def valid_user(db: Session, user_email: str, user_password: int):
    hashed_password = hashing.Hasher.get_hash(user_password)
    db_user = db.query(models.User).filter(and_(models.User.email==user_email, models.User.hashed_password==hashed_password)).first()
    return db_user
