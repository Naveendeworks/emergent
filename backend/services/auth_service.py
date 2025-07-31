from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import os
from asyncpg import Pool

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-make-it-strong")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hashed password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user against database"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT password_hash FROM users WHERE username = $1",
                    username
                )
                if row is None:
                    return False
                return self.verify_password(password, row['password_hash'])
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.PyJWTError:
            return None