from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Tuple, List

@dataclass
class Memory:
    """
    Represents a single user memory entry.
    """
    memory_id: str
    user_id: str
    timestamp: datetime
    image_path: str
    caption: Optional[str] = None
    scene_label: Optional[str] = None
    vad: Optional[Dict[str, float]] = None
    gps: Optional[Tuple[float, float]] = None
    image_embedding: Optional[List[float]] = None
    caption_embedding: Optional[List[float]] = None
