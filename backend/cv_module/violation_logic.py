"""
Violation Logic — Rules engine for classifying traffic violations.
Implements:
  1. Helmet violation: motorcycle + person detected without helmet
  2. Red-light violation: vehicle crosses a line while traffic light is red
Uses IoU (Intersection over Union) for proximity detection.
"""
import logging

logger = logging.getLogger(__name__)


def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union between two bounding boxes.
    Each box is [x1, y1, x2, y2].
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0


def is_person_on_motorcycle(person_det, motorcycle_det, overlap_threshold=0.1):
    """
    Check if a person is riding a motorcycle by checking vertical overlap.
    Person's bottom half should overlap with motorcycle's top half.
    """
    p_box = person_det['bbox']
    m_box = motorcycle_det['bbox']

    # Person should be above or overlapping the motorcycle
    person_bottom = p_box[3]
    moto_top = m_box[1]
    moto_bottom = m_box[3]

    # Check horizontal overlap
    h_overlap = min(p_box[2], m_box[2]) - max(p_box[0], m_box[0])
    if h_overlap <= 0:
        return False

    # Person's lower body should be near motorcycle
    vertical_proximity = abs(person_bottom - moto_top) < (moto_bottom - moto_top) * 0.8

    return vertical_proximity or calculate_iou(p_box, m_box) > overlap_threshold


def check_helmet_region(person_det, frame, helmet_detector):
    """
    Check if the person is wearing a helmet by cropping their head region
    and passing it to a specialized helmet detection model.
    """
    if frame is None or helmet_detector is None:
        # Fallback to violation if no frame or model
        return False
        
    x1, y1, x2, y2 = person_det['bbox']
    
    # Calculate the upper 40% of the person's bounding box (head/shoulder region)
    height = y2 - y1
    head_y2 = y1 + int(height * 0.40)
    
    # Crop the image (ensure bounds are within frame)
    h_frame, w_frame = frame.shape[:2]
    crop_x1, crop_y1 = max(0, x1), max(0, y1)
    crop_x2, crop_y2 = min(w_frame, x2), min(h_frame, head_y2)
    
    # If crop is invalid
    if crop_y2 <= crop_y1 or crop_x2 <= crop_x1:
        return False
        
    cropped_head = frame[crop_y1:crop_y2, crop_x1:crop_x2]
    
    # Run the dedicated helmet detection model
    return helmet_detector.detect_helmet(cropped_head)


def detect_violations(detections, frame=None, red_light_line_y=None, helmet_detector=None):
    """
    Analyze detections to identify traffic violations.
    
    Args:
        detections: List of detection dicts from YOLODetector
        frame: Original frame (for helmet region analysis)
        red_light_line_y: Y-coordinate of the stop line (for red-light violations)
        helmet_detector: Instance of HelmetDetector for 2nd stage processing

    
    Returns:
        List of violation dicts:
        {
            'type': 'no_helmet' | 'red_light',
            'confidence': float,
            'bbox': [x1, y1, x2, y2],
            'details': str
        }
    """
    violations = []

    # Separate detections by class
    persons = [d for d in detections if d['class_name'] == 'person']
    motorcycles = [d for d in detections if d['class_name'] == 'motorcycle']
    bicycles = [d for d in detections if d['class_name'] == 'bicycle']
    vehicles = [d for d in detections if d['class_name'] in ('car', 'motorcycle', 'bus', 'truck')]
    traffic_lights = [d for d in detections if d['class_name'] == 'traffic light']

    # --- Helmet Violation Detection ---
    for moto in motorcycles:
        riders = [p for p in persons if is_person_on_motorcycle(p, moto)]
        for rider in riders:
            has_helmet = check_helmet_region(rider, frame, helmet_detector)
            if not has_helmet:
                violations.append({
                    'type': 'no_helmet',
                    'confidence': round((rider['confidence'] + moto['confidence']) / 2, 3),
                    'bbox': moto['bbox'],  # Use motorcycle bbox for plate detection
                    'details': f"Rider on motorcycle detected without helmet "
                              f"(confidence: {rider['confidence']:.1%})"
                })

    # --- Red Light Violation Detection ---
    if red_light_line_y and traffic_lights:
        # Check if any traffic light is red (simplified: we assume it's red for demo)
        # A real system would classify the light color from the cropped region
        is_red = True  # Simplified for demo

        if is_red:
            for vehicle in vehicles:
                # Check if vehicle has crossed the stop line
                vehicle_front = vehicle['bbox'][3]  # Bottom of bounding box
                if vehicle_front > red_light_line_y:
                    violations.append({
                        'type': 'red_light',
                        'confidence': vehicle['confidence'],
                        'bbox': vehicle['bbox'],
                        'details': f"{vehicle['class_name'].title()} crossed red light "
                                  f"(confidence: {vehicle['confidence']:.1%})"
                    })

    return violations
