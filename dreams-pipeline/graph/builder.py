from models.memory import Memory
from storage.graph_store import GraphStore
from storage.vector_store import VectorStore
from graph.edges.temporal import build_temporal_chain
from graph.edges.semantic import add_semantic_edges, add_scene_edges

class GraphBuilder:
    def __init__(self, graph_store: GraphStore, vector_store: VectorStore):
        self._graph_store = graph_store
        self._vector_store = vector_store

    def build_for_user(self, user_id: str, memories: list[Memory]) -> None:
        """
        Builds a comprehensive memory graph for a single user by adding all 
        memory nodes and linking them via temporal, thematic, and spatial edges.
        """
        graph = self._graph_store.get_or_create(user_id)
        
        # Add all nodes first
        for memory in memories:
            graph.add_node(memory.memory_id, **_memory_to_node_attrs(memory))
            
        # 1. Build temporal edges (chronological timeline)
        build_temporal_chain(graph, memories)
        
        # 2. Build semantic and scene-based edges
        for memory in memories:
            add_semantic_edges(graph, memory, self._vector_store)
            add_scene_edges(graph, memory, self._vector_store)

def _memory_to_node_attrs(memory: Memory) -> dict:
    """Helper formatting function to persist relevant dataclass properties onto graph nodes."""
    return {
        'user_id': memory.user_id,
        'timestamp': memory.timestamp,
        'scene_label': memory.scene_label,
        'valence': memory.vad.get('v') if memory.vad else None,
        'arousal': memory.vad.get('a') if memory.vad else None,
        'dominance': memory.vad.get('d') if memory.vad else None,
        'caption': memory.caption,
    }
