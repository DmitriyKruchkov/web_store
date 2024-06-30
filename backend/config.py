import os

# app
TIME_INTERVAL = int(os.getenv("TIME_INTERVAL", 10))

# connections:
# auth service connection
AUTH_HOST = os.getenv("AUTH_HOST", "127.0.0.1")
AUTH_PORT = int(os.getenv("AUTH_PORT", 11000))

# crypto service connection
CRYPTO_HOST = os.getenv("CRYPTO_HOST", "127.0.0.1")
CRYPTO_PORT = int(os.getenv("CRYPTO_PORT", "5000"))

# database connection
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.1.9")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# S3 connection
S3_HOST = os.getenv("S3_HOST", "192.168.1.9")
S3_PORT = os.getenv("S3_PORT", 9000)
ACCESS_KEY = os.getenv("ACCESS_KEY", "newAccessKey")
SECRET_KEY = os.getenv("SECRET_KEY", "newSecretKey")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "items")

# settings:
origins = [
    "*",  # заменить на адрес контейнера
]

S3_CONFIG = {
    "aws_access_key_id": ACCESS_KEY,
    "aws_secret_access_key": SECRET_KEY,
    "endpoint_url": f"http://{S3_HOST}:{S3_PORT}"
}
