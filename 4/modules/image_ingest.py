"""
Image validation and preprocessing module for the Sustainable Pesticide & Fertilizer Recommendation System.
Handles file validation, size checks, and image preprocessing for model inference.
"""

import os
import yaml
from PIL import Image
import numpy as np
from typing import Tuple, Optional, Dict, Any

# Define a simple exception class to replace FastAPI's HTTPException
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ImageValidator:
    """Handles image validation and preprocessing."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.image_config = self.config['image']
        self.model_config = self.config['model']
    
    def validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate uploaded file for size, format, and dimensions.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dict with validation results and metadata
            
        Raises:
            ValidationError: If validation fails
        """
        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > self.image_config['max_size_mb']:
            raise ValidationError(
                f"File too large. Maximum size: {self.image_config['max_size_mb']} MB"
            )
        
        # Check file extension
        file_ext = filename.lower().split('.')[-1]
        if file_ext not in self.image_config['supported_formats']:
            raise ValidationError(
                f"Unsupported format. Supported: {', '.join(self.image_config['supported_formats'])}"
            )
        
        try:
            # Load and validate image
            image = Image.open(io.BytesIO(file_content))
            
            # Check dimensions
            width, height = image.size
            min_width, min_height = self.image_config['min_dimensions']
            
            if width < min_width or height < min_height:
                raise ValidationError(
                    f"Image too small. Minimum dimensions: {min_width}x{min_height}"
                )
            
            # Check aspect ratio
            aspect_ratio = width / height
            max_ratio = self.image_config['max_aspect_ratio']
            min_ratio = self.image_config['min_aspect_ratio']
            
            if aspect_ratio > max_ratio or aspect_ratio < min_ratio:
                # Warning but not blocking
                warning = f"Extreme aspect ratio detected: {aspect_ratio:.2f}. Recommended range: {min_ratio}-{max_ratio}"
            else:
                warning = None
            
            return {
                'valid': True,
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio,
                'file_size_mb': file_size_mb,
                'format': file_ext,
                'warning': warning
            }
            
        except Exception as e:
            raise ValidationError(
                f"Invalid image file: {str(e)}"
            )
    
    def preprocess_image(self, file_content: bytes) -> np.ndarray:
        """
        Preprocess image for model inference.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            Preprocessed image array ready for model input
        """
        # Load image
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        target_size = tuple(self.model_config['input_size'])
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32)
        image_array = image_array / 255.0  # Normalize to [0, 1]
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array


# Import io at the top level
import io
