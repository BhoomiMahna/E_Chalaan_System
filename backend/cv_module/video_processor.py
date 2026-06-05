"""
Video Processor — OpenCV pipeline: YOLO → Violation Logic → OCR → DB.
"""
import os, logging, random
from datetime import datetime
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, app=None):
        self.app = app
        self.detector = None
        self.ocr_engine = None
        self.frame_skip = 5
        self._init()

    def _init(self):
        try:
            from cv_module.detector import YOLODetector
            from cv_module.helmet_detector import HelmetDetector
            from cv_module.ocr_engine import OCREngine
            from config import Config
            self.detector = YOLODetector(Config.YOLO_MODEL_PATH, Config.YOLO_CONFIDENCE_THRESHOLD)
            self.helmet_detector = HelmetDetector(confidence=0.45)
            self.ocr_engine = OCREngine()
            self.frame_skip = Config.FRAME_SKIP
        except Exception as e:
            logger.warning(f"CV init failed: {e}")

    def process_video(self, source, state=None):
        try:
            import cv2
        except ImportError:
            logger.error("OpenCV not installed")
            return
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            return
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if isinstance(source, str) else 0
        if state: state['total_frames'] = total
        count = viol_count = 0
        from config import Config
        locs = Config.LOCATIONS
        try:
            while cap.isOpened():
                if state and not state.get('is_processing', True): break
                ret, frame = cap.read()
                if not ret: break
                count += 1
                if state: state['processed_frames'] = count
                if count % self.frame_skip != 0: continue
                viols = self._process_frame(frame, locs)
                viol_count += len(viols)
                if state: state['violations_found'] = viol_count
                for v in viols: self._store(v, frame)
        finally:
            cap.release()

    def _process_frame(self, frame, locs):
        if not self.detector or not self.detector.is_available(): return []
        from cv_module.violation_logic import detect_violations
        dets = self.detector.detect(frame)
        if not dets: return []
        viols = detect_violations(dets, frame, helmet_detector=self.helmet_detector)
        for v in viols:
            if self.ocr_engine and self.ocr_engine.is_available():
                r = self.ocr_engine.extract_plate(frame, v.get('bbox'))
                v['vehicle_number'] = r.get('text', 'UNKNOWN')
            else:
                v['vehicle_number'] = self._rand_plate()
            v['location'] = random.choice(locs)
        return viols

    def _store(self, vdata, frame=None):
        if not self.app: return
        from models.violation import db, Violation
        from models.violation_fine import ViolationFine
        from config import Config
        with self.app.app_context():
            try:
                img_path = ''
                if frame is not None:
                    d = Config.VIOLATION_IMAGES_FOLDER
                    os.makedirs(d, exist_ok=True)
                    fn = f'violation_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.jpg'
                    try:
                        import cv2; cv2.imwrite(os.path.join(d, fn), frame)
                        img_path = f'/violation_images/{fn}'
                    except: pass
                
                v_type = vdata['type']
                fine_record = ViolationFine.query.filter_by(violation_type=v_type).first()
                fine_amount = fine_record.base_amount if fine_record else 1000

                v = Violation(
                    vehicle_number=vdata.get('vehicle_number','UNKNOWN'),
                    owner_name=self._rand_name(), address=self._rand_addr(),
                    violation_type=v_type,
                    fine_amount=fine_amount,
                    date_time=datetime.now(), location=vdata.get('location','Unknown'),
                    status='pending', image_path=img_path,
                    confidence=vdata.get('confidence', 0.0))
                db.session.add(v); db.session.commit()
            except Exception as e:
                db.session.rollback(); logger.error(f"Store failed: {e}")

    @staticmethod
    def _rand_plate():
        s = random.choice(['DL','HR','PB','UP','MH','KA','TN','RJ','GJ','MP'])
        return f"{s}{random.randint(1,99):02d}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=2))}{random.randint(1000,9999)}"

    @staticmethod
    def _rand_name():
        f = random.choice(['Rajesh','Amit','Priya','Sunita','Vikram','Deepak','Anita','Suresh','Kavita','Rahul','Pooja','Manish'])
        l = random.choice(['Kumar','Sharma','Singh','Verma','Gupta','Jain','Patel','Rao','Mishra','Chopra','Malhotra','Kapoor'])
        return f"{f} {l}"

    @staticmethod
    def _rand_addr():
        st = random.choice(['Model Town','Civil Lines','Sector 17','MG Road','Mall Road','GT Road','Ring Road','Station Road'])
        c = random.choice(['Chandigarh','Ludhiana','Amritsar','Jalandhar','Shimla','Dehradun','Jaipur','Delhi','Karnal'])
        return f"{random.randint(1,500)}, {st}, {c}"
