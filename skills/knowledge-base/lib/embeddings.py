#!/usr/bin/env python3
"""
embeddings.py - Embedding generation with caching and retries
"""

import time
import hashlib
import requests
from typing import Optional, List
from functools import lru_cache
from .config import (
    GEMINI_API_KEY, OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIM,
    MAX_RETRIES, RETRY_DELAYS, EMBEDDING_CACHE_SIZE
)

# Simple in-memory cache
_embedding_cache = {}


def get_cache_key(text: str, model: str) -> str:
    """Generate cache key for embedding."""
    return hashlib.md5(f"{model}:{text}".encode()).hexdigest()


def embed_gemini(text: str) -> Optional[List[float]]:
    """Generate embedding using Gemini API."""
    if not GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"
    
    try:
        resp = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json={
                "content": {"parts": [{"text": text}]},
                "taskType": "RETRIEVAL_DOCUMENT"
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get('embedding', {}).get('values')
    except Exception as e:
        print(f"Gemini embedding error: {e}")
    
    return None


def embed_openai(text: str) -> Optional[List[float]]:
    """Generate embedding using OpenAI API."""
    if not OPENAI_API_KEY:
        return None
    
    url = "https://api.openai.com/v1/embeddings"
    
    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "text-embedding-3-small",
                "input": text[:8000]  # Max input
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', [{}])[0].get('embedding')
    except Exception as e:
        print(f"OpenAI embedding error: {e}")
    
    return None


def embed_ollama(text: str) -> Optional[List[float]]:
    """Generate embedding using local Ollama."""
    try:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30
        )
        
        if resp.status_code == 200:
            return resp.json().get('embedding')
    except:
        pass
    
    return None


def embed_text(text: str, provider: str = "auto") -> Optional[List[float]]:
    """
    Generate embedding with fallback chain and caching.
    
    Provider options: auto, gemini, openai, ollama
    """
    # Check cache
    text_key = text[:8000]  # Truncate for cache key
    cache_key = get_cache_key(text_key, provider)
    
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]
    
    result = None
    
    if provider == "gemini":
        result = embed_gemini(text)
    elif provider == "openai":
        result = embed_openai(text)
    elif provider == "ollama":
        result = embed_ollama(text)
    else:
        # Auto: try Gemini -> OpenAI -> Ollama
        for p in [embed_gemini, embed_openai, embed_ollama]:
            result = p(text)
            if result:
                break
    
    # Cache result
    if result:
        _embedding_cache[cache_key] = result
        
        # Limit cache size
        if len(_embedding_cache) > EMBEDDING_CACHE_SIZE:
            # Remove oldest entries
            keys = list(_embedding_cache.keys())[:-EMBEDDING_CACHE_SIZE]
            for k in keys:
                del _embedding_cache[k]
    
    return result


def embed_batch(texts: List[str], provider: str = "auto", batch_size: int = 10) -> List[Optional[List[float]]]:
    """Generate embeddings for multiple texts with retry logic."""
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        for text in batch:
            # Retry logic
            embedding = None
            for attempt, delay in enumerate(RETRY_DELAYS):
                embedding = embed_text(text, provider)
                if embedding:
                    break
                if attempt < len(RETRY_DELAYS) - 1:
                    time.sleep(delay)
            
            results.append(embedding)
        
        # Delay between batches
        if i + batch_size < len(texts):
            time.sleep(0.2)
    
    return results


def embed_query(query: str) -> Optional[List[float]]:
    """Embed a search query."""
    return embed_text(query, provider="auto")