from typing import Any

from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from models import ConnectionManager
from core import caching
from utils import check_token, check_balance, set_price_and_owner_to_active

ws_router = APIRouter()
manager = ConnectionManager()


@ws_router.websocket("/ws")
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
