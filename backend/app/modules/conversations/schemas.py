"""Small detached context sent to the routing model."""

from pydantic import BaseModel


class HistoryTurn(BaseModel):
    question: str
    answer: str
