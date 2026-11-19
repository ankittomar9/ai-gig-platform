import os
import httpx
from typing import Optional, Dict, Any
from app.database import get_settings

LOCAL_WHISPER_ENDPOINT = os.getenv("WHISPER_ENDPOINT", "http://localhost:8178/inference")
LOCAL_WHISPER_HEALTH = "http://localhost:8178/health"

async def check_whisper_status() -> Dict[str, Any]:
    """Check if local whisper-sidecar or Groq Whisper is accessible"""
    settings = get_settings()
    groq_key = os.getenv("GROQ_API_KEY", "") or settings.get("groq_api_key", "")
    gemini_key = settings.get("gemini_api_key", "")

    # Check local whisper sidecar
    is_local_online = False
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(LOCAL_WHISPER_HEALTH)
            if r.status_code == 200:
                is_local_online = True
    except Exception:
        is_local_online = False

    return {
        "local_whisper_online": is_local_online,
        "local_endpoint": LOCAL_WHISPER_ENDPOINT,
        "groq_whisper_available": bool(groq_key),
        "gemini_available": bool(gemini_key),
        "web_speech_supported": True # Always supported in Chrome/Edge browsers
    }

async def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcribes audio bytes:
    1. Tries local whisper-sidecar (port 8178)
    2. Tries Groq Whisper API (whisper-large-v3-turbo)
    3. Returns error or fallback instructions
    """
    settings = get_settings()
    groq_key = os.getenv("GROQ_API_KEY", "") or settings.get("groq_api_key", "")

    # 1. Try local whisper.cpp sidecar
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            files = {"file": (filename, audio_bytes, "audio/wav")}
            resp = await client.post(LOCAL_WHISPER_ENDPOINT, files=files)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("text", "").strip()
    except Exception:
        pass

    # 2. Try Groq Whisper (ultra-fast 150ms transcription)
    if groq_key:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"Authorization": f"Bearer {groq_key}"}
                files = {"file": (filename, audio_bytes, "audio/wav")}
                data = {"model": "whisper-large-v3-turbo"}
                resp = await client.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
                if resp.status_code == 200:
                    result = resp.json()
                    return result.get("text", "").strip()
        except Exception:
            pass

    return ""
