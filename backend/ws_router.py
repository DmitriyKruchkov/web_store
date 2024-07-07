from typing import Any

from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from models.WebSocket_model import ConnectionManager
from core import caching
from utils import check_token, check_balance, set_price_and_owner_to_active, refresh_item

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
                    item = await refresh_item()
                    if item:
                        price = float(item["active:price"])
                        new_sum = round(price * (1 + int(percentages) / 100), 2)
                        if have_sum > new_sum:
                            id = int(item["active:id"])
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
