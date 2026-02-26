from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

ALGORITHM = "RS256"
ACCESS_EXPIRE_MINUTES = 60
REFRESH_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_rs256_keys() -> tuple[str, str]:
    settings = get_settings()
    if settings.jwt_private_key_path and settings.jwt_public_key_path:
        with open(settings.jwt_private_key_path) as f:
            private_key = f.read()
        with open(settings.jwt_public_key_path) as f:
            public_key = f.read()
        return private_key, public_key
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    private_key_obj = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_key_obj = private_key_obj.public_key()
    public_key = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_key, public_key


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    private_key, _ = _get_rs256_keys()
    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    private_key, _ = _get_rs256_keys()
    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    _, public_key = _get_rs256_keys()
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
