import logging

logger = logging.getLogger(__name__)

class HelmetDetector:
    """Secondary YOLO model specifically for detecting helmets on cropped head regions."""
    
    def __init__(self, model_path='helmet_model.pt', confidence=0.45):
        self.confidence = confidence
        self.model = None
        self.model_path = model_path
        self._load_model()
        
    def _load_model(self):
        try:
            from ultralytics import YOLO
            import os
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                logger.info(f"Helmet model loaded successfully: {self.model_path}")
            else:
                logger.warning(f"Helmet model not found at {self.model_path}. Will assume all riders have no helmet for demo purposes.")
                self.model = None
        except Exception as e:
            logger.warning(f"Failed to load Helmet model: {e}")
            self.model = None

    def is_available(self):
        return self.model is not None

    def detect_helmet(self, cropped_frame):
        """
        Analyzes a cropped frame for the presence of a helmet.
        Returns: True if helmet detected, False if no helmet detected.
        """
        if self.model is None or cropped_frame is None or cropped_frame.size == 0:
            # Fallback if no model exists: return False (triggering a violation) for demo purposes.
            return False

        results = self.model(cropped_frame, conf=self.confidence, verbose=False)
        
        for result in results:
            if result.probs is not None:
                top1_class_id = result.probs.top1
                class_name = result.names[top1_class_id].lower()
                
                # Check if the predicted class is a helmet
                if 'helmet' in class_name and 'no' not in class_name and 'without' not in class_name:
                    return True
                    
        return False
