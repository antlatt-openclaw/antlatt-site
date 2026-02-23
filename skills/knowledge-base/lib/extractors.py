#!/usr/bin/env python3
"""
extractors.py - Content extraction with fallback chain
"""

import re
import json
import hashlib
import requests
from typing import Optional, Tuple
from urllib.parse import urlparse, urljoin, parse_qs, urlencode

# Try to import optional dependencies
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from readability import Document
    HAS_READABILITY = True
except ImportError:
    HAS_READABILITY = False

from .config import (
    MIN_CONTENT_CHARS, MIN_ARTICLE_CHARS, MIN_PROSE_RATIO,
    MIN_PROSE_LINE_LEN, MAX_CONTENT_CHARS, TRACKING_PARAMS
)


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication."""
    url = url.strip()
    
    # Parse URL
    parsed = urlparse(url)
    
    # Normalize twitter.com to x.com
    if parsed.netloc in ("twitter.com", "www.twitter.com", "mobile.twitter.com"):
        parsed = parsed._replace(netloc="x.com")
    
    # Remove www.
    netloc = parsed.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    parsed = parsed._replace(netloc=netloc)
    
    # Remove tracking params
    query = parse_qs(parsed.query)
    filtered = {k: v for k, v in query.items() if k.lower() not in TRACKING_PARAMS}
    new_query = urlencode(filtered, doseq=True) if filtered else ""
    
    # Remove fragment, trailing slash
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    
    parsed = parsed._replace(query=new_query, fragment="")
    parsed = parsed._replace(path=path)
    
    return parsed.geturl()


def content_hash(content: str) -> str:
    """Generate SHA-256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def detect_type(url: str, filepath: Optional[str] = None) -> str:
    """Detect content type from URL pattern or file extension."""
    if filepath:
        ext = filepath.lower().split('.')[-1] if '.' in filepath else ''
        ext_map = {
            'pdf': 'pdf',
            'txt': 'text',
            'md': 'text',
            'json': 'text'
        }
        return ext_map.get(ext, 'other')
    
    url_lower = url.lower()
    
    # Twitter/X
    if any(x in url_lower for x in ['twitter.com', 'x.com', 't.co']):
        return 'tweet'
    
    # YouTube
    youtube_patterns = ['youtube.com/watch', 'youtu.be/', 'youtube.com/v/', 
                       'youtube.com/embed/', 'youtube.com/shorts/']
    if any(p in url_lower for p in youtube_patterns):
        return 'video'
    
    # PDF
    if url_lower.endswith('.pdf') or 'pdf' in url_lower:
        return 'pdf'
    
    # Default to article
    return 'article'


def validate_content(content: str, source_type: str) -> Tuple[bool, str]:
    """Validate extracted content quality."""
    if not content or len(content.strip()) < MIN_CONTENT_CHARS:
        return False, "Content too short (min 20 chars)"
    
    # Check for error signals (skip for text files, which we control)
    # Only check for error pages in web-extracted content
    if source_type in ('article', 'tweet', 'video'):
        error_signals = [
            "access denied", "captcha", "please enable javascript",
            "cloudflare", "404 not found", "sign in", "blocked", 
            "rate limit", "are you a robot", "verify you are human"
        ]
        content_lower = content.lower()
        signal_count = sum(1 for s in error_signals if s in content_lower)
        if signal_count >= 2:
            return False, f"Error page detected ({signal_count} error signals)"
    
    # Article-specific validation
    if source_type == 'article':
        if len(content) < MIN_ARTICLE_CHARS:
            return False, f"Article too short (min {MIN_ARTICLE_CHARS} chars)"
        
        # Check prose ratio
        lines = [l for l in content.split('\n') if l.strip()]
        if lines:
            prose_lines = sum(1 for l in lines if len(l) >= MIN_PROSE_LINE_LEN)
            ratio = prose_lines / len(lines)
            if ratio < MIN_PROSE_RATIO:
                return False, f"Low prose ratio ({ratio:.1%}, min {MIN_PROSE_RATIO:.0%})"
    
    # Max length
    if len(content) > MAX_CONTENT_CHARS:
        return True, f"Content truncated to {MAX_CONTENT_CHARS} chars"
    
    return True, "Valid"


