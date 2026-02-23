#!/usr/bin/env python3
"""
kokoro.py - Text-to-speech using Kokoro TTS container
"""

import argparse
import os
import sys
from pathlib import Path

import requests

# Load env
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

KOKORO_URL = os.environ.get("KOKORO_URL", "http://192.168.1.204:8880")
DEFAULT_VOICE = os.environ.get("KOKORO_VOICE", "af_nova")
DEFAULT_FORMAT = os.environ.get("KOKORO_FORMAT", "opus")  # opus for Telegram voice messages


def get_voices():
    """Fetch available voices from Kokoro."""
    try:
        resp = requests.get(f"{KOKORO_URL}/v1/audio/voices", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("voices", data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []


def synthesize(text: str, voice: str = DEFAULT_VOICE, output: str = None, 
               model: str = "kokoro", format: str = "mp3"):
    """Synthesize speech from text.
    
    For Telegram voice messages, use format="opus" (OGG/Opus is native format).
    """
    
    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": format
    }
    
    try:
        resp = requests.post(
            f"{KOKORO_URL}/v1/audio/speech",
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        
        audio_data = resp.content
        
        if output:
            Path(output).write_bytes(audio_data)
            return output
        else:
            # Write to temp file and return path for playback
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
                f.write(audio_data)
                return f.name
                
    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Kokoro TTS")
    parser.add_argument("text", nargs="?", help="Text to synthesize")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE, 
                        help=f"Voice to use (default: {DEFAULT_VOICE})")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", default="mp3",
                        choices=["mp3", "wav", "opus", "aac", "flac"],
                        help="Audio format (default: mp3)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List available voices")
    parser.add_argument("--play", "-p", action="store_true",
                        help="Play audio after synthesis (requires mpv/mpg123)")
    
    args = parser.parse_args()
    
    if args.list_voices:
        voices = get_voices()
        print(f"Available voices ({len(voices)}):")
        for v in voices:
            marker = " *" if v == DEFAULT_VOICE else ""
            print(f"  {v}{marker}")
        print(f"\n* = default")
        return
    
    if not args.text:
        print("Error: Provide text to synthesize")
        parser.print_help()
        sys.exit(1)
    
    print(f"Synthesizing with voice={args.voice}...")
    audio_file = synthesize(args.text, voice=args.voice, output=args.output, 
                           format=args.format)
    
    if audio_file:
        print(f"✓ Audio saved to: {audio_file}")
        
        if args.play:
            import subprocess
            for player in ["mpv", "mpg123", "ffplay"]:
                try:
                    subprocess.run([player, audio_file], check=True)
                    break
                except FileNotFoundError:
                    continue
            else:
                print("No audio player found (mpv/mpg123/ffplay)")


if __name__ == "__main__":
    main()