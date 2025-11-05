from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72


def _ensure_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("Password cannot exceed 72 bytes once encoded.")


def hash_password(password: str) -> str:
    _ensure_password_length(password)
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    _ensure_password_length(password)
    return pwd_context.verify(password, hashed_password)
