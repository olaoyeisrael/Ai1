
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import FastAPI, UploadFile, File, HTTPException

from fastapi import Header, HTTPException, Depends
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()
from app.utils.mongo import users
from pydantic import BaseModel, EmailStr
from datetime import datetime

from bson import ObjectId

class UserOutput(BaseModel):
    id: str                   # User ID (e.g., from MongoDB _id or JWT sub)
    email: EmailStr           # Email address
    role: str                 # Role: "student", "trial", or "admin"
    trial_ends_at: Optional[datetime] = None

def get_token_from_header(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return authorization.split(" ")[1]


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
def decode_jwt(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
       

        student_id = payload.get("student_id", "").lower()

        # Determine actual role
        if student_id == "admin":
            role = "admin"
        elif student_id == "trial":
            role = "trial"
        else:
            role = "student"

      
        if "trial_ends_at" in payload:
            trial_ends_at = datetime.utcfromtimestamp(payload["trial_ends_at"])
        else:
            trial_ends_at = None




        return UserOutput(
            id=payload.get("sub"),
            email=payload.get("email"),
            role=role,
            trial_ends_at=trial_ends_at
        )
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please verify OTP again.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")