from fastapi import APIRouter, Body, HTTPException
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
from app.utils.mongo import users

router = APIRouter()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

@router.post("/freetrial/register")
def register(email: str = Body(...), password: str = Body(...)):
    if users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = bcrypt.hash(password)
    trial_ends = datetime.utcnow() + timedelta(days=7)

    users.insert_one({
        "email": email,
        "hashed_password": hashed_pw,
        "trial_ends_at": trial_ends,
        "created_at": datetime.utcnow(),
        "role": "trial"
    })

    return {"message": "Account created. Please log in."}



@router.post("/freetrial/login")
def login(email: str = Body(...), password: str = Body(...)):
    user = users.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "exp": int(user["trial_ends_at"].timestamp())
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "token": token,
        "trial_ends_at": user["trial_ends_at"].isoformat()
    }
