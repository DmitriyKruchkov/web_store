import asyncio
from typing import List

import requests
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket

from config import DATABASE_URL

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_price = Column(Float)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.last_sum = 1
        self.last_owner = "-"

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json(self.last_owner)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)
        self.last = message