"""Flask backend for Qwen3-TTS Interactive Demo."""

import io
import json
import time
import wave
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, Response, jsonify, render_template, request, send_file
from flask_cors import CORS

from config import (
    CHANNELS,
    FLASK_DEBUG,
    FLASK_HOST,
    FLASK_PORT,
    INSTRUCTION_PRESETS,
    LANGUAGES,
    OUTPUTS_DIR,
    QWEN_TTS_AUTH_TOKEN,
    QWEN_TTS_BASE_URL,
    SAMPLE_RATE,
    SAMPLE_WIDTH,
    SPEAKERS,
    validate_config,
)

app = Flask(__name__)
CORS(app)

# History storage
HISTORY_FILE = OUTPUTS_DIR / "history.json"


def load_history() -> list[dict]:
    """Load generation history from JSON file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list[dict]) -> None:
    """Save generation history to JSON file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_to_history(entry: dict) -> None:
    """Add a new entry to history."""
    history = load_history()
    history.insert(0, entry)  # Add to beginning
    # Keep only last 50 entries
    history = history[:50]
    save_history(history)


@app.route("/")
def index():
    """Render the main UI."""
    config_errors = validate_config()
    return render_template(
        "index.html",
        speakers=SPEAKERS,
        languages=LANGUAGES,
        instruction_presets=INSTRUCTION_PRESETS,
        config_errors=config_errors,
        has_token=bool(QWEN_TTS_AUTH_TOKEN),
    )


@app.route("/api/speakers")
def get_speakers():
    """Return list of available speakers."""
    return jsonify(SPEAKERS)


@app.route("/api/languages")
def get_languages():
    """Return list of supported languages."""
    return jsonify(LANGUAGES)


@app.route("/api/history")
def get_history():
    """Return generation history."""
    return jsonify(load_history())


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    """Clear generation history."""
    save_history([])
    return jsonify({"status": "cleared"})


