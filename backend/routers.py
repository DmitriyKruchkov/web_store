from fastapi import APIRouter
import aiohttp
from fastapi import Form, HTTPException
from sqlalchemy.future import select
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from models import Product
from utils import check_token
from config import LOGIN_URL, REGISTER_URL
from core import caching, templates
from database import SessionLocal

rest_router = APIRouter()


@rest_router.get("/active_product")
async def get_active_product():
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(Product).order_by(Product.id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            return {"is_active": product.id, "price": product.current_price}


@rest_router.get("/login")
async def login_get(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token and check_token(access_token):
        redirect_response = RedirectResponse(url="/", status_code=303)
        redirect_response.set_cookie(key="access_token", value=access_token)
        active_id = caching.get("active:id").decode('utf-8')
        redirect_response.set_cookie(key="active_id", value=active_id)
        return redirect_response
    return templates.TemplateResponse("login.html", {"request": request, "title": "WebSocket Example"})


@rest_router.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "WebSocket Example"})


@rest_router.post("/register")
async def register_post(crypto: str = Form(...), tg_tag: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(REGISTER_URL,
                                json={"crypto": crypto, "tg_tag": tg_tag, "password": password}) as response:
            data = await response.json()
            if data.get("status"):
                return RedirectResponse("/login", status_code=303)


@rest_router.post("/login")
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


@rest_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if request.cookies.get("access_token"):
        item_name = caching.get("active:name").decode('utf-8')
        img_link = caching.get("active:img_link").decode('utf-8')
        return templates.TemplateResponse("index.html",
                                          {"request": request, "item_name": item_name, "img_link": img_link})
    else:
        return RedirectResponse(url="/login")



