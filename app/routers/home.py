from fastapi import APIRouter, Depends, HTTPException, Request, status, responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, timedelta, date

from models import models
from dependencies import get_db
from crud import crud
from auth import token

max_issue = 3

templates = Jinja2Templates(directory="frontend")

router = APIRouter(
    include_in_schema=False,
    responses={404: {"description": "Not found"}},
)


@router.get("/home", response_class=HTMLResponse)
def item_home(request: Request, db:Session=Depends(get_db)):
    books = crud.get_books(db)
    try:
        email = token.get_current_user_email(request)
        user = db.query(models.User).filter(models.User.email==email).first()
        return templates.TemplateResponse("item_home.html", {"request": request, "books": books, "user":user})
    except:
        return templates.TemplateResponse("item_home.html", {"request": request, "books": books})


@router.get("/book/{book_id}", response_class=HTMLResponse)
def item_detail(request: Request, book_id: int, db:Session=Depends(get_db)):
    book = crud.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return templates.TemplateResponse("item_detail.html", {"request": request, "book": book})


@router.get("/books/create-book/")
def create_book(request:Request):
    try:
        email = token.get_current_user_email(request)
    except:
        return responses.RedirectResponse("/login/?msg=Please Login first...", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("create_item.html", {"request":request})


@router.post("/books/create-book/")
async def create_book(request:Request, db:Session=Depends(get_db)):
    try:
        email = token.get_current_user_email()
        form = await request.form()
        title = form.get("title")
        description = form.get("description")
        stock = form.get("quantity")
        errors = []

        if not title:
            errors.append("Please enter a title")
        if not description:
            errors.append("Please enter a description")
        if len(errors) > 0:
            return templates.TemplateResponse("create_item.html", {"request":request, "errors":errors})

        user = db.query(models.User).filter(models.User.email==email).first()        
        book = models.Book(title=title, description=description, stock=stock, created_by=user.email)
        db.add(book)
        db.commit()
        return responses.RedirectResponse(f"/book/{book.id}", status_code=status.HTTP_302_FOUND)
    except:
        return responses.RedirectResponse("/login/?msg=Please Login first...", status_code=status.HTTP_404_NOT_FOUND)


@router.get("/search")
def search_book(request: Request, query:Optional[str], db:Session=Depends(get_db)):
    books = db.query(models.Book).filter(models.Book.title.contains(query)).all() 
    return templates.TemplateResponse("item_home.html", {"request":request, "books":books})


@router.get("/issue-book/{book_id}")
def issue_book(request: Request, book_id:int, db:Session=Depends(get_db)):
    try:
        email = token.get_current_user_email(request)
        errors=[]
        book = db.query(models.Book).filter(models.Book.id==book_id).first()

        books_issued = db.query(models.Issue).filter(and_(models.Issue.created_by==email, models.Issue.return_date.is_(None))).all()

        if(len(books_issued)>=max_issue):
            errors.append("You can't issue more than 3 books")
        else:
            last_date=date.isoformat(date.today() + timedelta(days=7))
            issue = models.Issue(book_id=book_id, last_date=last_date, created_by=email)
            book.stock = book.stock - 1
            db.add(issue)
            db.commit()
        return templates.TemplateResponse("item_detail.html", {"request":request, "book":book, "errors":errors})
    except:
        return responses.RedirectResponse("/login/?msg=Please Login first...", status_code=status.HTTP_404_NOT_FOUND)


@router.get("/profile/{user_id}")
def user_profile(request: Request, user_id:int, db:Session=Depends(get_db)):
    email = token.get_current_user_email(request)
    user = db.query(models.User).filter(models.User.id==user_id).first()
    books = db.query(models.Issue).filter(and_(models.Issue.created_by==user.email, models.Issue.return_date.is_(None))).all()
    issue = db.query(models.Issue).filter(models.Issue.created_by==user.email).first()
    return templates.TemplateResponse("profile.html", {"request":request, "books":books, "length":len(books), "user":user, "fees":user.fees})
    

@router.get("/return_book/{issue_id}")
def return_book(request: Request, issue_id:int, db:Session=Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.issue_id==issue_id).first()
    issue.return_date = date.isoformat(date.today())
    book = db.query(models.Book).filter(models.Book.id==issue.book_id).first()
    book.stock = book.stock + 1
    db.commit()

    user = db.query(models.User).filter(models.User.email==issue.created_by).first()
    late = (datetime.strptime(issue.return_date, "%Y-%m-%d")-datetime.strptime(issue.last_date, "%Y-%m-%d")).days
    count = db.query(models.Issue).filter(and_(models.Issue.created_by==user.email, models.Issue.return_date.is_(None))).all()

    if(late>0):
        if user.fees is None:
            user.fees = late*5
        else:
            user.fees = int(user.fees) + late*5
        
        db.commit()
    
    return templates.TemplateResponse("profile.html", {"request":request, "issue_id":issue.issue_id, "user":user, "fees":user.fees, "books":count, "length":len(count)})


@router.get("/add_quantity/{book_id}")
def add_quantity(request: Request,book_id:int, msg:str=None,db:Session=Depends(get_db)):
    try:
        email = token.get_current_user_email(request)
        book = db.query(models.Book).filter(models.Book.id==book_id).first()
        return templates.TemplateResponse("add_quantity.html", {"request": request,"msg":msg, "book":book})
    except:    
        return responses.RedirectResponse("/login/?msg=Please Login first...", status_code=status.HTTP_302_FOUND)


@router.post("/add_quantity/{book_id}")
async def add_quantity(request: Request,book_id: int, msg:str=None,db:Session=Depends(get_db)):
    try:
        form = await request.form()
        quantity = form.get("quantity")
        email = token.get_current_user_email(request)
        book = db.query(models.Book).filter(models.Book.id==book_id).first()

        if book.stock is None:
            book.stock = int(quantity)
        else:
            book.stock = book.stock + int(quantity)

        book.modified_by = email
        db.commit()
        return templates.TemplateResponse("item_detail.html", {"request":request, "book":book})   
    except:
        return responses.RedirectResponse("/login/?msg=Please Login first...", status_code=status.HTTP_302_FOUND)


@router.get("/issue_detail/{issue_id}")
def issue_detail(request: Request,issue_id: int,db:Session=Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.issue_id==issue_id).first()
    book = db.query(models.Book).filter(models.Book.id==issue.book_id).first()
    return templates.TemplateResponse("issue_detail.html", {"request":request, "issue":issue, "book":book})
