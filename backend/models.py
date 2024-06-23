import datetime
import math
from typing import List
import pytz
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from starlette.websockets import WebSocket

from database import Base
from core import caching
from config import TIME_INTERVAL




class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_price = Column(Float)
    date_of_start = Column(DateTime)
    owner = Column(String)
    picture_path = Column(String)
    is_sold = Column(Boolean)
    sell_counts = Column(Integer)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        price = caching.get("active:price").decode('utf-8')

        owner = caching.get("active:owner").decode('utf-8')

        active_id = caching.get("active:id").decode('utf-8')

        last_bid = caching.get("active:last_bid")
        if last_bid:
            last_bid = last_bid.decode('utf-8')
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz)
            last_bid = datetime.datetime.strptime(last_bid, '%Y-%m-%d %H:%M:%S.%f%z')
            diff = (current_time_moscow - last_bid).total_seconds()
            progress_bar = 100 - math.ceil(diff / TIME_INTERVAL)
            await websocket.send_json(
                {"price": price, "address": owner, "active_id": active_id, "progress_bar": progress_bar})
        else:
            await websocket.send_json(
                {"price": price, "address": owner, "active_id": active_id, "progress_bar": 100})
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)
