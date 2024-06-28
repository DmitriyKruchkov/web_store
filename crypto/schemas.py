from pydantic import BaseModel


class Wallet(BaseModel):
    address: str


class WalletBalance(BaseModel):
    balance: float
