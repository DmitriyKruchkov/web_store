from typing import Any

from fastapi import APIRouter, UploadFile, Depends
import aiohttp
from fastapi import Form, HTTPException
from sqlalchemy.future import select
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from utils import check_token, add_new_item, refresh_item
from config import AUTH_HOST, AUTH_PORT
from core import caching, templates


rest_router = APIRouter()




@rest_router.get("/login")
async def login_get(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token and (await check_token(access_token)):
        redirect_response = RedirectResponse(url="/", status_code=303)
        redirect_response.set_cookie(key="access_token", value=access_token)
        return redirect_response
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})


@rest_router.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "WebSocket Example"})


@rest_router.post("/register")
async def register_post(crypto: str = Form(...), tg_tag: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        request = f"http://{AUTH_HOST}:{AUTH_PORT}/register"
        async with session.post(request,
                                json={"crypto": crypto, "tg_tag": tg_tag, "password": password}) as response:
            data = await response.json()
            if data.get("status"):
                return RedirectResponse("/login", status_code=303)


@rest_router.post("/login")
async def login_post(crypto: str = Form(...), password: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        request = f"http://{AUTH_HOST}:{AUTH_PORT}/login"
        async with session.post(request, json={"crypto": crypto, "password": password}) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get("access_token")
                if access_token:
                    redirect_response = RedirectResponse(url="/", status_code=303)
                    redirect_response.set_cookie(key="access_token", value=access_token)
                    item = await refresh_item()
                    if item:
                        redirect_response.set_cookie(key="active_id", value=item["active:id"])
                    else:
                        redirect_response = RedirectResponse(url="/stopped", status_code=303)
                    return redirect_response
                else:
                    raise HTTPException(status_code=401, detail="Invalid token response")
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")


@rest_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if request.cookies.get("access_token"):
        item = await refresh_item()
        if item:
            item_name = item["active:name"]
            img_link = item["active:img_link"]
            return templates.TemplateResponse("index.html",
                                              {"request": request, "item_name": item_name, "img_link": img_link})
        else:
            return RedirectResponse(url="/stopped")
    else:
        return RedirectResponse(url="/login")


@rest_router.get("/new_item")
async def new_item_get(request: Request):
    return templates.TemplateResponse("new_item.html", {"request": request, "title": "WebSocket Example"})


@rest_router.get("/stopped")
async def stopped(request: Request):
    return templates.TemplateResponse("stopped.html", {"request": request})


@rest_router.post("/new_item")
async def new_item_post(
        request: Request,
        item_name: str = Form(...),
        item_image: UploadFile = Form(...),
        price: float = Form(...)
        # access_token: Any = Depends(check_token)
):
    # if access_token:
    await add_new_item(item_name, item_image, price)
    return RedirectResponse(url="/", status_code=303)
    # else:
    #     return RedirectResponse(url="/login", status_code=303)
