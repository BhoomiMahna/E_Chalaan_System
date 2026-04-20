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


def check_helmet_region(person_det, frame=None):
    """
    Check if the person's head region suggests they are wearing a helmet.
    This is a simplified check — production would use a dedicated helmet classifier.
    
    For the base COCO model, we look at the top portion of the person bounding box.
    Returns True if helmet detected (no violation), False if no helmet (violation).
    
    NOTE: Without a custom helmet detection model, this returns False (violation)
    for demo purposes. Replace with actual classifier for production.
    """
    # In a real system, we'd crop the head region and run a helmet classifier
    # For demo: we flag all motorcycle riders as potential violations
    return False


def detect_violations(detections, frame=None, red_light_line_y=None):
    """
    Analyze detections to identify traffic violations.
    
    Args:
        detections: List of detection dicts from YOLODetector
        frame: Original frame (for helmet region analysis)
        red_light_line_y: Y-coordinate of the stop line (for red-light violations)
    
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
            has_helmet = check_helmet_region(rider, frame)
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
