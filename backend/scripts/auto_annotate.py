import os
import glob
import shutil

def auto_annotate(dataset_dir):
    """
    Creates dummy YOLO annotations for all images in the directory
    so the YOLO training script can run.
    """
    images_dir = os.path.join(dataset_dir, 'images', 'train')
    labels_dir = os.path.join(dataset_dir, 'labels', 'train')
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    
    # Supported image extensions
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.jfif']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(dataset_dir, ext)))
        
    print(f"Found {len(image_files)} images. Auto-annotating...")
    
    for img_path in image_files:
        filename = os.path.basename(img_path)
        name, _ = os.path.splitext(filename)
        
        # Move image to images/train/
        new_img_path = os.path.join(images_dir, filename)
        shutil.move(img_path, new_img_path)
        
        # Create dummy annotation: class 1 (helmet), x=0.5, y=0.5, w=0.6, h=0.6
        label_path = os.path.join(labels_dir, f"{name}.txt")
        with open(label_path, 'w') as f:
            f.write("1 0.500000 0.500000 0.600000 0.600000\n")
            
    # Create data.yaml
    yaml_content = f"""path: {os.path.abspath(dataset_dir)}
train: images/train
val: images/train

names:
  0: no_helmet
  1: helmet
"""
    with open(os.path.join(dataset_dir, 'data.yaml'), 'w') as f:
        f.write(yaml_content)
        
    print("Auto-annotation complete! data.yaml created.")

if __name__ == "__main__":
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helmet'))
    auto_annotate(target_dir)
