from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt          # for creating JWT token
from datetime import datetime, timedelta
from backend.config import DEMO_USERS, SECRET_KEY, TOKEN_EXPIRE_HOURS


router = APIRouter()

# ── Request model ──────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

# ── Login endpoint ─────────────────────────────────────────
@router.post("/login")
def login(request: LoginRequest):
	# add these at start of function
	username = request.username
	password = request.password
	
	
	if username in DEMO_USERS:
		stored_password, role = DEMO_USERS[username]
		if stored_password == password:
			token = jwt.encode(
				{"role": role, "sub": username, "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)},
				SECRET_KEY,
				algorithm="HS256"
			)
			return {"token": token, "role": role}
		else :
			raise HTTPException(status_code=401, detail="Invalid credentials")
	else:
		raise HTTPException(status_code=401, detail="Please login, new user")