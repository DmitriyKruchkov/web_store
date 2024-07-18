import os

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
QUEUE_NAME = os.getenv("QUEUE_NAME", "telegram_queue")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
API_TOKEN = os.getenv("API_TOKEN", 'telegram-bot-token')
RABBITMQ_LOGIN = os.getenv("RABBITMQ_LOGIN", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "158.160.168.118")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))