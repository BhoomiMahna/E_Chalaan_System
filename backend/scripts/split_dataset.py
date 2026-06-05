import os
import shutil
import random
import glob

def split_dataset(dataset_dir, val_split=0.1):
    train_dir = os.path.join(dataset_dir, 'train')
    val_dir = os.path.join(dataset_dir, 'val')
    
    os.makedirs(val_dir, exist_ok=True)
    
    # Get all class folders
    classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
    
    for cls in classes:
        cls_train_dir = os.path.join(train_dir, cls)
        cls_val_dir = os.path.join(val_dir, cls)
        os.makedirs(cls_val_dir, exist_ok=True)
        
        # Get all images in this class
        images = glob.glob(os.path.join(cls_train_dir, '*.*'))
        num_val = max(1, int(len(images) * val_split)) # At least 1 image for val
        
        # Randomly select images to move
        val_images = random.sample(images, num_val)
        for img in val_images:
            shutil.move(img, os.path.join(cls_val_dir, os.path.basename(img)))
            
    print("Dataset split into train and val successfully!")

if __name__ == "__main__":
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helmet', 'Helmet_Dataset'))
    split_dataset(target_dir)
