import threading
import hashlib
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    print("WARNING: sentence-transformers not found. Using deterministic fallback for Python 3.13 compatibility.")
    HAS_TRANSFORMERS = False

class EmbeddingService:
    _instance = None
    _model = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_model(cls):
        if cls._model is None and HAS_TRANSFORMERS:
            with cls._lock:
                if cls._model is None:
                    print("Loading SentenceTransformer('all-mpnet-base-v2') singleton...")
                    cls._model = SentenceTransformer("all-mpnet-base-v2")
                    print("Model loaded successfully.")
        return cls._model

    def generate_embedding(self, text: str) -> List[float]:
        if not text.strip():
            return [0.0] * 768
            
        if HAS_TRANSFORMERS:
            model = self.get_model()
            embedding_ndarray = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding_ndarray.tolist()
        else:
            # Deterministic fallback for local Python 3.13 environments without C-compilers
            # Create a 768-dim vector using seeded hashing of the text words
            words = text.lower().split()
            vector = [0.0] * 768
            for i, word in enumerate(words):
                # Hash the word to get a consistent index and value
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = h % 768
                val = ((h % 100) / 100.0) - 0.5
                vector[idx] += val
            
            # Normalize vector to simulate cosine similarity properly
            magnitude = sum(x*x for x in vector) ** 0.5
            if magnitude > 0:
                vector = [x / magnitude for x in vector]
            return vector

# Global singleton instance
embedding_service = EmbeddingService()
