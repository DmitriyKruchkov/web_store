import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List

from starlette.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

app = FastAPI()

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

origins = [
    "*",  # заменить на адрес контейнера
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_price = Column(Float)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.websocket("/ws/{product_id}")
async def websocket_endpoint(websocket: WebSocket, product_id: int):
    await manager.connect(websocket)
    try:
        async with SessionLocal() as session:
            while True:
                data = await websocket.receive_text()
                new_price = float(data)

                async with session.begin():
                    stmt = select(Product).where(Product.id == product_id)
                    result = await session.execute(stmt)
                    product = result.scalar_one_or_none()
                    if product:
                        product.current_price = round(product.current_price * (1 + new_price / 100), 2)
                        await manager.broadcast(f"price {product.current_price}")
                        await session.commit()

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/active_product")
async def get_active_product():
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(Product).order_by(Product.id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            return {"is_active": product.id, "price": product.current_price}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
