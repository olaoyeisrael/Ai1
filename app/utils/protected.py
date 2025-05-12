
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import FastAPI, UploadFile, File, HTTPException

from fastapi import Header, HTTPException, Depends
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

def get_token_from_header(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return authorization.split(" ")[1]


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
def decode_jwt(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = 'admin' if payload.get("student_id", "").lower() == "admin" else 'student'

        return {
            "user_id": payload.get("id"),
            "role": role,
            "student_id": payload.get("student_id")
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")