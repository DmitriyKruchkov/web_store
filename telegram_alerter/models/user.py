from sqlalchemy import Column, Integer, String

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    chat_id = Column(String)

