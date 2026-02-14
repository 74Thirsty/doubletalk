from fastapi import Header, HTTPException


ADMIN_KEY = 'changeme'


def require_admin_key(x_admin_key: str = Header(default='')) -> None:
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail='Unauthorized')
