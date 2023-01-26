from sqlalchemy import Column, ForeignKey, Integer, String

from models import base_class

class User(base_class.Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    fees = Column(Integer)


class Book(base_class.Base):
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    stock = Column(Integer, index=True)


class Issue(base_class.Base):
    __tablename__ = "issues"
    __table_args__ = {'extend_existing': True}

    issue_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    last_date = Column(String, index=True)
    return_date = Column(String)
