"""The single declarative Base; model registration belongs to composition roots."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
