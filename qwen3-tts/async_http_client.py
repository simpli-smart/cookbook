"""Streaming TTS client using HTTP streaming (not WebSocket)."""
import asyncio
import aiohttp
import wave
from pathlib import Path

# Same configuration as client2.py
# Try the endpoint from config.py which the Flask app uses
BASE_URL = "https://YOUR-SIMPLISMART-ENDPOINT"
AUTH_TOKEN = "YOUR-AUTH-TOKEN"

TEXT = "Hello world. This is a streaming test. Goodbye."
LANGUAGE = "English"
SPEAKER = "Aiden"
LEADING_SILENCE = True
OUTPUT_WAV = "test_ws_sentences.wav"

SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # PCM16


async def stream_tts():
    """Stream TTS audio using HTTP streaming with aiohttp."""
    url = f"{BASE_URL}/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "audio/L16",
        "Content-Type": "application/json",
    }
    payload = {
        "text": TEXT,
        "language": LANGUAGE,
        "speaker": SPEAKER,
        "leading_silence": LEADING_SILENCE,
    }

    chunks = []
    first_chunk_time = None

    async with aiohttp.ClientSession() as session:
        print(f"Connecting to {url}...")
        t0 = asyncio.get_event_loop().time()

        async with session.post(url, json=payload, headers=headers) as resp:
            print(f"Response status: {resp.status}")
            resp.raise_for_status()

            # Stream chunks as they arrive
            chunk_count = 0
            async for chunk in resp.content.iter_chunked(4096):
                if chunk:
                    if first_chunk_time is None:
                        first_chunk_time = asyncio.get_event_loop().time() - t0
                    chunks.append(chunk)
                    chunk_count += 1
                    print(f"Received chunk {chunk_count}: {len(chunk)} bytes")

    print(f"\nTotal chunks received: {chunk_count}")

    # Combine PCM data
    pcm_data = b"".join(chunks)
    print(f"Total PCM data: {len(pcm_data)} bytes")

    # Create WAV file
    out = Path(OUTPUT_WAV)
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm_data)

    # Calculate metrics
    duration_s = len(pcm_data) / (SAMPLE_RATE * SAMPLE_WIDTH)
    ttfc_ms = (first_chunk_time or 0.0) * 1000

    print(f"\nSaved: {out.absolute()}")
    print(f"Duration: {duration_s:.2f}s")
    print(f"Time to first chunk: {ttfc_ms:.2f}ms")

    return out


if __name__ == "__main__":
    output_file = asyncio.run(stream_tts())
    print(f"\nAudio saved to: {output_file}")
