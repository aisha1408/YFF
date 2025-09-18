"""
Unit tests for image validation and preprocessing module.
"""

import pytest
import io
import numpy as np
from PIL import Image
from modules.image_ingest import ImageValidator, ValidationError


class TestImageValidator:
    """Test cases for ImageValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create ImageValidator instance for testing."""
        return ImageValidator("config.yaml")
    
    @pytest.fixture
    def valid_image_bytes(self):
        """Create valid image bytes for testing."""
        # Create a 300x300 RGB image
        img = Image.new('RGB', (300, 300), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    @pytest.fixture
    def small_image_bytes(self):
        """Create small image bytes for testing."""
        # Create a 100x100 RGB image (below minimum size)
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    @pytest.fixture
    def large_image_bytes(self):
        """Create large image bytes for testing."""
        # Create a large image (simulate > 8MB)
        # For testing, we'll create a smaller image but mock the size check
        img = Image.new('RGB', (500, 500), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_valid_image_validation(self, validator, valid_image_bytes):
        """Test validation of a valid image."""
        result = validator.validate_file(valid_image_bytes, "test.jpg")
        
        assert result['valid'] is True
        assert result['width'] == 300
        assert result['height'] == 300
        assert result['format'] == 'jpg'
        assert result['warning'] is None
    
    def test_invalid_file_extension(self, validator, valid_image_bytes):
        """Test validation with invalid file extension."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(valid_image_bytes, "test.txt")
        
        assert exc_info.value.status_code == 400
        assert "Unsupported format" in exc_info.value.detail
    
    def test_small_image_dimensions(self, validator, small_image_bytes):
        """Test validation with image below minimum dimensions."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(small_image_bytes, "small.jpg")
        
        assert exc_info.value.status_code == 400
        assert "Image too small" in exc_info.value.detail
    
    def test_extreme_aspect_ratio_warning(self, validator):
        """Test warning for extreme aspect ratio."""
        # Create a very wide image
        img = Image.new('RGB', (1000, 100), color='yellow')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        
        result = validator.validate_file(img_bytes.getvalue(), "wide.jpg")
        
        assert result['valid'] is True
        assert result['warning'] is not None
        assert "Extreme aspect ratio" in result['warning']
    
    def test_file_size_validation(self, validator):
        """Test file size validation."""
        # Create a large file (simulate > 8MB)
        large_data = b'x' * (9 * 1024 * 1024)  # 9MB
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(large_data, "large.jpg")
        
        assert exc_info.value.status_code == 400
        assert "File too large" in exc_info.value.detail
    
    def test_image_preprocessing(self, validator, valid_image_bytes):
        """Test image preprocessing for model input."""
        processed = validator.preprocess_image(valid_image_bytes)
        
        # Check shape: should be (1, 224, 224, 3) for batch, height, width, channels
        assert processed.shape == (1, 224, 224, 3)
        
        # Check data type
        assert processed.dtype == np.float32
        
        # Check value range (should be normalized to [0, 1])
        assert processed.min() >= 0.0
        assert processed.max() <= 1.0
    
    def test_rgb_conversion(self, validator):
        """Test conversion of non-RGB images to RGB."""
        # Create a grayscale image
        img = Image.new('L', (300, 300), color=128)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        
        processed = validator.preprocess_image(img_bytes.getvalue())
        
        # Should still be RGB after conversion
        assert processed.shape == (1, 224, 224, 3)
    
    def test_png_image_processing(self, validator):
        """Test processing of PNG images."""
        # Create a PNG image
        img = Image.new('RGB', (300, 300), color='purple')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        
        result = validator.validate_file(img_bytes.getvalue(), "test.png")
        processed = validator.preprocess_image(img_bytes.getvalue())
        
        assert result['valid'] is True
        assert result['format'] == 'png'
        assert processed.shape == (1, 224, 224, 3)
    
    def test_invalid_image_file(self, validator):
        """Test handling of invalid image files."""
        invalid_data = b'This is not an image file'
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(invalid_data, "invalid.jpg")
        
        assert exc_info.value.status_code == 400
        assert "Invalid image file" in exc_info.value.detail
