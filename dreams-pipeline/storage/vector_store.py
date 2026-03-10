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
        self._scenes = self._client.get_or_create_collection('scenes')

    def insert_memory(self, memory: Memory) -> None:
        """
        Embeds the memory caption and scene, and upserts them into the vector database into their respective collections.
        """
        encoder = _load_encoder()
        metadata = {'user_id': memory.user_id}
        
        if memory.caption:
            caption_embedding = encoder.encode(memory.caption).tolist()
            self._captions.upsert(
                ids=[memory.memory_id],
                embeddings=[caption_embedding],
                metadatas=[metadata]
            )
            
        if memory.scene_label:
            scene_embedding = encoder.encode(memory.scene_label).tolist()
            self._scenes.upsert(
                ids=[memory.memory_id],
                embeddings=[scene_embedding],
                metadatas=[metadata]
            )

    def find_similar(self, memory_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Retrieves the top_k most similar memories to the given memory_id based on caption embeddings.
        Returns a list of tuples containing (memory_id, distance).
        """
        try:
            query_result = self._captions.get(ids=[memory_id], include=['embeddings'])
            if not query_result or 'embeddings' not in query_result or len(query_result['embeddings']) == 0:
                return []
                
            query_embeddings = query_result['embeddings']
            
            result = self._captions.query(
                query_embeddings=query_embeddings,
                n_results=top_k + 1
            )
            
            matches = []
            for i in range(len(result['ids'][0])):
                mid = result['ids'][0][i]
                if mid != memory_id:
                    distance = result['distances'][0][i] if 'distances' in result and result['distances'] else 0.0
                    matches.append((mid, distance))
            
            return matches[:top_k]
        except Exception as e:
            print(f"Error finding similar memories by caption: {e}")
            return []

    def find_similar_scenes(self, memory_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Retrieves the top_k most similar memories to the given memory_id based on scene embeddings.
        Returns a list of tuples containing (memory_id, distance).
        """
        try:
            query_result = self._scenes.get(ids=[memory_id], include=['embeddings'])
            if not query_result or 'embeddings' not in query_result or len(query_result['embeddings']) == 0:
                return []
                
            query_embeddings = query_result['embeddings']
            
            result = self._scenes.query(
                query_embeddings=query_embeddings,
                n_results=top_k + 1
            )
            
            matches = []
            for i in range(len(result['ids'][0])):
                mid = result['ids'][0][i]
                if mid != memory_id:
                    distance = result['distances'][0][i] if 'distances' in result and result['distances'] else 0.0
                    matches.append((mid, distance))
            
            return matches[:top_k]
        except Exception as e:
            print(f"Error finding similar memories by scene: {e}")
            return []
