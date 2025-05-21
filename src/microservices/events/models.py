from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserEvent(BaseModel):
    user_id: int
    username: str
    action: str
    timestamp: datetime = datetime.utcnow()


class PaymentEvent(BaseModel):
    payment_id: int
    user_id: int
    amount: float
    status: str
    timestamp: datetime = datetime.utcnow()
    method_type: str


class MovieEvent(BaseModel):
    movie_id: int
    title: str
    action: str
    user_id: int
    timestamp: datetime = datetime.utcnow()
