import asyncio
import aiohttp
import os
import time

api_key = "SIMPLISMART_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}"
}

async def test_websocket_sentences():
    """Sentence stream: send config, then sentences; receive WAV (header + PCM16) until [DONE]."""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("wss://YOUR-SIMPLISMART-ENDPOINT/ws/tts", headers=headers) as ws:
            async def send_sentences():
                await ws.send_json({"speaker": "Vivian"})
                for s in ["Hello world.", "This is a test.", "Goodbye.", "[DONE]"]:
                    await ws.send_str(s)
                    print(f"Sent: {s!r}")

            async def receive_audio():
                chunks = []
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        chunks.append(msg.data)
                    elif msg.type == aiohttp.WSMsgType.TEXT and msg.data == "[DONE]":
                        break
                return b"".join(chunks)

            _, audio_data = await asyncio.gather(send_sentences(), receive_audio())

            out_path = f"outputs/test_ws_sentences_{time.time()}.wav"
            with open(out_path, "wb") as f:
                f.write(audio_data)
            print(f"Wrote {out_path} ({len(audio_data)} bytes)")


asyncio.run(test_websocket_sentences())