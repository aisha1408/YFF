"""
Inference engine module for the Sustainable Pesticide & Fertilizer Recommendation System.
Coordinates image processing, model inference, and result formatting.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
import logging
from .image_ingest import ImageValidator
from .model_loader import ModelLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InferenceEngine:
    """Main inference engine that coordinates the detection pipeline."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the inference engine with all required components."""
        self.image_validator = ImageValidator(config_path)
        self.model_loader = ModelLoader(config_path)
        self.config_path = config_path
        
        # Load configuration
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process an uploaded image through the complete inference pipeline.
        
        Args:
            file_content: Raw image file bytes
            filename: Original filename
            
        Returns:
            Dictionary containing detection results and metadata
        """
        try:
            # Step 1: Validate image
            validation_result = self.image_validator.validate_file(file_content, filename)
            logger.info(f"Image validation passed: {validation_result['width']}x{validation_result['height']}")
            
            # Step 2: Preprocess image
            processed_image = self.image_validator.preprocess_image(file_content)
            logger.info(f"Image preprocessed to shape: {processed_image.shape}")
            
            # Step 3: Run inference
            disease_id, disease_name, confidence, heatmap_base64 = self.model_loader.predict(processed_image)
            logger.info(f"Prediction: {disease_name} (confidence: {confidence:.3f})")
            
            # Step 4: Format results
            result = {
                "disease": {
                    "id": disease_id,
                    "name": disease_name,
                    "confidence": confidence
                },
                "image_metadata": {
                    "width": validation_result['width'],
                    "height": validation_result['height'],
                    "aspect_ratio": validation_result['aspect_ratio'],
                    "file_size_mb": validation_result['file_size_mb'],
                    "format": validation_result['format']
                },
                "supporting_heatmap_base64": heatmap_base64,
                "model_info": {
                    "mock_mode": self.model_loader.is_mock_mode(),
                    "confidence_threshold": self.config['model']['confidence_threshold']
                }
            }
            
            # Add warning if present
            if validation_result.get('warning'):
                result["warning"] = validation_result['warning']
            
            return result
            
        except Exception as e:
            logger.error(f"Inference pipeline failed: {str(e)}")
            raise
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Determine confidence level based on thresholds.
        
        Args:
            confidence: Prediction confidence score
            
        Returns:
            Confidence level string
        """
        low_threshold = self.config['model']['low_confidence_threshold']
        high_threshold = self.config['model']['confidence_threshold']
        
        if confidence >= high_threshold:
            return "high"
        elif confidence >= low_threshold:
            return "medium"
        else:
            return "low"
    
    def should_recommend_treatment(self, confidence: float, disease_id: str) -> bool:
        """
        Determine if treatment should be recommended based on confidence and disease.
        
        Args:
            confidence: Prediction confidence score
            disease_id: Detected disease ID
            
        Returns:
            Boolean indicating if treatment should be recommended
        """
        # Don't recommend treatment for healthy plants
        if disease_id == "healthy":
            return False
        
        # Use confidence threshold for treatment recommendations
        confidence_threshold = self.config['model']['confidence_threshold']
        return confidence >= confidence_threshold
    
    def get_uncertainty_message(self, confidence: float, disease_id: str) -> Optional[str]:
        """
        Generate uncertainty message for low-confidence predictions.
        
        Args:
            confidence: Prediction confidence score
            disease_id: Detected disease ID
            
        Returns:
            Uncertainty message or None
        """
        if disease_id == "healthy":
            return None
        
        low_threshold = self.config['model']['low_confidence_threshold']
        
        if confidence < low_threshold:
            return (
                f"Low confidence detection ({confidence:.1%}). "
                "Consider additional scouting or confirmatory tests before treatment."
            )
        
        return None
