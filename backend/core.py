import logging

import redis
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from config import origins, REDIS_HOST, REDIS_PORT, DATABASE_URL


app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info("Redis connecting")
logger.info(f"{REDIS_HOST, REDIS_PORT}")
caching = redis.Redis(REDIS_HOST, REDIS_PORT)
logger.info("Redis connected")
logger.info(f"addr db:  {DATABASE_URL}")