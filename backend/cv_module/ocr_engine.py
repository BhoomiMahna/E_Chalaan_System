"""
OCR Engine — License plate detection and text extraction using EasyOCR.
Pipeline: Frame → Crop vehicle region → Detect plate contour → Extract text.
"""
import re
import logging
import numpy as np

logger = logging.getLogger(__name__)


class OCREngine:
    """Extracts license plate text from vehicle images using EasyOCR."""

    def __init__(self, languages=None):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes for EasyOCR (default: ['en'])
        """
        self.reader = None
        self.languages = languages or ['en']
        self._initialize()

    def _initialize(self):
        """Load EasyOCR reader. Falls back gracefully if unavailable."""
        try:
            import easyocr
            self.reader = easyocr.Reader(self.languages, gpu=False)
            logger.info("EasyOCR initialized successfully")
        except ImportError:
            logger.warning(
                "easyocr not installed. OCR will return placeholder plates. "
                "Install with: pip install easyocr"
            )
        except Exception as e:
            logger.warning(f"Could not initialize EasyOCR: {e}")

    def extract_plate(self, frame, vehicle_bbox=None):
        """
        Extract license plate text from a frame.
        
        Args:
            frame: OpenCV BGR image (numpy array)
            vehicle_bbox: [x1, y1, x2, y2] bounding box of the vehicle
            
        Returns:
            dict: {
                'text': str (cleaned plate number),
                'confidence': float,
                'raw_results': list (all OCR detections)
            }
        """
        if frame is None:
            return self._empty_result()

        try:
            import cv2
        except ImportError:
            return self._empty_result()

        # Crop to vehicle region if bbox provided
        if vehicle_bbox:
            x1, y1, x2, y2 = vehicle_bbox
            # Focus on lower half of vehicle (where plate usually is)
            plate_region_y1 = y1 + int((y2 - y1) * 0.5)
            cropped = frame[plate_region_y1:y2, x1:x2]
        else:
            cropped = frame

        if cropped.size == 0:
            return self._empty_result()

        # Preprocess for better OCR
        processed = self._preprocess(cropped)

        # Run OCR
        if self.reader is None:
            return self._empty_result()

        try:
            results = self.reader.readtext(processed)
            if not results:
                return self._empty_result()

            # Find the most likely plate text
            best_text = ''
            best_conf = 0.0
            raw_results = []

            for (bbox, text, conf) in results:
                raw_results.append({
                    'text': text,
                    'confidence': conf
                })
                cleaned = self._clean_plate_text(text)
                if cleaned and conf > best_conf:
                    best_text = cleaned
                    best_conf = conf

            return {
                'text': best_text or 'UNKNOWN',
                'confidence': round(best_conf, 3),
                'raw_results': raw_results
            }
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return self._empty_result()

    def _preprocess(self, image):
        """
        Preprocess image for better OCR results.
        Applies: grayscale → bilateral filter → threshold.
        """
        try:
            import cv2
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            # Adaptive threshold for better contrast
            thresh = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            return thresh
        except Exception:
            return image

    def _clean_plate_text(self, text):
        """
        Clean and validate extracted plate text.
        Indian plates follow pattern like: XX00XX0000
        """
        # Remove spaces and special characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', text.upper())

        # Must be at least 4 chars to be a valid plate
        if len(cleaned) < 4:
            return ''

        return cleaned

    def _empty_result(self):
        """Return an empty OCR result."""
        return {
            'text': 'UNKNOWN',
            'confidence': 0.0,
            'raw_results': []
        }

    def is_available(self):
        """Check if OCR engine is ready."""
        return self.reader is not None
