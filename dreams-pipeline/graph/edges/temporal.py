import networkx as nx
from models.memory import Memory

def add_temporal_edge(graph: nx.DiGraph, previous: Memory, current: Memory) -> None:
    """
    Adds a directed 'NEXT' edge between two memories, weighting the edge by the
    time difference (in hours) between them.
    """
    delta_t_hours = (current.timestamp - previous.timestamp).total_seconds() / 3600.0
    graph.add_edge(
        previous.memory_id,
        current.memory_id,
        edge_type='NEXT',
        delta_t=delta_t_hours
    )

def build_temporal_chain(graph: nx.DiGraph, memories: list[Memory]) -> None:
    """
    Sorts a list of memories chronologically and constructs a continuous
    temporal chain by linking each memory to the next.
    """
    if len(memories) < 2:
        return
        
    sorted_memories = sorted(memories, key=lambda m: m.timestamp)
    for i in range(1, len(sorted_memories)):
        add_temporal_edge(graph, sorted_memories[i - 1], sorted_memories[i])