@app.route("/api/outputs/<path:filename>")
def serve_output(filename):
    """Serve generated audio files."""
    file_path = OUTPUTS_DIR / filename
    if file_path.exists():
        return send_file(file_path, mimetype="audio/wav")
    return jsonify({"error": "File not found"}), 404


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    """Generate speech from text using Qwen3-TTS API."""
    data = request.get_json()

    # Validate request
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    language = data.get("language", "English")
    speaker = data.get("speaker", "Aiden")
    instruct = data.get("instruct", "")
    leading_silence = data.get("leading_silence", True)
    stream_mode = data.get("stream", True)

    # Validate config
    config_errors = validate_config()
    if config_errors:
        return jsonify({"error": config_errors[0]}), 500

    # Prepare API request
    url = f"{QWEN_TTS_BASE_URL.rstrip('/')}/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {QWEN_TTS_AUTH_TOKEN}",
        "Accept": "audio/L16",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "language": language,
        "speaker": speaker,
        "leading_silence": leading_silence,
    }
    if instruct:
        payload["instruct"] = instruct
        print(f"[DEBUG] Adding instruct: {instruct}")
    else:
        print("[DEBUG] No instruct provided")
    
    print(f"[DEBUG] Full payload: {payload}")

    try:
        # Make request to Qwen API
        t0 = time.perf_counter()
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=300,
        )
        resp.raise_for_status()

        # Collect audio chunks
        chunks = []
        first_chunk_time = None
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                if first_chunk_time is None:
                    first_chunk_time = time.perf_counter() - t0
                chunks.append(chunk)

        # Combine PCM data
        pcm_data = b"".join(chunks)

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(pcm_data)

        wav_buffer.seek(0)
        wav_data = wav_buffer.read()

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_text = "".join(c for c in text[:30] if c.isalnum() or c.isspace()).strip().replace(" ", "_")
        filename = f"{timestamp}_{speaker}_{safe_text}.wav"
        file_path = OUTPUTS_DIR / filename

        with open(file_path, "wb") as f:
            f.write(wav_data)

        # Calculate metrics
        duration = len(pcm_data) / (SAMPLE_RATE * SAMPLE_WIDTH)
        ttfc_ms = (first_chunk_time or 0.0) * 1000

        # Add to history
        history_entry = {
            "id": timestamp,
            "filename": filename,
            "text": text,
            "language": language,
            "speaker": speaker,
            "instruct": instruct,
            "duration": round(duration, 2),
            "ttfc_ms": round(ttfc_ms, 2),
            "timestamp": datetime.now().isoformat(),
            "size_bytes": len(wav_data),
        }
        add_to_history(history_entry)

        # Return audio file
        wav_buffer.seek(0)
        return send_file(
            wav_buffer,
            mimetype="audio/wav",
            as_attachment=False,
            download_name=filename,
        )

    except requests.RequestException as e:
        error_detail = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail += f" | {e.response.text}"
            except Exception:
                pass
        return jsonify({"error": f"TTS API request failed: {error_detail}"}), 502

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/tts/stream", methods=["POST"])
def text_to_speech_stream():
    """Stream speech generation from Qwen3-TTS API."""
    data = request.get_json()

    # Validate request
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    language = data.get("language", "English")
    speaker = data.get("speaker", "Aiden")
    instruct = data.get("instruct", "")
    leading_silence = data.get("leading_silence", True)

    # Validate config
    config_errors = validate_config()
    if config_errors:
        return jsonify({"error": config_errors[0]}), 500

    # Prepare API request
    url = f"{QWEN_TTS_BASE_URL.rstrip('/')}/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {QWEN_TTS_AUTH_TOKEN}",
        "Accept": "audio/L16",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "language": language,
        "speaker": speaker,
        "leading_silence": leading_silence,
    }
    if instruct:
        payload["instruct"] = instruct

    def generate():
        """Generator function for streaming response."""
        chunks = []
        t0 = time.perf_counter()
        first_chunk_time = None

        try:
            with requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=300,
            ) as resp:
                resp.raise_for_status()

                for chunk in resp.iter_content(chunk_size=4096):
                    if chunk:
                        if first_chunk_time is None:
                            first_chunk_time = time.perf_counter() - t0
                        chunks.append(chunk)
                        yield chunk

            # Save complete file after streaming
            pcm_data = b"".join(chunks)
            if pcm_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_text = "".join(c for c in text[:30] if c.isalnum() or c.isspace()).strip().replace(" ", "_")
                filename = f"{timestamp}_{speaker}_{safe_text}.wav"
                file_path = OUTPUTS_DIR / filename

                # Create WAV file
                with wave.open(str(file_path), "wb") as wav_file:
                    wav_file.setnchannels(CHANNELS)
                    wav_file.setsampwidth(SAMPLE_WIDTH)
                    wav_file.setframerate(SAMPLE_RATE)
                    wav_file.writeframes(pcm_data)

                # Calculate metrics
                duration = len(pcm_data) / (SAMPLE_RATE * SAMPLE_WIDTH)
                ttfc_ms = (first_chunk_time or 0.0) * 1000

                # Add to history
                history_entry = {
                    "id": timestamp,
                    "filename": filename,
                    "text": text,
                    "language": language,
                    "speaker": speaker,
                    "instruct": instruct,
                    "duration": round(duration, 2),
                    "ttfc_ms": round(ttfc_ms, 2),
                    "timestamp": datetime.now().isoformat(),
                    "size_bytes": len(pcm_data) + 44,  # + WAV header
                }
                add_to_history(history_entry)

        except requests.RequestException as e:
            error_msg = f"Error: {str(e)}".encode()
            yield error_msg

    # Return streaming response with WAV header first, then PCM data
    def wav_stream():
        """Stream WAV file with proper headers."""
        # First, we need to collect all data to create proper WAV headers
        # For true streaming, we'd need to estimate or use a different format
        # Here we'll buffer and send as a complete WAV
        pcm_chunks = []
        for chunk in generate():
            if chunk.startswith(b"Error:"):
                yield chunk
                return
            pcm_chunks.append(chunk)

        pcm_data = b"".join(pcm_chunks)

        # Create WAV in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(pcm_data)

        wav_buffer.seek(0)
        yield wav_buffer.read()

    return Response(
        wav_stream(),
        mimetype="audio/wav",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache",
        },
    )


@app.route("/api/config", methods=["GET"])
def get_config():
    """Return public configuration (without sensitive data)."""
    return jsonify({
        "has_token": bool(QWEN_TTS_AUTH_TOKEN),
        "base_url": QWEN_TTS_BASE_URL,
        "sample_rate": SAMPLE_RATE,
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Check if the Qwen TTS API is reachable and responding."""
    config_errors = validate_config()
    if config_errors:
        return jsonify({
            "status": "error",
            "message": config_errors[0],
            "api_reachable": False,
        }), 503

    # Test the Qwen TTS API with a minimal request
    url = f"{QWEN_TTS_BASE_URL.rstrip('/')}/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {QWEN_TTS_AUTH_TOKEN}",
        "Accept": "audio/L16",
        "Content-Type": "application/json",
    }
    # Minimal test payload - just a short word
    payload = {
        "text": "hi",
        "language": "English",
        "speaker": "Aiden",
        "leading_silence": False,
    }

    try:
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=10,  # Short timeout for health check
        )
        resp.raise_for_status()
        # Just read a small amount to confirm it's working
        _ = next(resp.iter_content(chunk_size=1024), None)
        return jsonify({
            "status": "healthy",
            "message": "Qwen TTS API is reachable",
            "api_reachable": True,
        })
    except requests.RequestException as e:
        error_detail = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail += f" | Status: {e.response.status_code}"
            except Exception:
                pass
        return jsonify({
            "status": "error",
            "message": f"TTS API health check failed: {error_detail}",
            "api_reachable": False,
        }), 503


if __name__ == "__main__":
    # Validate config on startup
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease set the required environment variables or create a .env file.")
        print("See .env.example for reference.")

    print(f"Starting Qwen3-TTS Demo on http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
