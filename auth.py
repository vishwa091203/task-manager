from jose import jwt
from datetime import datetime, timedelta
import os
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_token(data: dict):
    token_data = data.copy()
    token_data["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
def decode_token(token): return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
