from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        role = payload.get("role")
        username = payload.get("sub")

        if role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
		
        return {"role": role, "username": username}
		
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")