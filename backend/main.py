from typing import Any
import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Form, HTTPException
from sqlalchemy.future import select
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from routers import rest_router
from models import ConnectionManager, engine, Base, SessionLocal, Product
from config import origins, AUTH_URL, CRYPTO_URL, LOGIN_URL, REGISTER_URL
import logging

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
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "WebSocket Example"})


@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "WebSocket Example"})


@app.post("/register")
async def try_register(crypto: str = Form(...), tg_tag: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(REGISTER_URL,
                                json={"crypto": crypto, "tg_tag": tg_tag, "password": password}) as response:

            data = await response.json()
            if data.get("status"):
                return RedirectResponse("/login", status_code=303)


@app.post("/login")
async def try_auth(crypto: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(LOGIN_URL, json={"crypto": crypto, "password": password}) as response:
            print(response)
            if response.status == 200:
                data = await response.json()
                access_token = data.get("access_token")
                if access_token:
                    redirect_response = RedirectResponse(url="/", status_code=303)
                    redirect_response.set_cookie(key="access_token", value=access_token)
                    return redirect_response
                else:
                    raise HTTPException(status_code=401, detail="Invalid token response")
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if request.cookies.get("access_token"):
        return templates.TemplateResponse("index.html", {"request": request, "title": "WebSocket Example"})
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


@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse("/login")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, access_token: Any = Depends(check_token)):
    if websocket.cookies.get("access_token"):
        crypto = access_token.get("crypto")
        if access_token.get('access'):
            await manager.connect(websocket)
            try:
                async with SessionLocal() as session:
                    # if not manager.last_sum:
                    #     manager.last_ = 100  # исправить
                    while True:
                        data = await websocket.receive_text()
                        new_price = float(data)
                        have_sum = (await check_balance(crypto)).get("balance")
                        must_sum = round(manager.price * (1 + new_price / 100), 2)
                        if have_sum > must_sum:
                            async with session.begin():
                                stmt = select(Product).where(Product.id == 1)  # исправить
                                result = await session.execute(stmt)
                                product = result.scalar_one_or_none()
                                if product:
                                    product.current_price = must_sum
                                    manager.price = must_sum
                                    manager.owner = crypto
                                    await manager.broadcast({'price': product.current_price, "address": crypto})
                                    await session.commit()


            except WebSocketDisconnect:
                manager.disconnect(websocket)
        else:
            await websocket.close()
    else:
        return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
