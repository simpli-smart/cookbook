# Qwen3-TTS on Simplismart

Code examples and a sample app for running [Qwen3-TTS-12Hz-1.7B-CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) via a Simplismart deployment.

Deploy the model at [simplismart.ai/marketplace](https://simplismart.ai/marketplace), then set your endpoint URL and auth token in `.env`.

## Setup

```bash
cp .env.example .env
# Fill in QWEN_TTS_BASE_URL and QWEN_TTS_AUTH_TOKEN
pip install -r requirements.txt
```

## Examples

| File | What it shows |
|---|---|
| `client.py` | Sync HTTP streaming — simplest working client |
| `async_http_client.py` | Async HTTP streaming with aiohttp |
| `websocket.py` | WebSocket client — stream sentences in, receive audio back |
| `app.py` | Flask demo app with a browser UI, history, and instruction presets |

## Sample App

```bash
python app.py
# Open http://localhost:5000
```

The demo app lets you pick a speaker, language, and instruction preset, play audio in the browser, and view generation history with TTFB metrics.

## Integrations

- [LiveKit guide](https://docs.simplismart.ai/guides/livekit) — wire the TTS endpoint into a LiveKit voice agent
- [Pipecat](https://github.com/simpli-smart/pipecat-simplismart) — `pip install pipecat-simplismart` for Pipecat-based pipelines
