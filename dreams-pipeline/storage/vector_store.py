import os
import chromadb
from sentence_transformers import SentenceTransformer
from models.memory import Memory

_encoder = None

def _load_encoder():
    """Loads the sentence transformer encoder globally so it's only loaded once."""
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer('all-MiniLM-L6-v2')
    return _encoder

class VectorStore:
    """
    Handles similarity search and embedding storage for memory captions using ChromaDB.
    """
    def __init__(self, persist_dir: str = None):
        if persist_dir is None:
            # Default to the data directory in the pipeline root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(base_dir, 'data', 'chroma_db')
            
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._captions = self._client.get_or_create_collection('captions')

    def insert_memory(self, memory: Memory) -> None:
        """
        Embeds the memory caption and upserts it into the vector database along with metadata.
        """
        if not memory.caption:
            return
            
        encoder = _load_encoder()
        embedding = encoder.encode(memory.caption).tolist()
        
        # Prepare metadata (chromadb requires metadata values to be str, int, float or bool)
        metadata = {'user_id': memory.user_id}
        if memory.scene_label:
            metadata['scene'] = memory.scene_label
            
        self._captions.upsert(
            ids=[memory.memory_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def find_similar(self, memory_id: str, top_k: int = 5) -> list[str]:
        """
        Retrieves the top_k most similar memories to the given memory_id.
        """
        # Fetch the embedding for the given memory_id
        try:
            query_result = self._captions.get(ids=[memory_id], include=['embeddings'])
            if not query_result or 'embeddings' not in query_result or len(query_result['embeddings']) == 0:
                return []
                
            query_embeddings = query_result['embeddings']
            
            # Query the database
            result = self._captions.query(
                query_embeddings=query_embeddings,
                n_results=top_k + 1 # +1 because it will return itself
            )
            
            # Filter out the original memory_id
            return [mid for mid in result['ids'][0] if mid != memory_id][:top_k]
        except Exception as e:
            print(f"Error finding similar memories: {e}")
            return []
