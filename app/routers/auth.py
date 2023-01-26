from fastapi import APIRouter, Depends, Request, responses, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependencies import get_db
from sqlalchemy.exc import IntegrityError

from models import models
from hashing import hashing
from auth import token


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="frontend")


@router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("user_register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    password = form.get("password")
    hashed_password = hashing.Hasher.get_hash(password)
    errors = []
    if len(password) < 8:
        errors.append("Passwords should be minimum 8 characters long")
        response = templates.TemplateResponse("user_register.html", {"request":request, "errors":errors})
    else:
        query = models.User(name=form.get("name"), email=form.get("email"), hashed_password=hashed_password, created_by=form.get("name"))
        try:
            db.add(query)
            db.commit()
            response = responses.RedirectResponse("/login/?msg=Successfully Registered, Login Now...", status_code=status.HTTP_302_FOUND)
        except IntegrityError:
            errors.append("Email already exists")
            response = templates.TemplateResponse("user_register.html", {"request":request, "errors":errors})

    return response


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(response: Response, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    errors = []
    try:
        user=db.query(models.User).filter(models.User.email==email).first()
        if user is None:
            errors.append("Email does not exists")
            response = templates.TemplateResponse("login.html", {"request": request, "errors": errors})
        else:
            if hashing.Hasher.verify_password(password, user.hashed_password):
                token.store_cookie(response,email)
                response = responses.RedirectResponse("/home/?msg=Successfully Logged In...", status_code=status.HTTP_302_FOUND)
            else:
                errors.append("Invalid Password")
                response = templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    except:
        errors.append("Something Wrong while authentication or storing tokens!")
        response =  templates.TemplateResponse("login.html", {"request": request, "errors": errors})

    return response


@router.get("/logout")
def logout(request: Request):
    try:
        email = token.get_current_user_email(request)
        response = responses.RedirectResponse("/login/?msg=Please Login First...", status_code=status.HTTP_302_FOUND)
    except:
        response = responses.RedirectResponse("/login/?msg=Successfully Logged Out...", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("access_token")

    return response




#  project on node js
#  store mail, templates = welocme, sanction, results
#  sequelize, postgres, oops, nunjx, smtp integration, json dump, number of mails sent