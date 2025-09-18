"""
Model loading and management module for the Sustainable Pesticide & Fertilizer Recommendation System.
Handles model loading, mock mode, and model configuration.
"""

import os
import yaml
import numpy as np
from typing import Optional, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelLoader:
    """Handles model loading and mock mode operations."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['model']
        self.mock_mode = self.model_config['mock_mode']
        self.model = None
        
        if not self.mock_mode:
            self._load_model()
    
    def _load_model(self):
        """Load the actual model from disk."""
        model_path = self.model_config['path']
        
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found at {model_path}. Switching to mock mode.")
            self.mock_mode = True
            return
        
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
        except ImportError:
            logger.warning("TensorFlow not available. Install with: pip install tensorflow")
            logger.info("Switching to mock mode.")
            self.mock_mode = True
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}. Switching to mock mode.")
            self.mock_mode = True
    
    def predict(self, image_array: np.ndarray) -> Tuple[str, str, float, Optional[str]]:
        """
        Run inference on the image.
        
        Args:
            image_array: Preprocessed image array
            
        Returns:
            Tuple of (disease_id, disease_name, confidence_score, heatmap_base64)
        """
        if self.mock_mode:
            return self._mock_predict()
        else:
            return self._real_predict(image_array)
    
    def _mock_predict(self) -> Tuple[str, str, float, Optional[str]]:
        """Return mock prediction results for testing/demo."""
        # Mock data for demonstration
        mock_results = [
            ("powdery_mildew", "Powdery Mildew", 0.92),
            ("bacterial_spot", "Bacterial Spot", 0.87),
            ("rust", "Rust Disease", 0.78),
            ("healthy", "Healthy Plant", 0.95)
        ]
        
        # Return a random mock result (in real implementation, you might cycle through these)
        import random
        disease_id, disease_name, confidence = random.choice(mock_results)
        
        # Mock heatmap (base64 encoded 1x1 transparent PNG)
        mock_heatmap = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        return disease_id, disease_name, confidence, mock_heatmap
    
    def _real_predict(self, image_array: np.ndarray) -> Tuple[str, str, float, Optional[str]]:
        """Run actual model inference."""
        try:
            # Run prediction
            predictions = self.model.predict(image_array, verbose=0)
            confidence = float(np.max(predictions))
            predicted_class = int(np.argmax(predictions))
            
            # Map class index to disease ID (this would be configured based on your model)
            class_mapping = {
                0: "powdery_mildew",
                1: "bacterial_spot", 
                2: "rust",
                3: "healthy"
            }
            
            disease_id = class_mapping.get(predicted_class, "unknown")
            disease_name = disease_id.replace("_", " ").title()
            
            # Generate Grad-CAM heatmap
            heatmap_base64 = self._generate_gradcam(image_array, predicted_class)
            
            return disease_id, disease_name, confidence, heatmap_base64
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return "unknown", "Unknown", 0.0, None
    
    def _generate_gradcam(self, image_array: np.ndarray, predicted_class: int) -> Optional[str]:
        """Generate Grad-CAM heatmap for explainability."""
        try:
            import tensorflow as tf
            import cv2
            import base64
            from io import BytesIO
            
            # Get the last convolutional layer
            last_conv_layer = None
            for layer in reversed(self.model.layers):
                if len(layer.output_shape) == 4:  # Convolutional layer
                    last_conv_layer = layer
                    break
            
            if last_conv_layer is None:
                return None
            
            # Create a model that outputs the last conv layer and final predictions
            grad_model = tf.keras.models.Model(
                inputs=self.model.inputs,
                outputs=[last_conv_layer.output, self.model.output]
            )
            
            # Compute gradients
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(image_array)
                class_output = predictions[:, predicted_class]
            
            grads = tape.gradient(class_output, conv_outputs)
            
            # Global average pooling of gradients
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            
            # Multiply each channel in the feature map array by its importance
            conv_outputs = conv_outputs[0]
            heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            
            # Normalize heatmap
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = heatmap.numpy()
            
            # Resize heatmap to original image size
            heatmap = cv2.resize(heatmap, (224, 224))
            heatmap = np.uint8(255 * heatmap)
            
            # Apply colormap
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            # Convert to base64
            _, buffer = cv2.imencode('.png', heatmap)
            heatmap_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return heatmap_base64
            
        except ImportError:
            logger.warning("OpenCV not available. Install with: pip install opencv-python")
            return None
        except Exception as e:
            logger.error(f"Grad-CAM generation failed: {str(e)}")
            return None
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self.mock_mode
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and status."""
        return {
            "mock_mode": self.mock_mode,
            "model_loaded": self.model is not None,
            "model_path": self.model_config['path'],
            "input_size": self.model_config['input_size'],
            "confidence_threshold": self.model_config['confidence_threshold']
        }
