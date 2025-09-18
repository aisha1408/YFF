"""
Recommendation engine module for the Sustainable Pesticide & Fertilizer Recommendation System.
Implements rules-driven treatment recommendations with anti-overuse logic and SDG alignment.
"""

import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TreatmentRemedy:
    """Data class for treatment remedy information."""
    type: str  # "organic" or "chemical"
    name: str
    application: str
    application_volume: str
    frequency: str
    best_time: str
    cost_estimate_per_hectare: str
    safety: Dict[str, Any]
    evidence_score: float
    max_applications_per_season: int
    requires_confirmation: bool = False


class RecommendationEngine:
    """Rules-driven recommendation engine with anti-overuse logic."""
    
    def __init__(self, diseases_path: str = "diseases.yml", config_path: str = "config.yaml"):
        """Initialize the recommendation engine."""
        # Load diseases database
        with open(diseases_path, 'r') as f:
            self.diseases_db = yaml.safe_load(f)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.anti_overuse_config = self.config['anti_overuse']
        self.sdg_alignment = self.config['sdg_alignment']
    
    def get_recommendations(
        self, 
        disease_id: str, 
        confidence: float, 
        crop_type: Optional[str] = None,
        growth_stage: Optional[str] = None,
        location: Optional[str] = None,
        farmer_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate treatment recommendations based on disease detection.
        
        Args:
            disease_id: Detected disease ID
            confidence: Prediction confidence score
            crop_type: Optional crop type
            growth_stage: Optional growth stage
            location: Optional location
            farmer_language: Farmer's preferred language
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        # Get disease information
        if disease_id not in self.diseases_db:
            logger.warning(f"Unknown disease ID: {disease_id}")
            return self._get_unknown_disease_response()
        
        disease_info = self.diseases_db[disease_id]
        remedies = disease_info.get('remedies', [])
        
        # Apply decision rules
        filtered_remedies = self._apply_decision_rules(remedies, confidence, disease_id)
        
        # Format recommendations
        recommendations = []
        for remedy_data in filtered_remedies:
            remedy = TreatmentRemedy(**remedy_data)
            recommendations.append(self._format_remedy(remedy))
        
        # Generate human summary
        human_summary = self._generate_human_summary(disease_info['name'], recommendations, farmer_language)
        
        # Check for uncertainty
        uncertainty_message = self._get_uncertainty_message(confidence, disease_id)
        
        return {
            "disease": {
                "id": disease_id,
                "name": disease_info['name'],
                "confidence": confidence
            },
            "recommended_treatments": recommendations,
            "notes": human_summary,
            "uncertainty_warning": uncertainty_message,
            "metadata": {
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "location": location,
                "language": farmer_language
            }
        }
    
    def _apply_decision_rules(
        self, 
        remedies: List[Dict], 
        confidence: float, 
        disease_id: str
    ) -> List[Dict]:
        """Apply decision rules to filter and prioritize remedies."""
        filtered_remedies = []
        
        # Rule 1: Default - present organic remedies first
        organic_remedies = [r for r in remedies if r['type'] == 'organic']
        chemical_remedies = [r for r in remedies if r['type'] == 'chemical']
        
        # Always include organic remedies
        filtered_remedies.extend(organic_remedies)
        
        # Rule 2: Chemical remedies based on confidence and evidence
        low_confidence_threshold = self.config['model']['low_confidence_threshold']
        
        if confidence >= low_confidence_threshold:
            # Include chemical remedies if confidence is sufficient
            for remedy in chemical_remedies:
                if confidence >= remedy.get('evidence_score', 0.5):
                    filtered_remedies.append(remedy)
        else:
            # Low confidence - mark chemical remedies as requiring confirmation
            for remedy in chemical_remedies:
                remedy_copy = remedy.copy()
                remedy_copy['requires_confirmation'] = True
                filtered_remedies.append(remedy_copy)
        
        return filtered_remedies
    
    def _format_remedy(self, remedy: TreatmentRemedy) -> Dict[str, Any]:
        """Format a remedy for API response."""
        return {
            "type": remedy.type,
            "name": remedy.name,
            "dosage": remedy.application,
            "application_volume": remedy.application_volume,
            "frequency": remedy.frequency,
            "best_time": remedy.best_time,
            "cost_estimate_per_hectare": remedy.cost_estimate_per_hectare,
            "safety": remedy.safety,
            "evidence_score": remedy.evidence_score,
            "max_applications_per_season": remedy.max_applications_per_season,
            "requires_confirmation": remedy.requires_confirmation
        }
    
    def _generate_human_summary(
        self, 
        disease_name: str, 
        recommendations: List[Dict], 
        language: str
    ) -> str:
        """Generate a human-friendly summary of recommendations."""
        if not recommendations:
            return f"No specific treatment needed for {disease_name}."
        
        # Get top organic recommendation
        organic_recs = [r for r in recommendations if r['type'] == 'organic']
        chemical_recs = [r for r in recommendations if r['type'] == 'chemical']
        
        summary_parts = [f"Detected: {disease_name}"]
        
        if organic_recs:
            top_organic = organic_recs[0]
            summary_parts.append(f"Try: {top_organic['name']} ({top_organic['dosage']})")
        
        if chemical_recs:
            top_chemical = chemical_recs[0]
            ppe_list = ", ".join(top_chemical['safety'].get('PPE', []))
            phi = top_chemical['safety'].get('pre_harvest_interval', '0')
            
            summary_parts.append(
                f"If needed: {top_chemical['name']} ({top_chemical['dosage']}) "
                f"— wear {ppe_list} — wait {phi} days before harvest"
            )
        
        return " | ".join(summary_parts)
    
    def _get_uncertainty_message(self, confidence: float, disease_id: str) -> Optional[str]:
        """Generate uncertainty message for low-confidence predictions."""
        if disease_id == "healthy":
            return None
        
        low_threshold = self.config['model']['low_confidence_threshold']
        
        if confidence < low_threshold:
            return (
                f"Low confidence detection ({confidence:.1%}). "
                "Consider additional scouting or confirmatory tests before treatment."
            )
        
        return None
    
    def _get_unknown_disease_response(self) -> Dict[str, Any]:
        """Handle unknown disease cases."""
        return {
            "disease": {
                "id": "unknown",
                "name": "Unknown Disease",
                "confidence": 0.0
            },
            "recommended_treatments": [],
            "sdg_alignment": self.sdg_alignment,
            "notes": "Unknown disease detected. Please consult with a local agricultural expert.",
            "uncertainty_warning": "Disease not recognized. Manual inspection recommended.",
            "metadata": {}
        }
    
    def validate_dosage(
        self, 
        disease_id: str, 
        remedy_name: str, 
        requested_dosage: str
    ) -> Dict[str, Any]:
        """
        Validate requested dosage against anti-overuse rules.
        
        Args:
            disease_id: Disease ID
            remedy_name: Name of the remedy
            requested_dosage: Requested dosage string
            
        Returns:
            Validation result with warnings and blocking status
        """
        if disease_id not in self.diseases_db:
            return {
                "valid": False,
                "warning": "Unknown disease",
                "blocked": True
            }
        
        # Find the specific remedy
        remedies = self.diseases_db[disease_id].get('remedies', [])
        remedy = None
        for r in remedies:
            if r['name'] == remedy_name:
                remedy = r
                break
        
        if not remedy:
            return {
                "valid": False,
                "warning": "Remedy not found",
                "blocked": True
            }
        
        # Parse requested dosage (simplified - in real implementation, you'd parse the string)
        # For now, we'll use a simple multiplier check
        max_multiplier = self.anti_overuse_config['max_dosage_multiplier']
        confirmation_threshold = self.anti_overuse_config['require_confirmation_above']
        
        # Mock dosage validation (in real implementation, parse and compare actual values)
        dosage_multiplier = 1.0  # This would be calculated from requested_dosage
        
        if dosage_multiplier > max_multiplier:
            return {
                "valid": False,
                "warning": f"Dosage exceeds maximum allowed ({max_multiplier}x recommended)",
                "blocked": True
            }
        elif dosage_multiplier > confirmation_threshold:
            return {
                "valid": True,
                "warning": f"High dosage requested ({dosage_multiplier}x recommended)",
                "blocked": False,
                "requires_confirmation": True
            }
        else:
            return {
                "valid": True,
                "warning": None,
                "blocked": False,
                "requires_confirmation": False
            }
    
    def get_treatment_by_id(self, disease_id: str) -> Optional[Dict[str, Any]]:
        """Get treatment information for a specific disease ID (for offline lookup)."""
        if disease_id not in self.diseases_db:
            return None
        
        disease_info = self.diseases_db[disease_id]
        remedies = disease_info.get('remedies', [])
        
        formatted_remedies = []
        for remedy_data in remedies:
            remedy = TreatmentRemedy(**remedy_data)
            formatted_remedies.append(self._format_remedy(remedy))
        
        return {
            "disease": {
                "id": disease_id,
                "name": disease_info['name']
            },
            "remedies": formatted_remedies
        }
