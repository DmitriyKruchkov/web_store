from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

from database import Base


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
    last_bid = Column(DateTime)
