from fastapi import HTTPException
from starlette.responses import RedirectResponse
from starlette.requests import Request
from database import engine, Base
from utils import update_current_item
from ws_router import ws_router
from routers import rest_router

from core import app


app.include_router(rest_router)
app.include_router(ws_router)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await update_current_item(startup=True)


@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse("/login")


