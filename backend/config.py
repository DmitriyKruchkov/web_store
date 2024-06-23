DATABASE_URL = "sqlite+aiosqlite:///./test.db"

origins = [
    "*",  # заменить на адрес контейнера
]

LOGIN_URL = "http://127.0.0.1:11000/login"
REGISTER_URL = "http://127.0.0.1:11000/register"
AUTH_URL = "http://127.0.0.1:11000/check_token"
CRYPTO_URL = "http://127.0.0.1:5000/get_balance"
TIME_INTERVAL = 10
REDIS_HOST = "192.168.1.9"
REDIS_PORT = 6379