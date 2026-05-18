from pathlib import Path
import sys
import time
import wave

import requests


# =========================
# CONFIG
# =========================
BASE_URL = "https://YOUR-SIMPLISMART-ENDPOINT"


AUTH_TOKEN = "YOUR-AUTH-TOKEN"

TEXT = "Hello, this is an authenticated HTTP TTS request."
LANGUAGE = "English"
SPEAKER = "Aiden"
LEADING_SILENCE = True

OUTPUT_WAV = "output_http_ not_angry.wav"

SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # PCM16


def main() -> None:
    if not AUTH_TOKEN.strip():
        print("Set AUTH_TOKEN in this file before running.", file=sys.stderr)
        sys.exit(2)

    url = f"{BASE_URL.rstrip('/')}/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "audio/L16",
    }
    payload = {
        "text": TEXT,
        "language": LANGUAGE,
        "speaker": SPEAKER,
        "leading_silence": LEADING_SILENCE,
        # "instruct": "angry",
    }

    t0 = time.perf_counter()
    try:
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        detail = str(e)
        if getattr(e, "response", None) is not None:
            try:
                detail += f" | body={e.response.text}"
            except Exception:
                pass
        raise RuntimeError(f"HTTP request failed: {detail}") from e

    chunks: list[bytes] = []
    first_chunk_s = None
    for chunk in resp.iter_content(chunk_size=4096):
        if not chunk:
            continue
        if first_chunk_s is None:
            first_chunk_s = time.perf_counter() - t0
        chunks.append(chunk)

    pcm = b"".join(chunks)
    out = Path(OUTPUT_WAV)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)

    dur_s = len(pcm) / (SAMPLE_RATE * SAMPLE_WIDTH)
    ttfc_ms = (first_chunk_s or 0.0) * 1000
    print(
        f"Saved {out} | bytes={len(pcm)} | duration={dur_s:.2f}s | ttfc={ttfc_ms:.2f}ms"
    )


if __name__ == "__main__":
    main()