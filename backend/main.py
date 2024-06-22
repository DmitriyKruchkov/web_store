import asyncio
import datetime
import threading
from typing import Any
import aiohttp
import pytz
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Form, HTTPException
from sqlalchemy import and_, not_
from sqlalchemy.future import select
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from routers import rest_router
from models import ConnectionManager, engine, Base, SessionLocal, Product
from config import origins, AUTH_URL, CRYPTO_URL, LOGIN_URL, REGISTER_URL, TIME_INTERVAL
import logging
from core import caching

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app.include_router(rest_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/login")
async def login_get(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token and check_token(access_token):
        redirect_response = RedirectResponse(url="/", status_code=303)
        redirect_response.set_cookie(key="access_token", value=access_token)
        active_id = caching.get("active:id").decode('utf-8')
        redirect_response.set_cookie(key="active_id", value=active_id)
        return redirect_response
    return templates.TemplateResponse("login.html", {"request": request, "title": "WebSocket Example"})


@app.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "WebSocket Example"})


@app.post("/register")
async def register_post(crypto: str = Form(...), tg_tag: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(REGISTER_URL,
                                json={"crypto": crypto, "tg_tag": tg_tag, "password": password}) as response:
            data = await response.json()
            if data.get("status"):
                return RedirectResponse("/login", status_code=303)


@app.post("/login")
async def login_post(crypto: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(LOGIN_URL, json={"crypto": crypto, "password": password}) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get("access_token")
                if access_token:
                    redirect_response = RedirectResponse(url="/", status_code=303)
                    redirect_response.set_cookie(key="access_token", value=access_token)
                    active_id = caching.get("active:id").decode('utf-8')
                    redirect_response.set_cookie(key="active_id", value=active_id)
                    return redirect_response
                else:
                    raise HTTPException(status_code=401, detail="Invalid token response")
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if request.cookies.get("access_token"):
        item_name = caching.get("active:name").decode('utf-8')
        img_link = caching.get("active:img_link").decode('utf-8')
        return templates.TemplateResponse("index.html", {"request": request, "item_name": item_name, "img_link": img_link})
    else:
        return RedirectResponse(url="/login")


async def check_token(access_token: str):
    async with aiohttp.ClientSession() as session:
        request = AUTH_URL
        async with session.get(request, json={"access_token": access_token}) as response:
            return await response.json()


async def check_balance(address: str):
    async with aiohttp.ClientSession() as session:
        request = CRYPTO_URL
        async with session.get(request, json={"address": address}) as response:
            return await response.json()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await update_current_item(startup=True)


@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse("/login")


async def accept_winner(id, time):
    print("accepting")
    last_item = caching.get("active:id").decode('utf-8')
    last_bid = caching.get("active:last_bid").decode('utf-8')
    if str(id) == (last_item) and str(time) == str(last_bid):
        async with (SessionLocal() as session):
            async with session.begin():
                stmt = select(Product).where(Product.id == int(id))
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                print(product)
                print(product.is_sold)
                if not product.is_sold:
                    product.is_sold = 1
                    product.sell_counts += 1
                    await session.commit()
                    await update_current_item()


async def update_current_item(startup=False):
    async with (SessionLocal() as session):
        async with session.begin():
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz)
            stmt = select(Product).order_by(Product.sell_counts)  # .where(

            # and_(
            #     Product.date_of_start < current_time_moscow,
            # not_(Product.is_sold)
            # )

            result = await session.execute(stmt)

            current_item = result.scalars().first()
            caching.set("active:id", str(current_item.id))
            caching.set("active:name", str(current_item.name))
            caching.set("active:img_link", str(current_item.picture_path))
            caching.set("active:price", str(current_item.current_price))
            caching.set("active:owner", str(current_item.owner))

def run_async_function(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()
async def set_price_and_owner_to_active(id, price, owner):
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(Product).where(Product.id == id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if product is not None:
                product.current_price = float(price)
                product.owner = owner
                await session.commit()
                caching.set("active:price", price)
                caching.set("active:owner", owner)
                moscow_tz = pytz.timezone('Europe/Moscow')
                current_time_moscow = datetime.datetime.now(moscow_tz)
                caching.set("active:last_bid", str(current_time_moscow))
                threading.Timer(TIME_INTERVAL, run_async_function, args=(accept_winner, id, current_time_moscow)).start()



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, access_token: Any = Depends(check_token)):
    if websocket.cookies.get("access_token"):

        if access_token.get('access'):

            try:
                await manager.connect(websocket)
                while True:
                    percentages = await websocket.receive_text()
                    crypto = access_token.get("crypto")
                    have_sum = (await check_balance(crypto)).get("balance")
                    price = float(caching.get("active:price").decode('utf-8'))
                    new_sum = round(price * (1 + int(percentages) / 100), 2)
                    if have_sum > new_sum:
                        id = int(caching.get("active:id").decode('utf-8'))
                        await set_price_and_owner_to_active(id, new_sum, crypto)
                        await manager.broadcast(
                            {'active_id': id, 'price': new_sum, "address": crypto, "progress_bar": 100}
                        )

            except WebSocketDisconnect:
                manager.disconnect(websocket)
        else:
            await websocket.close()
    else:
        await websocket.close(code=1008)
        return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
