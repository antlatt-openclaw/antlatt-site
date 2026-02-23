# Kokoro TTS

Local text-to-speech using Kokoro container on Proxmox.

## Endpoint

```
http://192.168.1.204:8880
```

OpenAI-compatible API at `/v1/audio/speech`.

## Usage

```bash
# Basic TTS
python3 skills/tts/scripts/kokoro.py "Hello, this is a test."

# Specify voice
python3 skills/tts/scripts/kokoro.py "Hello!" --voice af_bella

# Save to file
python3 skills/tts/scripts/kokoro.py "Save this" --output audio.mp3

# List voices
python3 skills/tts/scripts/kokoro.py --list-voices
```

## Voices

- `af_nova` — default, warm female
- `af_bella` — younger, energetic female
- `am_michael` — deep male
- `bf_emma` — British female
- `am_adam` — professional male

Full list: `curl http://192.168.1.204:8880/v1/audio/voices`

## API Reference

```python
POST /v1/audio/speech
{
  "model": "kokoro",
  "voice": "af_nova",
  "input": "Text to speak",
  "response_format": "mp3"  # mp3, wav, opus, aac, flac
}
```