from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.future import select
from starlette.middleware.cors import CORSMiddleware

from routers import rest_router
from models import ConnectionManager, engine, Base, SessionLocal, Product
from config import origins

app = FastAPI()
app.include_router(rest_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                        await manager.broadcast({'price': product.current_price})
                        await session.commit()

    except WebSocketDisconnect:
        manager.disconnect(websocket)




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
