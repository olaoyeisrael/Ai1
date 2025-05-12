from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, ask, auth

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Tutor Backend Ready"}
