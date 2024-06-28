import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.1.9")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 11000))
