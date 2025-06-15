from fastapi import APIRouter, Body, HTTPException
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
from app.utils.mongo import users
from app.utils.mailer import send_email
import random
from datetime import datetime, timedelta, timezone

from bson import ObjectId
datetime.now(timezone.utc)

router = APIRouter()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

@router.post("/freetrial/register")
def register(email: str = Body(...), password: str = Body(...)):
    
    if users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = bcrypt.hash(password)
    trial_ends = datetime.utcnow() + timedelta(days=7)

    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    users.insert_one({
        "email": email,
        "hashed_password": hashed_pw,
        "trial_ends_at": trial_ends,
        "created_at": datetime.utcnow(),
        "role": "trial",
        "otp_code": otp,
        "otp_expires_at": expires
    })
    body = f"<p>Your OTP code is <strong>{otp}</strong>. It expires in 10 minutes.</p>"
    send_email(email, "Welcome to Lextorah AI Tutor – Verify Your Email", body)

    return {"message": "Account created. OTP sent. Please verify to complete registration."}

 

@router.post("/freetrial/login")
def login(email: str = Body(...), password: str = Body(...)):
    email = email.lower().strip()
    user = users.find_one({"email": email})
    
    if not user or not bcrypt.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    users.update_one(
            {"email": email},
            {"$set": {
                "otp_code": otp,
                "otp_expires_at": expires
            }}
        )
    # Send OTP email
        
    body = f"<p>Your OTP code is <strong>{otp}</strong>. It expires in 10 minutes.</p>"
    send_email(email, "Your AI Tutor OTP Code", body)

    raise HTTPException(
            status_code=200,
            detail="OTP sent. Please verify to complete login."
        )

   




@router.post("/api/verify")
def verify_otp(email: str = Body(...), otp: str = Body(...)):
    user = users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    if user.get("otp_code") != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    print(email)

    if datetime.utcnow() > user.get("otp_expires_at", datetime.utcnow()):
        users.update_one({"email": email}, {"$unset": {"otp_code": "", "otp_expires_at": ""}})
        raise HTTPException(status_code=400, detail="OTP expired")

    # ✅ Clear OTP and mark as verified
    users.update_one(
        {"email": email},
        {"$unset": {"otp_code": "", "otp_expires_at": ""}}
    )
    
    # ✅ Return JWT token + trial info
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=3600)
    trial_ends_at = user.get("trial_ends_at")
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "student_id": user["role"],
        "exp": int(expires_at.timestamp()),
        "trial_ends_at": int(trial_ends_at.timestamp())   
     }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


    return {
        "token": token,
        "trial_ends_at": user["trial_ends_at"].isoformat(),
        "email": email,
        "role": user.get("role", "trial"),
     }


    