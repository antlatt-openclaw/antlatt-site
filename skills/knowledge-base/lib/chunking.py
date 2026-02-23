#!/usr/bin/env python3
"""
chunking.py - Text chunking with sentence boundary splits
"""

import re
from typing import List
from .config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE


def split_sentences(text: str) -> List[str]:
    """Split text on sentence boundaries."""
    # Match sentence endings followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[dict]:
    """
    Chunk text into overlapping segments.
    
    Returns list of dicts with 'content', 'start_char', 'end_char'
    """
    if not text:
        return []
    
    sentences = split_sentences(text)
    chunks = []
    current_chunk = ""
    current_start = 0
    char_pos = 0
    sentence_positions = []
    
    # Track sentence positions
    pos = 0
    for s in sentences:
        sentence_positions.append((pos, pos + len(s), s))
        pos += len(s) + 1  # +1 for space
    
    chunk_index = 0
    
    for start_pos, end_pos, sentence in sentence_positions:
        if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                'content': current_chunk.strip(),
                'chunk_index': chunk_index,
                'start_char': current_start,
                'end_char': current_start + len(current_chunk)
            })
            chunk_index += 1
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + " " + sentence
            current_start = end_pos - len(current_chunk)
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
                current_start = start_pos
    
    # Don't forget the last chunk
    if current_chunk and len(current_chunk) >= MIN_CHUNK_SIZE:
        chunks.append({
            'content': current_chunk.strip(),
            'chunk_index': chunk_index,
            'start_char': current_start,
            'end_char': current_start + len(current_chunk)
        })
    elif current_chunk and chunks:
        # Append small remainder to last chunk
        chunks[-1]['content'] += " " + current_chunk.strip()
    
    return chunks