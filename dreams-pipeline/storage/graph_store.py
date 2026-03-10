import networkx as nx
from typing import Optional

class GraphStore:
    def __init__(self):
        self._graphs: dict[str, nx.DiGraph] = {}

    def get_or_create(self, user_id: str) -> nx.DiGraph:
        if user_id not in self._graphs:
            self._graphs[user_id] = nx.DiGraph()
        return self._graphs[user_id]

    def get(self, user_id: str) -> Optional[nx.DiGraph]:
        return self._graphs.get(user_id)

    def all_user_ids(self) -> list[str]:
        return list(self._graphs.keys())
