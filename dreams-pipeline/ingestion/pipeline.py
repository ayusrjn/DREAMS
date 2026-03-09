import uuid
from datetime import datetime
from typing import Optional
import logging

from models.memory import Memory
from ingestion.extractors.scene import SceneExtractor
from ingestion.extractors.emotion import EmotionScoreExtractor

logger = logging.getLogger(__name__)

# Initialize extractors globally to avoid loading models on every function call
_scene_extractor = SceneExtractor()
_emotion_extractor = EmotionScoreExtractor()

def process_memory(
    image_path: str,
    user_id: str,
    timestamp: datetime,
    caption: Optional[str] = None,
    memory_id: Optional[str] = None
) -> Memory:
    """
    Processes an image and an optional caption through required extractors
    to generate a populated Memory dataclass instance.
    """
    memory_id = memory_id or str(uuid.uuid4())
    logger.info("Processing memory %s for user %s", memory_id, user_id)
    
    # 1. Extract Scene from Image
    scene_label = _scene_extractor.extract_scene(image_path)
    
    # 2. Extract Emotion (VAD) from caption
    vad = None
    if caption:
        vad = _emotion_extractor.extract_vad(caption)
        
    # 3. Create and return the Memory object
    return Memory(
        memory_id=memory_id,
        user_id=user_id,
        timestamp=timestamp,
        image_path=image_path,
        caption=caption,
        scene_label=scene_label,
        vad=vad,
        # Placeholder for future extractors
        gps=None,
        image_embedding=None,
        caption_embedding=None
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_image = "data/synthetic-data/images/hospital_providence.png"
    test_caption = "Starting my new treatment plan today. Feeling exhausted."
    
    memory_result = process_memory(
        image_path=test_image,
        user_id="user_123",
        timestamp=datetime.utcnow(),
        caption=test_caption
    )
    
    print("\nGenerated Memory Dataclass Instance:")
    print(memory_result)
