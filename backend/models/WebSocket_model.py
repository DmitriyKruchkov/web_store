import datetime
import math
from typing import List

import pytz
from starlette.websockets import WebSocket

from config import TIME_INTERVAL
from core import caching
from utils import refresh_item


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        item = await refresh_item()

        price = item["active:price"]
        owner = item["active:owner"]
        active_id = item["active:id"].decode("utf-8")
        last_bid = item["active:last_bid"].decode("utf-8")


        if last_bid:
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time_moscow = datetime.datetime.now(moscow_tz)
            last_bid = datetime.datetime.strptime(last_bid, '%Y-%m-%d %H:%M:%S.%f')

            # Присвойте временную зону
            last_bid = last_bid.replace(tzinfo=moscow_tz)

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
        try:
            await websocket.send_json(message)
        except RuntimeError:
            self.disconnect(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                self.disconnect(connection)
