
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.utils.protected import decode_jwt
from services.vector_store import search_chunks
from services.qa import answer_question

router = APIRouter()
chat_sessions = {}

# class UserOutput(BaseModel):
#     id : int
#     first_name: str
#     last_name : str
#     email : EmailStr
#     role: str
class UserOutput(BaseModel):
    id: str
    email: EmailStr
    role: str  # "student", "trial", or "admin"
    trial_ends_at: datetime

class AskInput(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    question: AskInput,
    user: UserOutput = Depends(decode_jwt)
):

    if user.role not in ["student", "trial"]:
        raise HTTPException(status_code=403, detail="Only students and trial users can access.")
   
    if user.role == "trial" and user.trial_ends_at and datetime.utcnow() > user.trial_ends_at:
        raise HTTPException(status_code=403, detail="Free trial expired.")

    user_id = str(user.id)

    if user_id not in chat_sessions:
        chat_sessions[user_id] = [
            {"role": "system", "content": "You are an academic assistant."}
        ]


    top_chunks = search_chunks(question.question, top_k=4, threshold=0.5)
    context = "\n\n".join([chunk['text'] for chunk in top_chunks])

    answer, updated_history = answer_question(
        question.question,
        context,
        chat_sessions[user_id]
    )
   

    chat_sessions[user_id] = updated_history
    print(user.role)
    print(user.trial_ends_at)

    return {
        "question": question.question,
        "answer": answer,
        "search": context
    }