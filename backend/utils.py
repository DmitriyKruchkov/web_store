import asyncio
import datetime
import threading

import aiohttp
import pytz
from fastapi import UploadFile
from sqlalchemy import select, not_, and_

from database import SessionLocal
from config import TIME_INTERVAL, S3_CONFIG, AUTH_HOST, AUTH_PORT, CRYPTO_HOST, CRYPTO_PORT
from core import caching, logger
from models import Product, S3Client

logger.info("S3 connecting")
logger.info(f"{S3_CONFIG}")
s3_client = S3Client(S3_CONFIG)
logger.info("S3 connected")


async def check_token(access_token: str):
    async with aiohttp.ClientSession() as session:
        request = f"http://{AUTH_HOST}:{AUTH_PORT}/check_token"
        async with session.get(request, json={"access_token": access_token}) as response:
            return await response.json()


async def check_balance(address: str):
    async with aiohttp.ClientSession() as session:
        request = f"http://{CRYPTO_HOST}:{CRYPTO_PORT}/get_balance"
        async with session.get(request, json={"address": address}) as response:
            return await response.json()


async def accept_winner(id, time):
    last_item = caching.get("active:id").decode('utf-8')
    last_bid = caching.get("active:last_bid").decode('utf-8')
    if str(id) == (last_item) and str(time) == str(last_bid):
        async with (SessionLocal() as session):
            async with session.begin():
                stmt = select(Product).where(Product.id == int(id))
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                if not product.is_sold:
                    product.is_sold = 1
                    product.sell_counts += 1
                    await session.commit()
                    await update_current_item()


async def update_current_item(startup=False):
    async with (SessionLocal() as session):
        logger.info("Session connected")
        async with session.begin():
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz).replace(tzinfo=None)
            stmt = select(Product).where(
                and_(
                    Product.date_of_start < current_time_moscow,
                    not_(Product.is_sold)
                )).order_by(Product.sell_counts)

            result = await session.execute(stmt)

            current_item = result.scalars().first()
            if current_item:
                logger.info("Cache creation started")
                caching.set("active:id", str(current_item.id))
                caching.set("active:name", str(current_item.name))
                caching.set("active:img_link", str(current_item.picture_path))
                caching.set("active:price", str(current_item.current_price))
                caching.set("active:owner", str(current_item.owner))
                logger.info("Cache created")


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
                current_time_moscow = datetime.datetime.now(moscow_tz).replace(tzinfo=None)
                caching.set("active:last_bid", str(current_time_moscow))
                threading.Timer(TIME_INTERVAL, run_async_function,
                                args=(accept_winner, id, current_time_moscow)).start()


async def add_new_item(name: str, file: UploadFile, price: float):
    product_link = await s3_client.upload_file(file, "lots")
    moscow_tz = pytz.timezone('Europe/Moscow')
    new_product = Product(name=name,
                          picture_path=product_link,
                          current_price=price,
                          is_sold=0,
                          sell_counts=0,
                          date_of_start=datetime.datetime.now(moscow_tz).replace(tzinfo=None))
    async with SessionLocal() as session:
        async with session.begin():
            session.add(new_product)
            await session.commit()
