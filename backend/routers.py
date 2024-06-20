from fastapi import APIRouter
from sqlalchemy import select
from starlette.responses import RedirectResponse

from models import SessionLocal, Product

rest_router = APIRouter()


@rest_router.get("/active_product")
async def get_active_product():
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(Product).order_by(Product.id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            return {"is_active": product.id, "price": product.current_price}
