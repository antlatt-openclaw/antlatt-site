#!/usr/bin/env python3
"""
storage.py - Qdrant storage for sources and chunks
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue, MatchText
)
from qdrant_client.http.exceptions import UnexpectedResponse

from .config import (
    QDRANT_URL, SOURCES_COLLECTION, CHUNKS_COLLECTION, EMBEDDING_DIM
)


def get_client() -> QdrantClient:
    """Get Qdrant client."""
    return QdrantClient(url=QDRANT_URL)


def init_collections():
    """Initialize Qdrant collections."""
    client = get_client()
    
    # Sources collection (no vectors, just metadata)
    try:
        client.get_collection(SOURCES_COLLECTION)
    except UnexpectedResponse:
        client.create_collection(
            collection_name=SOURCES_COLLECTION,
            vectors_config=VectorParams(
                size=1,  # Dummy size for metadata-only
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {SOURCES_COLLECTION}")
    
    # Chunks collection (with vectors)
    try:
        client.get_collection(CHUNKS_COLLECTION)
    except UnexpectedResponse:
        client.create_collection(
            collection_name=CHUNKS_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {CHUNKS_COLLECTION}")


def store_source(
    url: str,
    title: str,
    source_type: str,
    raw_content: str,
    content_hash: str,
    tags: List[str] = None,
    summary: str = None
) -> str:
    """Store a source document. Returns source_id."""
    client = get_client()
    source_id = str(uuid.uuid4())
    
    # Check for duplicate by content_hash
    existing = client.scroll(
        collection_name=SOURCES_COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="content_hash", match=MatchValue(value=content_hash))]
        ),
        limit=1
    )
    
    if existing[0]:
        raise ValueError(f"Duplicate content detected (hash: {content_hash[:12]}...)")
    
    # Store source
    point = PointStruct(
        id=source_id,
        vector=[0.0],  # Dummy vector
        payload={
            "url": url,
            "title": title or "",
            "source_type": source_type,
            "raw_content": raw_content,
            "content_hash": content_hash,
            "tags": tags or [],
            "summary": summary or "",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    )
    
    client.upsert(collection_name=SOURCES_COLLECTION, points=[point])
    return source_id


def store_chunk(
    source_id: str,
    chunk_index: int,
    content: str,
    embedding: List[float],
    embedding_provider: str = "auto"
) -> str:
    """Store a chunk with embedding. Returns chunk_id."""
    client = get_client()
    chunk_id = str(uuid.uuid4())
    
    point = PointStruct(
        id=chunk_id,
        vector=embedding,
        payload={
            "source_id": source_id,
            "chunk_index": chunk_index,
            "content": content,
            "embedding_provider": embedding_provider,
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    client.upsert(collection_name=CHUNKS_COLLECTION, points=[point])
    return chunk_id


def get_source(source_id: str) -> Optional[Dict[str, Any]]:
    """Get source by ID."""
    client = get_client()
    try:
        result = client.retrieve(collection_name=SOURCES_COLLECTION, ids=[source_id])
        if result:
            return {"id": result[0].id, **result[0].payload}
    except:
        pass
    return None


def get_source_by_hash(content_hash: str) -> Optional[Dict[str, Any]]:
    """Get source by content hash."""
    client = get_client()
    results = client.scroll(
        collection_name=SOURCES_COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="content_hash", match=MatchValue(value=content_hash))]
        ),
        limit=1
    )
    if results[0]:
        return {"id": results[0][0].id, **results[0][0].payload}
    return None


def search_chunks(
    query_embedding: List[float],
    limit: int = 10,
    min_score: float = 0.3
) -> List[Dict[str, Any]]:
    """Search chunks by embedding similarity."""
    client = get_client()
    
    result = client.query_points(
        collection_name=CHUNKS_COLLECTION,
        query=query_embedding,
        limit=limit * 3,  # Get extra for dedup
        score_threshold=min_score
    )
    
    results = result.points
    
    # Deduplicate by source_id (keep best score)
    seen_sources = set()
    deduped = []
    
    for r in results:
        source_id = r.payload.get("source_id")
        if source_id and source_id not in seen_sources:
            seen_sources.add(source_id)
            deduped.append({
                "chunk_id": str(r.id),
                "source_id": source_id,
                "content": r.payload.get("content", "")[:2500],
                "chunk_index": r.payload.get("chunk_index"),
                "score": r.score
            })
            
            if len(deduped) >= limit:
                break
    
    return deduped


def list_sources(limit: int = 50, source_type: str = None) -> List[Dict[str, Any]]:
    """List all sources."""
    client = get_client()
    
    query_filter = None
    if source_type:
        query_filter = Filter(
            must=[FieldCondition(key="source_type", match=MatchValue(value=source_type))]
        )
    
    results, _ = client.scroll(
        collection_name=SOURCES_COLLECTION,
        scroll_filter=query_filter,
        limit=limit,
        with_payload=True
    )
    
    return [{"id": r.id, **r.payload} for r in results]


def delete_source(source_id: str):
    """Delete a source and all its chunks."""
    client = get_client()
    
    # Delete chunks
    client.delete(
        collection_name=CHUNKS_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="source_id", match=MatchValue(value=source_id))]
        )
    )
    
    # Delete source
    client.delete(collection_name=SOURCES_COLLECTION, points_selector=[source_id])


def get_stats() -> Dict[str, int]:
    """Get collection stats."""
    client = get_client()
    
    stats = {}
    
    try:
        info = client.get_collection(SOURCES_COLLECTION)
        stats["sources"] = info.points_count
    except:
        stats["sources"] = 0
    
    try:
        info = client.get_collection(CHUNKS_COLLECTION)
        stats["chunks"] = info.points_count
    except:
        stats["chunks"] = 0
    
    return stats