import datetime
import json
import math
from contextlib import asynccontextmanager
from random import random
from typing import List
import pytz
from aiobotocore.session import get_session
from fastapi import UploadFile
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from starlette.websockets import WebSocket

from database import Base
from core import caching
from config import TIME_INTERVAL


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_price = Column(Float)
    date_of_start = Column(DateTime)
    owner = Column(String)
    picture_path = Column(String)
    is_sold = Column(Boolean)
    sell_counts = Column(Integer)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        price = caching.get("active:price").decode('utf-8')

        owner = caching.get("active:owner").decode('utf-8')

        active_id = caching.get("active:id").decode('utf-8')

        last_bid = caching.get("active:last_bid")
        if last_bid:
            last_bid = last_bid.decode('utf-8')
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz)
            last_bid = datetime.datetime.strptime(last_bid, '%Y-%m-%d %H:%M:%S.%f%z')
            diff = (current_time_moscow - last_bid).total_seconds()
            progress_bar = 100 - math.ceil(diff / TIME_INTERVAL)
            await websocket.send_json(
                {"price": price, "address": owner, "active_id": active_id, "progress_bar": progress_bar})
        else:
            await websocket.send_json(
                {"price": price, "address": owner, "active_id": active_id, "progress_bar": 100})
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


class S3Client:
    def __init__(
            self,
            config: dict

    ):
        self.config = config
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def create_bucket(self, bucket_name):
        async with self.get_client() as client:
            buckets_responce = await client.list_buckets()
            buckets_list = [bucket['Name'] for bucket in buckets_responce['Buckets']]
            if bucket_name not in buckets_list:
                await client.create_bucket(Bucket=bucket_name)

    def create_unique_key(self, object_name, list_of_keys):
        ext = object_name.split(".")[-1]
        len_of_hash = 16
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        new_name = ''.join(random.sample(alphabet, len_of_hash))
        while new_name in list_of_keys:
            new_name = ''.join(random.sample(alphabet, len_of_hash))
        return '.'.join([new_name, ext])

    async def upload_file(self, file: UploadFile, bucket_name, acl: str = "public-read"):
        await self.create_bucket(bucket_name)
        object_name = file.filename.split("/")[-1]
        async with self.get_client() as client:
            list_objects_response = await client.list_objects_v2(Bucket=bucket_name)
            list_of_obj = [i["Key"] for i in list_objects_response.get('Contents', [])]
            key = self.create_unique_key(object_name, list_of_obj)
            file_data = await file.read()
            await client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_data,
                ACL=acl
            )
        link_to_file = "/".join([self.config['endpoint_url'], bucket_name, key])
        return link_to_file
