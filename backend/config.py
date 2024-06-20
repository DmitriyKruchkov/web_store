DATABASE_URL = "sqlite+aiosqlite:///./test.db"

origins = [
    "*",  # заменить на адрес контейнера
]

LOGIN_URL = "http://127.0.0.1:11000/login"
AUTH_URL = "http://127.0.0.1:11000/check_token"
CRYPTO_URL = "http://127.0.0.1:5000/get_balance"
