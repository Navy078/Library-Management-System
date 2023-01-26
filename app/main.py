from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from routers import books, users, home, auth
from database import conn
from models import models

models.conn.Base.metadata.create_all(bind=conn.engine)
app = FastAPI()


app.mount("/static", StaticFiles(directory="./static"), name="static")

app.include_router(users.router)
app.include_router(books.router)
app.include_router(home.router)
app.include_router(auth.router)


