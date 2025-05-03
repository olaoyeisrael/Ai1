from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.whisper import transcribe_audio
from services.parser import extract_pdf_text
from services.chunker import chunk_text
from services.embedder import embed_chunks, embed_query
from services.vector_store import store_chunks, search_chunks
from services.qa import answer_question
from services.vector_store import print_all_chunks
from services.parser import extract_ppt_text
import os
import shutil
from typing import Dict, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class AskInput(BaseModel):
    question: str

chat_sessions: Dict[str, List[Dict]] = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload")
async def upload_material(file: UploadFile = File(...)):
    try:
        UPLOAD_DIR = "/tmp/uploads"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, file.filename)

        print(f"[DEBUG] Saving to {filepath}")
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        content_type = file.content_type
        filename = file.filename.lower()

        if "audio" in content_type or filename.endswith((".mp3", ".wav", ".mp4")):
            text = transcribe_audio(filepath)
        elif content_type == "application/pdf" or filename.endswith(".pdf"):
            text = extract_pdf_text(filepath)
        elif filename.endswith((".ppt", ".pptx")) or content_type in [
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]:
            text = extract_ppt_text(filepath)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not text or not text.strip():
            raise HTTPException(status_code=422, detail="No text extracted from file.")

        chunks = chunk_text(text)
        store_chunks(chunks)

        return {
            "message": "Material processed and stored",
            "chunks": len(chunks),
            "text": text
        }

    except Exception as e:
        print("❌ Upload crashed:", e)
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@app.post("/api/ask")
async def ask_question(
    question: AskInput):
    user_id = "guest_user" 
    if user_id not in chat_sessions:
        chat_sessions[user_id] = [
            {"role": "system", "content":"You are an academic assistant."}
         ]
    top_chunks = search_chunks(question.question,3, 0.75)

    context = "\n\n".join([chunk['text'] for chunk in top_chunks])
    answer, updated_history = answer_question(question.question, context, chat_sessions[user_id])
 
    chat_sessions[user_id] = updated_history
    print(context)
    return {"question": question, "answer": answer, "search": context}



@app.get("/api/debug/chunks")
def debug_chunks():
    print_all_chunks()
    return {"status": "Printed chunks to console"}


@app.get("/")
def root():
    return {"message": "AI Tutor Backend Ready"}