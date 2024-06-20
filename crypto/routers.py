from fastapi import APIRouter

from utils import check_balance
from schemas import Wallet, WalletBalance

router = APIRouter()


@router.get("/get_balance", response_model=WalletBalance)
async def get_balance(wallet: Wallet):
    balance = await check_balance(wallet.address)
    return {"balance": balance}
    # return {"balance": float(1000)}
