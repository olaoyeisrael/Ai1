# import whisper

# def transcribe_audio(filepath):
#     model = whisper.load_model("base")
#     result = model.transcribe(filepath)
#     return result['text']

from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
load_dotenv()
import mimetypes

client = InferenceClient( provider="hf-inference", api_key=os.getenv("HF_API_KEY"))
def transcribe_audio(filepath: str) -> str:
    """
    Uses HF InferenceClient with openai/whisper-large-v3.
    Passes binary bytes to avoid 502 and input errors.
    """
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "audio/ogg"
        with open(filepath, "rb") as f:
            audio_bytes = f.read()  # ✅ this is required

        response = client.automatic_speech_recognition(
            audio_bytes,
            model="openai/whisper-large-v3-turbo",
            content_type=mime_type
        )
        return response["text"]
    except Exception as e:
        print("❌ Whisper transcription failed:", e)
        return ""

