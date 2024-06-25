from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import redis
from config import REDIS_HOST, REDIS_PORT, DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, APP_HOST, \
    APP_PORT

from starlette.middleware.cors import CORSMiddleware


caching = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)




engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    crypto = Column(String, unique=True, index=True)
    tg_tag = Column(String)
    hashed_password = Column(String)
    access_token = Column(String)



Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    crypto: str
    tg_tag: str
    password: str


class UserLogin(BaseModel):
    crypto: str
    password: str


class Token(BaseModel):
    status: bool



class TokenCheck(BaseModel):
    access_token: str


class TokenData(BaseModel):
    access: bool
    crypto: str | None = None


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db: Session, crypto: str):
    return db.query(User).filter(User.crypto == crypto).first()


def authenticate_user(db: Session, crypto: str, password: str):
    user = get_user(db, crypto)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, crypto=user.crypto)
    if db_user:
        raise HTTPException(status_code=400, detail="Wallet already registered")
    hashed_password = get_password_hash(user.password)
    access_token = create_access_token(data={"sub": user.crypto})
    new_user = User(crypto=user.crypto, hashed_password=hashed_password, tg_tag=user.tg_tag, access_token=access_token)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": True}


@app.post("/login", response_model=TokenCheck)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, crypto=user.crypto, password=user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect wallet or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = db_user.access_token
    caching.set(access_token, user.crypto, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"access_token": access_token}


@app.get("/check_token", response_model=TokenData)
async def check_token(token: TokenCheck):
    crypto_user = caching.get(token.access_token)
    if crypto_user:
        return {"access": True, "crypto": crypto_user}
    else:
        return {"access": False, "crypto": None}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
