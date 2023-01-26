from fastapi import Request, HTTPException, Response
from jose import jwt


SECRET_KEY = "ba0b33e90b425be16a7f6c4cf210d18b1b64d50540bfb706ca7188a9a1c34ff9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user_email(request:Request):
    token = request.cookies.get("access_token")
    
    if token:
        type, space, param = token.partition(" ")
        payload = jwt.decode(
            param, SECRET_KEY, ALGORITHM
        )
        email = payload.get("sub")
    else:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return email


def store_cookie(response: Response, email:str):
    data = {"sub": email}
    jwt_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
