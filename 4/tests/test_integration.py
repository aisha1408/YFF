"""
Integration tests for the complete system workflow.
"""

import pytest
import io
import yaml
from PIL import Image
from modules.inference import InferenceEngine
from modules.recommender import RecommendationEngine
from modules.formatter import ResponseFormatter
from modules.cli import PlantCareCLI


class TestSystemIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def inference_engine(self):
        """Create inference engine for testing."""
        return InferenceEngine("config.yaml")
    
    @pytest.fixture
    def recommendation_engine(self):
        """Create recommendation engine for testing."""
        return RecommendationEngine("diseases.yml", "config.yaml")
    
    @pytest.fixture
    def formatter(self):
        """Create formatter for testing."""
        return ResponseFormatter("config.yaml")
    
    @pytest.fixture
    def cli_instance(self):
        """Create CLI instance for testing."""
        return PlantCareCLI("config.yaml")
    
    @pytest.fixture
    def test_image_bytes(self):
        """Create test image bytes."""
        img = Image.new('RGB', (300, 300), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_complete_workflow_mock_mode(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test complete workflow in mock mode."""
        # Step 1: Process image through inference
        inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
        
        # Verify inference result structure
        assert "disease" in inference_result
        assert "image_metadata" in inference_result
        assert "model_info" in inference_result
        
        disease_id = inference_result["disease"]["id"]
        confidence = inference_result["disease"]["confidence"]
        
        # Step 2: Generate recommendations
        recommendations = recommendation_engine.get_recommendations(
            disease_id=disease_id,
            confidence=confidence,
            farmer_language="en"
        )
        
        # Verify recommendations structure
        assert "disease" in recommendations
        assert "recommended_treatments" in recommendations
        assert "sdg_alignment" in recommendations
        assert "notes" in recommendations
        
        # Step 3: Format complete response
        response = formatter.format_detection_response(
            inference_result=inference_result,
            recommendations=recommendations,
            farmer_language="en"
        )
        
        # Verify complete response structure
        assert "disease" in response
        assert "recommended_treatments" in response
        assert "sdg_alignment" in response
        assert "notes" in response
        assert "supporting_heatmap_base64" in response
        assert "metadata" in response
        
        # Verify treatments have visual indicators
        treatments = response["recommended_treatments"]
        if treatments:
            for treatment in treatments:
                assert "icon" in treatment
                assert "badge" in treatment
                assert "color" in treatment
    
    def test_workflow_with_metadata(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test workflow with additional metadata."""
        # Process image
        inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
        
        # Generate recommendations with metadata
        recommendations = recommendation_engine.get_recommendations(
            disease_id=inference_result["disease"]["id"],
            confidence=inference_result["disease"]["confidence"],
            crop_type="Tomato",
            growth_stage="flowering",
            location="California",
            farmer_language="es"
        )
        
        # Format response
        response = formatter.format_detection_response(
            inference_result=inference_result,
            recommendations=recommendations,
            farmer_language="es"
        )
        
        # Verify metadata is preserved
        metadata = response["metadata"]
        assert metadata["crop_type"] == "Tomato"
        assert metadata["growth_stage"] == "flowering"
        assert metadata["location"] == "California"
        assert metadata["language"] == "es"
    
    def test_low_confidence_workflow(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test workflow with low confidence prediction."""
        # Process image
        inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
        
        # Manually set low confidence for testing
        inference_result["disease"]["confidence"] = 0.3
        
        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations(
            disease_id=inference_result["disease"]["id"],
            confidence=0.3,
            farmer_language="en"
        )
        
        # Format response
        response = formatter.format_detection_response(
            inference_result=inference_result,
            recommendations=recommendations,
            farmer_language="en"
        )
        
        # Verify uncertainty warning is present
        assert "uncertainty_warning" in response
        assert response["uncertainty_warning"] is not None
        
        # Verify chemical treatments require confirmation
        chemical_treatments = [t for t in response["recommended_treatments"] if t["type"] == "chemical"]
        for treatment in chemical_treatments:
            assert treatment.get("requires_confirmation", False) is True
    
    def test_healthy_plant_workflow(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test workflow for healthy plant detection."""
        # Process image
        inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
        
        # Manually set to healthy for testing
        inference_result["disease"]["id"] = "healthy"
        inference_result["disease"]["name"] = "Healthy Plant"
        inference_result["disease"]["confidence"] = 0.95
        
        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations(
            disease_id="healthy",
            confidence=0.95,
            farmer_language="en"
        )
        
        # Format response
        response = formatter.format_detection_response(
            inference_result=inference_result,
            recommendations=recommendations,
            farmer_language="en"
        )
        
        # Verify healthy plant response
        assert response["disease"]["id"] == "healthy"
        assert len(response["recommended_treatments"]) == 1
        assert response["recommended_treatments"][0]["type"] == "organic"
        assert "Preventive care" in response["recommended_treatments"][0]["name"]
        assert response.get("uncertainty_warning") is None
    
    def test_multilingual_support(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test multilingual support in the workflow."""
        languages = ["en", "es", "fr", "hi", "pt"]
        
        for language in languages:
            # Process image
            inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
            
            # Generate recommendations
            recommendations = recommendation_engine.get_recommendations(
                disease_id=inference_result["disease"]["id"],
                confidence=inference_result["disease"]["confidence"],
                farmer_language=language
            )
            
            # Format response
            response = formatter.format_detection_response(
                inference_result=inference_result,
                recommendations=recommendations,
                farmer_language=language
            )
            
            # Verify language is preserved
            assert response["metadata"]["language"] == language
            assert "labels" in response
    
    def test_anti_overuse_integration(self, recommendation_engine):
        """Test anti-overuse logic integration."""
        # Test valid dosage
        result_valid = recommendation_engine.validate_dosage(
            disease_id="powdery_mildew",
            remedy_name="Neem oil 1% spray",
            requested_dosage="10 ml per L"
        )
        assert result_valid["valid"] is True
        
        # Test invalid disease
        result_invalid = recommendation_engine.validate_dosage(
            disease_id="unknown_disease",
            remedy_name="Some remedy",
            requested_dosage="10 ml per L"
        )
        assert result_invalid["valid"] is False
        assert result_invalid["blocked"] is True
    
    def test_sdg_alignment_consistency(self, inference_engine, recommendation_engine, formatter, test_image_bytes):
        """Test that SDG alignment is consistent across the system."""
        # Process image
        inference_result = inference_engine.process_image(test_image_bytes, "test.jpg")
        
        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations(
            disease_id=inference_result["disease"]["id"],
            confidence=inference_result["disease"]["confidence"],
            farmer_language="en"
        )
        
        # Format response
        response = formatter.format_detection_response(
            inference_result=inference_result,
            recommendations=recommendations,
            farmer_language="en"
        )
        
        # Verify SDG alignment
        assert "sdg_alignment" in response
        assert len(response["sdg_alignment"]) > 0
        
        # Check that SDG alignment contains expected goals
        sdg_text = " ".join(response["sdg_alignment"])
        assert "SDG 12" in sdg_text
        assert "SDG 3" in sdg_text
        assert "SDG 15" in sdg_text
    
    def test_cli_workflow(self, cli_instance, test_image_bytes, tmp_path):
        """Test complete CLI workflow."""
        # Create a temporary image file
        image_path = tmp_path / "test_image.jpg"
        with open(image_path, 'wb') as f:
            f.write(test_image_bytes)
        
        # Test image analysis
        result = cli_instance.analyze_image(
            image_path=str(image_path),
            crop_type="Tomato",
            growth_stage="flowering",
            location="California",
            language="en"
        )
        
        # Verify result structure
        assert "disease" in result
        assert "recommended_treatments" in result
        assert "sdg_alignment" in result
        assert "notes" in result
        
        # Test treatment lookup
        treatment_result = cli_instance.get_treatment_info("powdery_mildew", "en")
        assert "disease" in treatment_result or "error" in treatment_result
        
        # Test disease listing
        diseases_result = cli_instance.list_diseases()
        assert "diseases" in diseases_result
        assert len(diseases_result["diseases"]) > 0
        
        # Test dosage validation
        validation_result = cli_instance.validate_dosage(
            "powdery_mildew",
            "Neem oil 1% spray",
            "10 ml per L"
        )
        assert "valid" in validation_result
    
    def test_cli_output_formatting(self, cli_instance, test_image_bytes, tmp_path):
        """Test CLI output formatting."""
        # Create a temporary image file
        image_path = tmp_path / "test_image.jpg"
        with open(image_path, 'wb') as f:
            f.write(test_image_bytes)
        
        # Test JSON output
        result = cli_instance.analyze_image(str(image_path), language="en")
        json_output = cli_instance.format_output(result, "json")
        assert isinstance(json_output, str)
        
        # Test text output
        text_output = cli_instance.format_output(result, "text")
        assert isinstance(text_output, str)
        assert "Disease:" in text_output or "Error:" in text_output
        
        # Test table output
        table_output = cli_instance.format_output(result, "table")
        assert isinstance(table_output, str)
    
    def test_error_handling_integration(self, inference_engine):
        """Test error handling in the integration workflow."""
        # Test with invalid image data
        invalid_data = b"This is not an image"
        
        with pytest.raises(Exception):
            inference_engine.process_image(invalid_data, "invalid.jpg")
    
    def test_configuration_loading(self):
        """Test that all configuration files load correctly."""
        # Test main config
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        assert "model" in config
        assert "image" in config
        assert "anti_overuse" in config
        assert "api" in config
        assert "localization" in config
        assert "sdg_alignment" in config
        
        # Test diseases config
        with open("diseases.yml", 'r') as f:
            diseases = yaml.safe_load(f)
        
        assert "powdery_mildew" in diseases
        assert "bacterial_spot" in diseases
        assert "rust" in diseases
        assert "healthy" in diseases
        
        # Verify disease structure
        for disease_id, disease_info in diseases.items():
            assert "name" in disease_info
            assert "remedies" in disease_info
            
            for remedy in disease_info["remedies"]:
                assert "type" in remedy
                assert "name" in remedy
                assert "application" in remedy
                assert "safety" in remedy
                assert "evidence_score" in remedy
                assert "max_applications_per_season" in remedy