def extract_tweet(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract tweet content using FxTwitter API with fallbacks."""
    # Extract tweet ID
    match = re.search(r'/status/(\d+)', url)
    if not match:
        return None, None, "Could not extract tweet ID"
    
    tweet_id = match.group(1)
    
    # Try FxTwitter API
    try:
        fx_url = f"https://api.fxtwitter.com/status/{tweet_id}"
        resp = requests.get(fx_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tweet = data.get('tweet', {})
            text = tweet.get('text', '')
            author = tweet.get('author', {}).get('name', '')
            if text:
                return text, author, None
    except Exception as e:
        pass
    
    # Fallback: try nitter
    try:
        nitter_url = f"https://nitter.net/{url.split('/status/')[0].split('/')[-1]}/status/{tweet_id}"
        resp = requests.get(nitter_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and HAS_BS4:
            soup = BeautifulSoup(resp.text, 'html.parser')
            tweet_div = soup.find('div', class_='tweet-content')
            if tweet_div:
                return tweet_div.get_text(strip=True), None, None
    except:
        pass
    
    return None, None, "Could not extract tweet content"


def extract_youtube(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract YouTube video transcript."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None, None, "youtube-transcript-api not installed"
    
    # Extract video ID
    video_id = None
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    elif 'v=' in url:
        video_id = parse_qs(urlparse(url).query).get('v', [None])[0]
    elif '/embed/' in url:
        video_id = url.split('/embed/')[-1].split('?')[0]
    elif '/shorts/' in url:
        video_id = url.split('/shorts/')[-1].split('?')[0]
    
    if not video_id:
        return None, None, "Could not extract YouTube video ID"
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([t['text'] for t in transcript_list])
        
        # Get video title
        try:
            resp = requests.get(f"https://www.youtube.com/oembed?url=https://youtu.be/{video_id}&format=json", timeout=5)
            title = resp.json().get('title', '') if resp.status_code == 200 else ''
        except:
            title = ''
        
        return text, title, None
    except Exception as e:
        return None, None, f"Transcript extraction failed: {e}"


def extract_article(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract article content with fallback chain."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # Try readability first
    if HAS_READABILITY:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                doc = Document(resp.text)
                content = doc.summary()
                title = doc.title()
                
                if HAS_BS4:
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
                else:
                    # Strip HTML tags manually
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                
                if len(content) >= MIN_ARTICLE_CHARS:
                    return content, title, None
        except Exception as e:
            pass
    
    # Fallback: simple extraction
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200 and HAS_BS4:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove script, style, nav, footer
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # Try article tag first
            article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|post|entry'))
            
            if article:
                paragraphs = article.find_all('p')
                content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            else:
                # Fall back to all paragraphs
                paragraphs = soup.find_all('p')
                content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            
            # Get title
            title = soup.find('title')
            title = title.get_text(strip=True) if title else ''
            
            return content, title, None
            
    except Exception as e:
        return None, None, f"Extraction failed: {e}"
    
    return None, None, "All extraction methods failed"


def extract_pdf(filepath: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract text from PDF file."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None, None, "PyMuPDF not installed"
    
    try:
        doc = fitz.open(filepath)
        text = '\n'.join([page.get_text() for page in doc])
        title = doc.metadata.get('title', '') or filepath.split('/')[-1]
        return text, title, None
    except Exception as e:
        return None, None, f"PDF extraction failed: {e}"


def extract_content(url: Optional[str] = None, filepath: Optional[str] = None) -> dict:
    """Main extraction function with type detection and fallback chain."""
    result = {
        'content': None,
        'title': None,
        'source_type': None,
        'error': None,
        'normalized_url': None
    }
    
    # Determine type
    source_type = detect_type(url or '', filepath)
    result['source_type'] = source_type
    
    if url:
        result['normalized_url'] = normalize_url(url)
    
    # Extract based on type
    content, title, error = None, None, None
    
    if filepath and source_type == 'pdf':
        content, title, error = extract_pdf(filepath)
    elif source_type == 'tweet':
        content, title, error = extract_tweet(url)
    elif source_type == 'video':
        content, title, error = extract_youtube(url)
    elif source_type == 'article' or source_type == 'pdf':
        if filepath:
            content, title, error = extract_pdf(filepath)
        else:
            content, title, error = extract_article(url)
    elif filepath:
        # Plain text file
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            title = filepath.split('/')[-1]
        except Exception as e:
            error = str(e)
    
    result['content'] = content
    result['title'] = title
    result['error'] = error
    
    if content and not error:
        # Validate
        valid, msg = validate_content(content, source_type)
        if not valid:
            result['error'] = msg
        elif 'truncated' in msg:
            result['content'] = content[:MAX_CONTENT_CHARS]
            result['warning'] = msg
    
    return result