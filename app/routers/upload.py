from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, shutil
from app.utils.protected import decode_jwt
from services.whisper import transcribe_audio
from services.parser import extract_pdf_text, extract_ppt_text
from services.chunker import chunk_text
from services.vector_store import store_chunks


router = APIRouter()

@router.post("/upload")
async def upload_material(file: UploadFile = File(...), user: dict = Depends(decode_jwt)):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admins only")
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
