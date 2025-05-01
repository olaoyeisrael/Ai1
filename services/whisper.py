# import whisper

# def transcribe_audio(filepath):
#     model = whisper.load_model("base")
#     result = model.transcribe(filepath)
#     return result['text']

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3"

def transcribe_audio(filepath: str) -> str:
    """
    Transcribes audio at given filepath using Hugging Face's Whisper Large v3.
    Returns the transcribed text.
    """
    if not HF_API_KEY:
        raise ValueError("HF_API_KEY not found in .env")

    # Detect content-type from file extension
    ext = os.path.splitext(filepath)[-1].lower()
    content_types = {
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".m4a": "audio/x-m4a"
    }
    content_type = content_types.get(ext, "application/octet-stream")

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": content_type
    }

    with open(filepath, "rb") as f:
        data = f.read()

    response = requests.post(HF_MODEL_URL, headers=headers, data=data)

    if response.status_code != 200:
        print("❌ HF Whisper Error:", response.text)
        raise Exception("Whisper transcription failed")

    return response.json().get("text", "No transcription returned")