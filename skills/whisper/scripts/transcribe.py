#!/usr/bin/env python3
"""
transcribe.py - Audio/video transcription using Groq Whisper API
"""

import argparse
import os
import sys
import json
import tempfile
import requests
from pathlib import Path

# Load environment from .env file
def load_env():
    env_path = Path("/root/.openclaw/antlatt-workspace/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

load_env()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}


def check_api_key():
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("ERROR: GROQ_API_KEY not set")
        print("Add your API key to /root/.openclaw/antlatt-workspace/.env")
        print("Get a key at: https://console.groq.com/keys")
        return False
    return True


def download_file(url: str) -> str:
    """Download file from URL to temp location."""
    print(f"Downloading from URL...")
    
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    
    # Get filename from URL or header
    filename = None
    if 'content-disposition' in response.headers:
        cd = response.headers['content-disposition']
        if 'filename=' in cd:
            filename = cd.split('filename=')[1].strip('"')
    
    if not filename:
        filename = url.split('/')[-1].split('?')[0] or "audio.mp3"
    
    # Create temp file
    suffix = Path(filename).suffix or '.mp3'
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    
    with os.fdopen(fd, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Downloaded to {temp_path}")
    return temp_path


def transcribe_file(filepath: str, model: str = "whisper-large-v3-turbo", language: str = None) -> dict:
    """Transcribe audio file using Groq Whisper API."""
    
    path = Path(filepath)
    
    # Check format
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"Warning: {path.suffix} may not be supported. Supported: {SUPPORTED_FORMATS}")
    
    # Check file size (Groq limit is 25MB)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 25:
        print(f"ERROR: File too large ({size_mb:.1f}MB). Groq limit is 25MB.")
        print("Consider splitting the file or using a different service.")
        return None
    
    print(f"Transcribing: {path.name} ({size_mb:.1f}MB)")
    print(f"Model: {model}")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    with open(path, 'rb') as audio_file:
        files = {
            'file': (path.name, audio_file, 'audio/mpeg')
        }
        data = {
            'model': model,
            'response_format': 'verbose_json'
        }
        
        if language:
            data['language'] = language
        
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )
    
    if response.status_code != 200:
        print(f"ERROR: API returned {response.status_code}")
        print(response.text)
        return None
    
    return response.json()


def format_transcript(result: dict) -> str:
    """Format transcription result as readable text."""
    
    text = result.get('text', '')
    
    # Check for segments
    segments = result.get('segments', [])
    
    if segments:
        lines = []
        for seg in segments:
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            seg_text = seg.get('text', '').strip()
            
            # Format timestamp
            start_fmt = f"{int(start//60):02d}:{int(start%60):02d}"
            end_fmt = f"{int(end//60):02d}:{int(end%60):02d}"
            
            lines.append(f"[{start_fmt}-{end_fmt}] {seg_text}")
        
        return '\n'.join(lines)
    
    return text


def summarize_text(text: str) -> str:
    """Summarize transcript (placeholder - would need LLM integration)."""
    # For now, just return key stats
    words = len(text.split())
    lines = len(text.split('\n'))
    
    return f"""
Transcript Summary:
- {words} words
- {lines} segments

[Full summary would require LLM integration]
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video with Groq Whisper")
    parser.add_argument("input", help="File path or URL to transcribe")
    parser.add_argument("--model", default="whisper-large-v3-turbo", 
                        help="Whisper model (default: whisper-large-v3-turbo)")
    parser.add_argument("--language", help="Language code (e.g., 'en', 'es')")
    parser.add_argument("--summarize", action="store_true", help="Summarize after transcription")
    parser.add_argument("--output", "-o", help="Save transcript to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if not check_api_key():
        sys.exit(1)
    
    # Handle URL vs file
    temp_file = None
    try:
        if args.input.startswith('http://') or args.input.startswith('https://'):
            filepath = download_file(args.input)
            temp_file = filepath
        else:
            filepath = args.input
            if not os.path.exists(filepath):
                print(f"ERROR: File not found: {filepath}")
                sys.exit(1)
        
        # Transcribe
        result = transcribe_file(filepath, args.model, args.language)
        
        if result is None:
            sys.exit(1)
        
        # Format output
        if args.json:
            output = json.dumps(result, indent=2)
        else:
            output = format_transcript(result)
            
            if args.summarize:
                output += "\n\n" + summarize_text(result.get('text', ''))
        
        print("\n" + "="*60)
        print(output)
        print("="*60)
        
        # Save to file
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\n✓ Saved to {args.output}")
        
        # Print stats
        duration = result.get('duration', 0)
        print(f"\nDuration: {int(duration//60)}m {int(duration%60)}s")
        
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    main()