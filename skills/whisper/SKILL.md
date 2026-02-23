# Groq Whisper Transcription

Fast audio/video transcription using Groq's Whisper API.

## Setup

1. Add your Groq API key to `.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

2. Get an API key at: https://console.groq.com/keys

## Commands

- `transcribe <file>` — Transcribe an audio/video file
- `transcribe <url>` — Transcribe from URL
- `transcribe <file> --summarize` — Transcribe and summarize

## Supported Formats

Audio: mp3, mp4, mpeg, mpga, m4a, wav, webm
Video: mp4, webm (audio extracted automatically)

## Usage

```bash
# Transcribe a file
python3 skills/whisper/scripts/transcribe.py /path/to/audio.mp3

# With summary
python3 skills/whisper/scripts/transcribe.py /path/to/audio.mp3 --summarize

# From URL
python3 skills/whisper/scripts/transcribe.py https://example.com/audio.mp3
```