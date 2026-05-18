"""Configuration management for Qwen3-TTS Demo."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Qwen3-TTS API Configuration
QWEN_TTS_BASE_URL = os.getenv("QWEN_TTS_BASE_URL", "")
QWEN_TTS_AUTH_TOKEN = os.getenv("QWEN_TTS_AUTH_TOKEN", "")

# Flask Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Audio Configuration (PCM16 format as per Qwen3-TTS spec)
SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # PCM16

# Supported speakers with descriptions
SPEAKERS = {
    "Vivian": {
        "description": "Bright, slightly edgy young female voice",
        "native_language": "Chinese",
        "gender": "Female",
        "style": "Bright, edgy"
    },
    "Serena": {
        "description": "Warm, gentle young female voice",
        "native_language": "Chinese",
        "gender": "Female",
        "style": "Warm, gentle"
    },
    "Uncle_Fu": {
        "description": "Seasoned male voice with a low, mellow timbre",
        "native_language": "Chinese",
        "gender": "Male",
        "style": "Seasoned, mellow"
    },
    "Dylan": {
        "description": "Youthful Beijing male voice with a clear, natural timbre",
        "native_language": "Chinese (Beijing Dialect)",
        "gender": "Male",
        "style": "Youthful, clear"
    },
    "Eric": {
        "description": "Lively Chengdu male voice with a slightly husky brightness",
        "native_language": "Chinese (Sichuan Dialect)",
        "gender": "Male",
        "style": "Lively, husky"
    },
    "Ryan": {
        "description": "Dynamic male voice with strong rhythmic drive",
        "native_language": "English",
        "gender": "Male",
        "style": "Dynamic, rhythmic"
    },
    "Aiden": {
        "description": "Sunny American male voice with a clear midrange",
        "native_language": "English",
        "gender": "Male",
        "style": "Sunny, clear"
    },
    "Ono_Anna": {
        "description": "Playful Japanese female voice with a light, nimble timbre",
        "native_language": "Japanese",
        "gender": "Female",
        "style": "Playful, nimble"
    },
    "Sohee": {
        "description": "Warm Korean female voice with rich emotion",
        "native_language": "Korean",
        "gender": "Female",
        "style": "Warm, emotional"
    }
}

# Supported languages
LANGUAGES = [
    {"code": "English", "name": "English", "flag": "🇺🇸"},
    {"code": "Chinese", "name": "Chinese (中文)", "flag": "🇨🇳"},
    {"code": "Japanese", "name": "Japanese (日本語)", "flag": "🇯🇵"},
    {"code": "Korean", "name": "Korean (한국어)", "flag": "🇰🇷"},
    {"code": "German", "name": "German (Deutsch)", "flag": "🇩🇪"},
    {"code": "French", "name": "French (Français)", "flag": "🇫🇷"},
    {"code": "Russian", "name": "Russian (Русский)", "flag": "🇷🇺"},
    {"code": "Portuguese", "name": "Portuguese (Português)", "flag": "🇵🇹"},
    {"code": "Spanish", "name": "Spanish (Español)", "flag": "🇪🇸"},
    {"code": "Italian", "name": "Italian (Italiano)", "flag": "🇮🇹"}
]

# Instruction presets for quick selection
INSTRUCTION_PRESETS = [
    {"name": "None", "value": ""},
    {"name": "Excited", "value": "Speak in an excited, enthusiastic tone"},
    {"name": "Calm", "value": "Speak calmly and soothingly"},
    {"name": "Professional", "value": "Speak in a professional, formal manner"},
    {"name": "Friendly", "value": "Speak in a warm, friendly, conversational tone"},
    {"name": "Sad", "value": "Speak with a hint of sadness in your voice"},
    {"name": "Angry", "value": "Speak with controlled anger and frustration"},
    {"name": "Whisper", "value": "Speak in a soft whisper, barely audible"},
    {"name": "Narrator", "value": "Speak like a documentary narrator, clear and engaging"},
    {"name": "Storyteller", "value": "Speak like a storyteller, with rhythm and expression"}
]


def validate_config() -> list[str]:
    """Validate configuration and return list of errors."""
    errors = []
    if not QWEN_TTS_AUTH_TOKEN:
        errors.append("QWEN_TTS_AUTH_TOKEN is not set. Please set it in your environment or .env file.")
    if not QWEN_TTS_BASE_URL:
        errors.append("QWEN_TTS_BASE_URL is not set.")
    return errors
