# speech_manager.py
import os
import tempfile
import uuid
import sounddevice as sd
import soundfile as sf
import requests
from dotenv import load_dotenv
import pyttsx3
from typing import Optional

load_dotenv()

ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

def record_audio(duration=4, samplerate=16000, channels=1) -> str:
    """Records a short clip and returns path to WAV file."""
    filename = os.path.join(tempfile.gettempdir(), f"voice_{uuid.uuid4().hex}.wav")
    print(f"[speech_manager] Recording {duration}s -> {filename} (press Ctrl+C to cancel)")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
    sd.wait()
    sf.write(filename, audio, samplerate)
    return filename
