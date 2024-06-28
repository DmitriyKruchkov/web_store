import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

origins = [
    "*",  # заменить на адрес контейнера
]
AUTH_HOST = os.getenv("AUTH_HOST", "127.0.0.1")
AUTH_PORT = int(os.getenv("AUTH_PORT", 11000))
CRYPTO_HOST = os.getenv("CRYPTO_HOST", "127.0.0.1")
CRYPTO_PORT = os.getenv("CRYPTO_PORT", "5000")
TIME_INTERVAL = int(os.getenv("TIME_INTERVAL", 10))
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.1.9")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ACCESS_KEY = os.getenv("ACCESS_KEY", "newAccessKey")
SECRET_KEY = os.getenv("SECRET_KEY", "newSecretKey")
S3_HOST = os.getenv("S3_HOST", "192.168.1.9")
S3_PORT = os.getenv("S3_PORT", 9000)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "items")
S3_CONFIG = {
    "aws_access_key_id": ACCESS_KEY,
    "aws_secret_access_key": SECRET_KEY,
    "endpoint_url": f"http://{S3_HOST}:{S3_PORT}"
}
