import asyncio
import datetime
import threading

import aio_pika
import aiohttp
import pytz
from fastapi import UploadFile
from sqlalchemy import select, not_, and_

from database import SessionLocal
from config import TIME_INTERVAL, S3_CONFIG, AUTH_HOST, AUTH_PORT, CRYPTO_HOST, CRYPTO_PORT, RABBITMQ_HOST, \
    RABBITMQ_PORT, RABBITMQ_LOGIN, RABBITMQ_PASS, QUEUE_NAME
from core import caching, logger
from models.DB_model import Product
from models.S3_model import S3Client

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
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(Product).where(Product.id == int(id))
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if not product.is_sold and product.last_bid < time:
                product.is_sold = 1
                product.sell_counts += 1
                await session.commit()
                await refresh_item()


async def refresh_item(update=False, price=0, owner=''):
    cache = caching.get("active:id")
    if cache and not update:
        return {
            "active:id": cache,
            "active:name": caching.get("active:name").decode('utf-8'),
            "active:img_link": caching.get("active:img_link").decode('utf-8'),
            "active:price": caching.get("active:price").decode('utf-8'),
            "active:owner": caching.get("active:owner").decode('utf-8'),
            "active:last_bid": caching.get("active:last_bid")
        }
    async with SessionLocal() as session:
        answer = None
        async with session.begin():
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz).replace(tzinfo=None)

            stmt = select(Product).where(
                and_(
                    Product.date_of_start < current_time_moscow,
                    not_(Product.is_sold)
                )
            ).order_by(Product.sell_counts)

            result = await session.execute(stmt)
            current_item = result.scalars().first()
            if update and current_item:
                current_item.owner = owner
                current_item.current_price = price
            if current_item:
                caching.set("active:id", str(current_item.id), ex=TIME_INTERVAL // 2)
                caching.set("active:name", str(current_item.name), ex=TIME_INTERVAL // 2)
                caching.set("active:img_link", str(current_item.picture_path), ex=TIME_INTERVAL // 2)
                caching.set("active:price", str(current_item.current_price), ex=TIME_INTERVAL // 2)
                caching.set("active:owner", str(current_item.owner), ex=TIME_INTERVAL // 2)
                caching.set("active:last_bid", str(current_item.last_bid), ex=TIME_INTERVAL // 2)
                answer = {
                    "active:id": str(current_item.id),
                    "active:name": str(current_item.name),
                    "active:img_link": str(current_item.picture_path),
                    "active:price": str(current_item.current_price),
                    "active:owner": str(current_item.owner),
                    "active:last_bid": str(current_item.last_bid)
                }
                await session.commit()
            return answer


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
                moscow_tz = pytz.timezone('Europe/Moscow')
                current_time_moscow = datetime.datetime.now(moscow_tz).replace(tzinfo=None)
                await refresh_item(update=True, price=price, owner=owner)
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
                          date_of_start=datetime.datetime.now(moscow_tz).replace(tzinfo=None),
                          last_bid=datetime.datetime.now(moscow_tz).replace(tzinfo=None))
    async with SessionLocal() as session:
        async with session.begin():
            session.add(new_product)
            await session.commit()


async def send_message_to_rabbitmq(name, price):
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_LOGIN,
        password=RABBITMQ_PASS
    )
    message = f'''Добавлен новый лот!
                Название: {name}
                Начальная цена: {price}'''

    async with connection:
        routing_key = QUEUE_NAME
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=routing_key,
        )
