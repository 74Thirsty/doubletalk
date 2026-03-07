from fastapi import Header, HTTPException

from src.config import ADMIN_API_KEY


def require_admin_key(x_admin_key: str = Header(default='')) -> None:
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail='Unauthorized')
