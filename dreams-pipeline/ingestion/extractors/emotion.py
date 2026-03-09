from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

# Standard mapping of the 7 Ekman-like emotions to a continuous VAD space [0, 1]
# Values approximate the classical circumplex model of affect.
EMOTION_VAD_MAPPING = {
    "anger":    {"v": 0.167, "a": 0.865, "d": 0.657},
    "disgust":  {"v": 0.052, "a": 0.775, "d": 0.317},
    "fear":     {"v": 0.073, "a": 0.840, "d": 0.293},
    "joy":      {"v": 0.980, "a": 0.824, "d": 0.794},
    "neutral":  {"v": 0.500, "a": 0.500, "d": 0.500},
    "sadness":  {"v": 0.052, "a": 0.288, "d": 0.164},
    "surprise": {"v": 0.875, "a": 0.875, "d": 0.562}
}

class EmotionScoreExtractor:
    """
    Extracts emotional tone from text and returns a continuous 
    Valence, Arousal, Dominance (VAD) vector.
    """
    def __init__(self):
        try:
            # We use top_k=None to get the probabilities for all 7 emotion classes
            self.classifier = pipeline(
                "text-classification", 
                model="j-hartmann/emotion-english-distilroberta-base", 
                top_k=None
            )
            logger.info("Emotion model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.classifier = None

    def extract_vad(self, text: str) -> dict:
        """
        Runs the classifier on the provided text and computes a VAD vector 
        by weighting the VAD coordinates by their respective emotion probabilities.
        """
        if not text or not str(text).strip() or self.classifier is None:
            return {"v": 0.5, "a": 0.5, "d": 0.5}

        try:
            results = self.classifier(text)
            
            # The pipeline with top_k=None can return a list of lists or a flat list.
            scores = results[0] if isinstance(results[0], list) else results

            weighted_v = 0.0
            weighted_a = 0.0
            weighted_d = 0.0
            
            for item in scores:
                label = item["label"]
                prob = item["score"]
                
                vad = EMOTION_VAD_MAPPING.get(label, {"v": 0.5, "a": 0.5, "d": 0.5})
                weighted_v += vad["v"] * prob
                weighted_a += vad["a"] * prob
                weighted_d += vad["d"] * prob

            return {
                "v": round(weighted_v, 4),
                "a": round(weighted_a, 4),
                "d": round(weighted_d, 4)
            }
        except Exception as e:
            logger.error(f"Error computing VAD vector: {e}")
            return {"v": 0.5, "a": 0.5, "d": 0.5}

# Example usage
if __name__ == "__main__":
    extractor = EmotionScoreExtractor()
    sample_text = "I am so incredibly happy with this result but a little scared for the future!"
    vad = extractor.extract_vad(sample_text)
    print(f"Input: {sample_text}")
    print(f"VAD Vector: {vad}")
