"""
Unit tests for CLI module.
"""

import pytest
import io
import tempfile
from pathlib import Path
from PIL import Image
from modules.cli import PlantCareCLI


class TestPlantCareCLI:
    """Test cases for PlantCareCLI class."""
    
    @pytest.fixture
    def cli_instance(self):
        """Create CLI instance for testing."""
        return PlantCareCLI("config.yaml")
    
    @pytest.fixture
    def test_image_path(self, tmp_path):
        """Create a temporary image file for testing."""
        img = Image.new('RGB', (300, 300), color='green')
        image_path = tmp_path / "test_image.jpg"
        img.save(image_path, format='JPEG')
        return str(image_path)
    
    def test_cli_initialization(self, cli_instance):
        """Test CLI initialization."""
        assert cli_instance is not None
        assert cli_instance.inference_engine is not None
        assert cli_instance.recommendation_engine is not None
        assert cli_instance.formatter is not None
        assert cli_instance.config is not None
    
    def test_analyze_image_success(self, cli_instance, test_image_path):
        """Test successful image analysis."""
        result = cli_instance.analyze_image(
            image_path=test_image_path,
            crop_type="Tomato",
            growth_stage="flowering",
            location="California",
            language="en"
        )
        
        # Check result structure
        assert "disease" in result
        assert "recommended_treatments" in result
        assert "sdg_alignment" in result
        assert "notes" in result
        assert "metadata" in result
        
        # Check disease information
        assert "id" in result["disease"]
        assert "name" in result["disease"]
        assert "confidence" in result["disease"]
        
        # Check metadata
        assert result["metadata"]["crop_type"] == "Tomato"
        assert result["metadata"]["growth_stage"] == "flowering"
        assert result["metadata"]["location"] == "California"
        assert result["metadata"]["language"] == "en"
    
    def test_analyze_image_file_not_found(self, cli_instance):
        """Test image analysis with non-existent file."""
        result = cli_instance.analyze_image(
            image_path="nonexistent_image.jpg",
            language="en"
        )
        
        assert result["error"] is True
        assert "Analysis failed" in result["message"]
        assert result["image_path"] == "nonexistent_image.jpg"
    
    def test_get_treatment_info_success(self, cli_instance):
        """Test successful treatment info retrieval."""
        result = cli_instance.get_treatment_info("powdery_mildew", "en")
        
        assert "disease" in result
        assert result["disease"]["id"] == "powdery_mildew"
        assert "treatments" in result
        assert "sdg_alignment" in result
    
    def test_get_treatment_info_not_found(self, cli_instance):
        """Test treatment info retrieval for non-existent disease."""
        result = cli_instance.get_treatment_info("nonexistent_disease", "en")
        
        assert result["error"] is True
        assert "Treatment not found" in result["message"]
    
    def test_list_diseases(self, cli_instance):
        """Test disease listing."""
        result = cli_instance.list_diseases()
        
        assert "diseases" in result
        assert isinstance(result["diseases"], list)
        assert len(result["diseases"]) > 0
        
        # Check disease structure
        disease = result["diseases"][0]
        assert "id" in disease
        assert "name" in disease
        assert "remedy_count" in disease
    
    def test_validate_dosage_success(self, cli_instance):
        """Test successful dosage validation."""
        result = cli_instance.validate_dosage(
            "powdery_mildew",
            "Neem oil 1% spray",
            "10 ml per L"
        )
        
        assert "valid" in result
        assert "blocked" in result
    
    def test_validate_dosage_invalid_disease(self, cli_instance):
        """Test dosage validation with invalid disease."""
        result = cli_instance.validate_dosage(
            "invalid_disease",
            "Some remedy",
            "10 ml per L"
        )
        
        assert result["valid"] is False
        assert result["blocked"] is True
    
    def test_format_output_json(self, cli_instance):
        """Test JSON output formatting."""
        data = {"test": "data", "number": 123}
        result = cli_instance.format_output(data, "json")
        
        assert isinstance(result, str)
        assert "test" in result
        assert "data" in result
        assert "123" in result
    
    def test_format_output_text(self, cli_instance):
        """Test text output formatting."""
        data = {
            "disease": {"name": "Powdery Mildew", "confidence": 0.85},
            "recommended_treatments": [
                {
                    "name": "Neem oil spray",
                    "type": "organic",
                    "dosage": "10 ml per L",
                    "frequency": "Every 7 days",
                    "best_time": "Morning",
                    "cost_estimate_per_hectare": "USD 12",
                    "safety": {"PPE": ["gloves", "mask"], "warning": "Test warning"}
                }
            ],
            "sdg_alignment": ["SDG 12: Responsible Consumption"],
            "notes": "Test summary"
        }
        
        result = cli_instance.format_output(data, "text")
        
        assert isinstance(result, str)
        assert "Powdery Mildew" in result
        assert "Confidence:" in result
        assert "Treatment Recommendations:" in result
        assert "Neem oil spray" in result
        assert "ORGANIC" in result
        assert "SDG 12" in result
        assert "Test summary" in result
    
    def test_format_output_text_error(self, cli_instance):
        """Test text output formatting for error cases."""
        data = {"error": True, "message": "Test error message"}
        result = cli_instance.format_output(data, "text")
        
        assert isinstance(result, str)
        assert "Error: Test error message" in result
    
    def test_format_output_table(self, cli_instance):
        """Test table output formatting."""
        data = {
            "disease": {"name": "Test Disease", "confidence": 0.75},
            "recommended_treatments": [
                {
                    "name": "Test Treatment",
                    "type": "organic",
                    "dosage": "5 ml per L",
                    "frequency": "Every 5 days",
                    "cost_estimate_per_hectare": "USD 8"
                }
            ]
        }
        
        result = cli_instance.format_output(data, "table")
        
        assert isinstance(result, str)
        assert "DISEASE DETECTION" in result
        assert "Test Disease" in result
        assert "TREATMENT RECOMMENDATIONS" in result
        assert "Test Treatment" in result
    
    def test_format_output_table_error(self, cli_instance):
        """Test table output formatting for error cases."""
        data = {"error": True, "message": "Test error"}
        result = cli_instance.format_output(data, "table")
        
        assert isinstance(result, str)
        assert "Error: Test error" in result
    
    def test_multilingual_support(self, cli_instance, test_image_path):
        """Test multilingual support in CLI."""
        languages = ["en", "es", "fr", "hi", "pt"]
        
        for language in languages:
            result = cli_instance.analyze_image(
                image_path=test_image_path,
                language=language
            )
            
            # Should not have error
            assert "error" not in result or not result["error"]
            
            # Check metadata language
            if "metadata" in result:
                assert result["metadata"]["language"] == language
    
    def test_optional_parameters(self, cli_instance, test_image_path):
        """Test CLI with optional parameters."""
        # Test with all parameters
        result_all = cli_instance.analyze_image(
            image_path=test_image_path,
            crop_type="Rice",
            growth_stage="vegetative",
            location="India",
            language="hi"
        )
        
        assert "metadata" in result_all
        assert result_all["metadata"]["crop_type"] == "Rice"
        assert result_all["metadata"]["growth_stage"] == "vegetative"
        assert result_all["metadata"]["location"] == "India"
        assert result_all["metadata"]["language"] == "hi"
        
        # Test with minimal parameters
        result_minimal = cli_instance.analyze_image(
            image_path=test_image_path,
            language="en"
        )
        
        assert "metadata" in result_minimal
        assert result_minimal["metadata"]["crop_type"] is None
        assert result_minimal["metadata"]["growth_stage"] is None
        assert result_minimal["metadata"]["location"] is None
        assert result_minimal["metadata"]["language"] == "en"
    
    def test_visual_indicators(self, cli_instance, test_image_path):
        """Test that visual indicators are added to treatments."""
        result = cli_instance.analyze_image(test_image_path, language="en")
        
        if "recommended_treatments" in result and result["recommended_treatments"]:
            treatment = result["recommended_treatments"][0]
            
            # Check visual indicators
            assert "icon" in treatment
            assert "badge" in treatment
            assert "color" in treatment
            assert "safety_level" in treatment
            assert "safety_icon" in treatment
            assert "cost_level" in treatment
            assert "cost_icon" in treatment
