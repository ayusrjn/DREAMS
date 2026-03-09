import os
import urllib.request
import torch
from torchvision import models, transforms
from PIL import Image
from torch.nn import functional as F
import logging

logger = logging.getLogger(__name__)

# Constants for Places365 ResNet50
MODEL_URL = 'http://places2.csail.mit.edu/models_places365/resnet50_places365.pth.tar'
CATEGORIES_URL = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'

class SceneExtractor:
    """
    Extracts the scene label from an image using a ResNet50 model pre-trained on Places365.
    """
    def __init__(self, model_dir='models/places365'):
        self.model_dir = model_dir
        self.model_path = os.path.join(self.model_dir, 'resnet50_places365.pth.tar')
        self.categories_path = os.path.join(self.model_dir, 'categories_places365.txt')
        self.classes = []
        
        # Ensure directories exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Download files if they don't exist
        self._download_if_needed(self.categories_path, CATEGORIES_URL)
        self._download_if_needed(self.model_path, MODEL_URL)
        
        # Load classes
        with open(self.categories_path, 'r') as f:
            for line in f:
                # Format is: /a/airfield 0
                scene = line.strip().split(' ')[0][3:] # Skip /x/ prefix
                self.classes.append(scene)
                
        # Load model
        try:
            # ResNet50 for Places365 has 365 classes
            self.model = models.resnet50(num_classes=365)
            checkpoint = torch.load(self.model_path, map_location=lambda storage, loc: storage)
            # Handle DataParallel prefix if present
            state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
            self.model.load_state_dict(state_dict)
            self.model.eval()
            
            # Standard Places365 transforms
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            logger.info("Places365 Scene model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Places365 Scene model: {e}")
            self.model = None

    def _download_if_needed(self, filepath, url):
        """Downloads a file if it doesn't already exist."""
        if not os.path.exists(filepath):
            logger.info(f"Downloading {url} to {filepath}...")
            urllib.request.urlretrieve(url, filepath)
            logger.info("Download complete.")

    def extract_scene(self, image_path: str) -> str:
        """
        Processes an image and returns the most likely scene category.
        """
        if self.model is None or not os.path.exists(image_path):
            return "unknown"
            
        try:
            img = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(img).unsqueeze(0)
            
            with torch.no_grad():
                output = self.model(input_tensor)
                probs = F.softmax(output, dim=1)
                
            top_prob, top_idx = probs.topk(1)
            predicted_class = self.classes[top_idx.item()]
            
            return predicted_class
        except Exception as e:
            logger.error(f"Error predicting scene for {image_path}: {e}")
            return "unknown"
