from typing import Any
from sqlalchemy import Column, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from datetime import date

curDate = date.isoformat(date.today())

@as_declarative()
class Base:
    id: Any
    _name_: str

    @declared_attr
    def created_on(cls):
        return Column(String, default=curDate)

    @declared_attr
    def modified_on(cls):
        return Column(String, onupdate=func.now())

    @declared_attr
    def created_by(cls):
        return Column(String)

    @declared_attr
    def modified_by(cls):
        return Column(String)

