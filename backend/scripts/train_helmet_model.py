import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_helmet_model(dataset_dir, epochs=50, imgsz=224, base_model='yolov8n-cls.pt'):
    """
    Train a specialized YOLOv8 CLASSIFICATION model for cropped helmet images.
    
    Expected Dataset structure:
    dataset_dir/
       train/
          Helmet/
          Person_no_helmet/
          no_person/
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("ultralytics is not installed. Please run: pip install ultralytics")
        return

    if not os.path.exists(os.path.join(dataset_dir, 'train')):
        logger.error(f"Train folder not found in dataset: {dataset_dir}")
        return

    logger.info(f"Loading classification base model {base_model}...")
    model = YOLO(base_model)

    logger.info(f"Starting classification training on dataset {dataset_dir} for {epochs} epochs...")
    results = model.train(
        data=dataset_dir,
        epochs=epochs,
        imgsz=imgsz,
        project='runs',
        name='helmet_classifier',
        device='', 
    )
    
    logger.info("Training complete!")
    logger.info("Your best model weights are saved in: runs/helmet_classifier/weights/best.pt")
    logger.info("Please copy 'best.pt' to your root directory as 'helmet_model.pt' to use it in the system.")

if __name__ == "__main__":
    # Pointing directly to the folder containing 'train'
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helmet', 'Helmet_Dataset'))
    train_helmet_model(dataset_dir, epochs=50)
