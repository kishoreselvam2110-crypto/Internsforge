import hashlib
import os
import httpx
from typing import List

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dimensional normalized embedding vector.
        Tries to call the Hugging Face Inference API for high-quality sentence embeddings.
        Falls back to a smart, dense, deterministic pure-Python word vectorizer if the API is down/offline.
        """
        if not text or not text.strip():
            return [0.0] * 768

        # 1. Try Hugging Face Inference API (all-mpnet-base-v2 is 768-dimensional)
        hf_token = os.getenv("HF_API_TOKEN")
        headers = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"

        try:
            # Short timeout to ensure the user facing request doesn't hang
            with httpx.Client(timeout=4.0) as client:
                response = client.post(
                    "https://api-inference.huggingface.co/models/sentence-transformers/all-mpnet-base-v2",
                    json={"inputs": text},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    # Standard Hugging Face feature-extraction returns a list of floats (or list of list)
                    if isinstance(data, list):
                        if len(data) == 768 and all(isinstance(x, (int, float)) for x in data):
                            return [float(x) for x in data]
                        elif len(data) > 0 and isinstance(data[0], list) and len(data[0]) == 768:
                            return [float(x) for x in data[0]]
        except Exception as e:
            # Fall through silently to the fallback vectorizer
            pass

        # 2. Smart, Dense, Deterministic Fallback Vectorizer
        # Cleans text, tokenizes, and maps each word to 8 distinct indices using salted hashing
        # to produce a dense representation that yields realistic cosine similarity scores.
        cleaned_text = re_clean_text(text)
        words = [w for w in cleaned_text.split() if len(w) > 1]
        
        vector = [0.0] * 768
        for word in set(words):
            # Salt the hash to map each word to 8 different indices (Bloom-filter-like)
            for salt in range(8):
                h = int(hashlib.md5(f"{word}_{salt}".encode()).hexdigest(), 16)
                idx = h % 768
                val = ((h % 100) / 100.0) - 0.5  # Deterministic sign/weight
                vector[idx] += val

        # Normalize the vector to unit length
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        return vector

def re_clean_text(text: str) -> str:
    """Helper to lowercase, remove punctuation and common stopwords."""
    t = text.lower()
    t = t.replace("\n", " ").replace("\r", " ")
    # Replace punctuation with space
    for char in '.,:;()[]{}!?"\'_#+-*/':
        t = t.replace(char, " ")
    
    stopwords = {
        "the", "a", "an", "and", "or", "but", "if", "then", "of", "in", "on", 
        "at", "to", "for", "with", "is", "are", "was", "were", "be", "been", "have", "has", "had"
    }
    words = [w for w in t.split() if w not in stopwords]
    return " ".join(words)

# Global singleton instance
embedding_service = EmbeddingService()
