"""
Unit tests for recommendation engine module.
"""

import pytest
import yaml
from modules.recommender import RecommendationEngine, TreatmentRemedy


class TestRecommendationEngine:
    """Test cases for RecommendationEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create RecommendationEngine instance for testing."""
        return RecommendationEngine("diseases.yml", "config.yaml")
    
    def test_get_recommendations_healthy_plant(self, engine):
        """Test recommendations for healthy plants."""
        result = engine.get_recommendations(
            disease_id="healthy",
            confidence=0.95,
            farmer_language="en"
        )
        
        assert result["disease"]["id"] == "healthy"
        assert result["disease"]["name"] == "Healthy Plant"
        assert len(result["recommended_treatments"]) == 1
        assert result["recommended_treatments"][0]["type"] == "organic"
        assert "Preventive care" in result["recommended_treatments"][0]["name"]
    
    def test_get_recommendations_powdery_mildew(self, engine):
        """Test recommendations for powdery mildew."""
        result = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.85,
            farmer_language="en"
        )
        
        assert result["disease"]["id"] == "powdery_mildew"
        assert result["disease"]["name"] == "Powdery Mildew"
        
        # Should have organic treatments first
        organic_treatments = [t for t in result["recommended_treatments"] if t["type"] == "organic"]
        chemical_treatments = [t for t in result["recommended_treatments"] if t["type"] == "chemical"]
        
        assert len(organic_treatments) >= 1
        assert len(chemical_treatments) >= 1
        
        # First treatment should be organic
        assert result["recommended_treatments"][0]["type"] == "organic"
    
    def test_low_confidence_recommendations(self, engine):
        """Test recommendations for low confidence predictions."""
        result = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.3,  # Below low confidence threshold
            farmer_language="en"
        )
        
        # Should still provide recommendations but with uncertainty warning
        assert result["uncertainty_warning"] is not None
        assert "Low confidence" in result["uncertainty_warning"]
        
        # Chemical treatments should require confirmation
        chemical_treatments = [t for t in result["recommended_treatments"] if t["type"] == "chemical"]
        for treatment in chemical_treatments:
            assert treatment.get("requires_confirmation", False) is True
    
    def test_unknown_disease_handling(self, engine):
        """Test handling of unknown diseases."""
        result = engine.get_recommendations(
            disease_id="unknown_disease",
            confidence=0.8,
            farmer_language="en"
        )
        
        assert result["disease"]["id"] == "unknown"
        assert result["disease"]["name"] == "Unknown Disease"
        assert len(result["recommended_treatments"]) == 0
        assert "Unknown disease detected" in result["notes"]
    
    def test_decision_rules_organic_first(self, engine):
        """Test that organic treatments are prioritized."""
        result = engine.get_recommendations(
            disease_id="bacterial_spot",
            confidence=0.8,
            farmer_language="en"
        )
        
        treatments = result["recommended_treatments"]
        
        # Find first organic and first chemical treatment
        first_organic_idx = None
        first_chemical_idx = None
        
        for i, treatment in enumerate(treatments):
            if treatment["type"] == "organic" and first_organic_idx is None:
                first_organic_idx = i
            elif treatment["type"] == "chemical" and first_chemical_idx is None:
                first_chemical_idx = i
        
        # Organic treatments should come before chemical treatments
        if first_organic_idx is not None and first_chemical_idx is not None:
            assert first_organic_idx < first_chemical_idx
    
    def test_evidence_score_filtering(self, engine):
        """Test filtering based on evidence scores."""
        result = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.6,  # Medium confidence
            farmer_language="en"
        )
        
        # All treatments should have evidence scores that match the confidence level
        for treatment in result["recommended_treatments"]:
            if treatment["type"] == "chemical":
                assert treatment["evidence_score"] <= 0.6  # Should be filtered out if evidence_score > confidence
    
    def test_human_summary_generation(self, engine):
        """Test human summary generation."""
        result = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.8,
            farmer_language="en"
        )
        
        summary = result["notes"]
        
        # Should contain disease name
        assert "Powdery Mildew" in summary
        
        # Should contain treatment information
        assert "Try:" in summary or "Detected:" in summary
    
    def test_sdg_alignment(self, engine):
        """Test SDG alignment inclusion."""
        result = engine.get_recommendations(
            disease_id="rust",
            confidence=0.7,
            farmer_language="en"
        )
        
        assert "sdg_alignment" in result
        assert len(result["sdg_alignment"]) > 0
        assert any("SDG" in sdg for sdg in result["sdg_alignment"])
    
    def test_metadata_inclusion(self, engine):
        """Test that metadata is included in results."""
        result = engine.get_recommendations(
            disease_id="bacterial_spot",
            confidence=0.8,
            crop_type="Tomato",
            growth_stage="flowering",
            location="California",
            farmer_language="es"
        )
        
        metadata = result["metadata"]
        assert metadata["crop_type"] == "Tomato"
        assert metadata["growth_stage"] == "flowering"
        assert metadata["location"] == "California"
        assert metadata["language"] == "es"
    
    def test_dosage_validation_valid(self, engine):
        """Test valid dosage validation."""
        result = engine.validate_dosage(
            disease_id="powdery_mildew",
            remedy_name="Neem oil 1% spray",
            requested_dosage="10 ml per L"
        )
        
        assert result["valid"] is True
        assert result["blocked"] is False
    
    def test_dosage_validation_unknown_disease(self, engine):
        """Test dosage validation for unknown disease."""
        result = engine.validate_dosage(
            disease_id="unknown_disease",
            remedy_name="Some remedy",
            requested_dosage="10 ml per L"
        )
        
        assert result["valid"] is False
        assert result["blocked"] is True
        assert "Unknown disease" in result["warning"]
    
    def test_dosage_validation_unknown_remedy(self, engine):
        """Test dosage validation for unknown remedy."""
        result = engine.validate_dosage(
            disease_id="powdery_mildew",
            remedy_name="Unknown Remedy",
            requested_dosage="10 ml per L"
        )
        
        assert result["valid"] is False
        assert result["blocked"] is True
        assert "Remedy not found" in result["warning"]
    
    def test_get_treatment_by_id_existing(self, engine):
        """Test getting treatment by ID for existing disease."""
        result = engine.get_treatment_by_id("powdery_mildew")
        
        assert result is not None
        assert result["disease"]["id"] == "powdery_mildew"
        assert result["disease"]["name"] == "Powdery Mildew"
        assert len(result["remedies"]) > 0
    
    def test_get_treatment_by_id_nonexistent(self, engine):
        """Test getting treatment by ID for non-existent disease."""
        result = engine.get_treatment_by_id("nonexistent_disease")
        
        assert result is None
    
    def test_treatment_remedy_dataclass(self):
        """Test TreatmentRemedy dataclass."""
        remedy = TreatmentRemedy(
            type="organic",
            name="Test Remedy",
            application="10 ml per L",
            application_volume="500 L/ha",
            frequency="Every 7 days",
            best_time="Morning",
            cost_estimate_per_hectare="USD 10",
            safety={"PPE": ["gloves"]},
            evidence_score=0.8,
            max_applications_per_season=4
        )
        
        assert remedy.type == "organic"
        assert remedy.name == "Test Remedy"
        assert remedy.evidence_score == 0.8
        assert remedy.requires_confirmation is False  # Default value
    
    def test_uncertainty_message_generation(self, engine):
        """Test uncertainty message generation."""
        # Test low confidence
        result_low = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.3,
            farmer_language="en"
        )
        assert result_low["uncertainty_warning"] is not None
        
        # Test high confidence
        result_high = engine.get_recommendations(
            disease_id="powdery_mildew",
            confidence=0.8,
            farmer_language="en"
        )
        assert result_high["uncertainty_warning"] is None
        
        # Test healthy plant (should not have uncertainty warning)
        result_healthy = engine.get_recommendations(
            disease_id="healthy",
            confidence=0.3,
            farmer_language="en"
        )
        assert result_healthy["uncertainty_warning"] is None
