const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

const QDRANT_URL = 'http://192.168.1.202:6333';
const COLLECTION = 'kb_chunks';
const OLLAMA_URL = 'http://192.168.1.207:11434';

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Search endpoint
app.post('/search', async (req, res) => {
  try {
    const { query, limit = 10 } = req.body;
    
    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Query required' });
    }

    // Get embedding from Ollama
    const embedResponse = await fetch(`${OLLAMA_URL}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'mxbai-embed-large',
        prompt: query
      })
    });

    if (!embedResponse.ok) {
      throw new Error('Failed to get embedding');
    }

    const embedData = await embedResponse.json();
    const vector = embedData.embedding;

    if (!vector || !Array.isArray(vector)) {
      throw new Error('Invalid embedding response');
    }

    // Search Qdrant
    const searchResponse = await fetch(`${QDRANT_URL}/collections/${COLLECTION}/points/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        vector,
        limit,
        with_payload: true
      })
    });

    if (!searchResponse.ok) {
      throw new Error('Failed to search Qdrant');
    }

    const searchData = await searchResponse.json();
    
    // Transform results
    const results = (searchData.result || [])
      .filter((point) => point.score >= 0.3)
      .map((point) => {
        const payload = point.payload || {};
        return {
          title: payload.title || 'Untitled',
          description: payload.description || payload.content?.slice(0, 200) || '',
          url: payload.url || payload.slug ? `/builds/${payload.slug}` : '/',
          tags: payload.tags || [],
          score: point.score
        };
      });

    res.json({ results });

  } catch (error) {
    console.error('Search API error:', error);
    res.status(500).json({ 
      error: 'Search failed',
      results: [] 
    });
  }
});

app.listen(PORT, () => {
  console.log(`Search API running on port ${PORT}`);
});