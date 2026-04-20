"""
YOLO Detector — YOLOv8 object detection engine for traffic violations.
Detects: person, bicycle, car, motorcycle, bus, truck, traffic light.
Uses ultralytics YOLOv8 with configurable confidence threshold.
"""
import logging

logger = logging.getLogger(__name__)

# COCO class IDs we care about
RELEVANT_CLASSES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck',
    9: 'traffic light'
}


class YOLODetector:
    """YOLOv8-based object detector for traffic scene analysis."""

    def __init__(self, model_path='yolov8n.pt', confidence=0.5):
        """
        Initialize the YOLO detector.
        
        Args:
            model_path: Path to YOLOv8 model weights (auto-downloads if not found)
            confidence: Minimum confidence threshold for detections
        """
        self.confidence = confidence
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """Load YOLOv8 model. Falls back to simulation mode if unavailable."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"YOLOv8 model loaded successfully: {self.model_path}")
        except ImportError:
            logger.warning(
                "ultralytics not installed. Running in simulation mode. "
                "Install with: pip install ultralytics"
            )
            self.model = None
        except Exception as e:
            logger.warning(f"Could not load YOLO model: {e}. Running in simulation mode.")
            self.model = None

    def detect(self, frame):
        """
        Run object detection on a single frame.
        
        Args:
            frame: OpenCV BGR image (numpy array)
            
        Returns:
            List of detections, each containing:
            {
                'class_id': int,
                'class_name': str,
                'confidence': float,
                'bbox': [x1, y1, x2, y2],  # pixel coordinates
                'center': (cx, cy)
            }
        """
        if self.model is None:
            return []

        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                class_id = int(box.cls[0])
                if class_id not in RELEVANT_CLASSES:
                    continue

                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                detections.append({
                    'class_id': class_id,
                    'class_name': RELEVANT_CLASSES[class_id],
                    'confidence': round(conf, 3),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': (int(cx), int(cy))
                })

        return detections

    def is_available(self):
        """Check if the YOLO model is loaded and ready."""
        return self.model is not None
