import networkx as nx
import logging
from storage.vector_store import VectorStore
from models.memory import Memory

logger = logging.getLogger(__name__)

MAX_SIMILAR_EDGES = 5

def add_semantic_edges(graph: nx.DiGraph, memory: Memory, vector_store: VectorStore) -> None:
    """
    Finds semantically similar memories based on captions and adds directed 
    'SIMILAR_TO' edges connecting the memories in the graph, weighted by distance.
    """
    try:
        similar_matches = vector_store.find_similar(memory.memory_id, top_k=MAX_SIMILAR_EDGES)
        for similar_id, distance in similar_matches:
            if graph.has_node(similar_id):
                graph.add_edge(
                    memory.memory_id,
                    similar_id,
                    edge_type='SIMILAR_TO',
                    weight=distance
                )
    except Exception as e:
        logger.error(f"Failed to add semantic edges for {memory.memory_id}: {e}")

def add_scene_edges(graph: nx.DiGraph, memory: Memory, vector_store: VectorStore) -> None:
    """
    Finds visually/structurally similar memories based on scene predictions and 
    adds directed 'SAME_SCENE' edges connecting the memories in the graph, weighted by distance.
    """
    try:
        similar_matches = vector_store.find_similar_scenes(memory.memory_id, top_k=MAX_SIMILAR_EDGES)
        for similar_id, distance in similar_matches:
            if graph.has_node(similar_id):
                graph.add_edge(
                    memory.memory_id,
                    similar_id,
                    edge_type='SAME_SCENE',
                    weight=distance
                )
    except Exception as e:
        logger.error(f"Failed to add scene edges for {memory.memory_id}: {e}")
