"""
Response formatting module for the Sustainable Pesticide & Fertilizer Recommendation System.
Handles JSON response formatting, internationalization, and human-readable summaries.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from .inference import InferenceEngine
from .recommender import RecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Handles response formatting and internationalization."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the formatter."""
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.localization_config = self.config['localization']
        self.default_language = self.localization_config['default_language']
        
        # Load translations (simplified - in real implementation, load from files)
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation strings for different languages."""
        return {
            "en": {
                "disease_detected": "Disease Detected",
                "confidence": "Confidence",
                "organic_treatment": "Organic Treatment",
                "chemical_treatment": "Chemical Treatment",
                "safety_warning": "Safety Warning",
                "ppe_required": "PPE Required",
                "pre_harvest_interval": "Pre-harvest Interval",
                "cost_estimate": "Cost Estimate",
                "frequency": "Frequency",
                "best_time": "Best Time",
                "uncertainty_warning": "Uncertainty Warning",
                "sdg_alignment": "SDG Alignment"
            },
            "es": {
                "disease_detected": "Enfermedad Detectada",
                "confidence": "Confianza",
                "organic_treatment": "Tratamiento Orgánico",
                "chemical_treatment": "Tratamiento Químico",
                "safety_warning": "Advertencia de Seguridad",
                "ppe_required": "EPP Requerido",
                "pre_harvest_interval": "Intervalo Pre-cosecha",
                "cost_estimate": "Estimación de Costo",
                "frequency": "Frecuencia",
                "best_time": "Mejor Momento",
                "uncertainty_warning": "Advertencia de Incertidumbre",
                "sdg_alignment": "Alineación ODS"
            },
            "fr": {
                "disease_detected": "Maladie Détectée",
                "confidence": "Confiance",
                "organic_treatment": "Traitement Biologique",
                "chemical_treatment": "Traitement Chimique",
                "safety_warning": "Avertissement de Sécurité",
                "ppe_required": "EPI Requis",
                "pre_harvest_interval": "Intervalle Pré-récolte",
                "cost_estimate": "Estimation des Coûts",
                "frequency": "Fréquence",
                "best_time": "Meilleur Moment",
                "uncertainty_warning": "Avertissement d'Incertitude",
                "sdg_alignment": "Alignement ODD"
            }
        }
    
    def format_detection_response(
        self,
        inference_result: Dict[str, Any],
        recommendations: Dict[str, Any],
        farmer_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Format the complete detection response with recommendations.
        
        Args:
            inference_result: Results from inference engine
            recommendations: Results from recommendation engine
            farmer_language: Farmer's preferred language
            
        Returns:
            Formatted response dictionary
        """
        # Ensure language is supported
        if farmer_language not in self.localization_config['supported_languages']:
            farmer_language = self.default_language
        
        # Combine inference and recommendation results
        response = {
            "disease": inference_result["disease"],
            "recommended_treatments": recommendations["recommended_treatments"],
            "notes": recommendations["notes"],
            "supporting_heatmap_base64": inference_result.get("supporting_heatmap_base64"),
            "metadata": {
                "language": farmer_language,
                "model_info": inference_result.get("model_info", {}),
                "image_metadata": inference_result.get("image_metadata", {}),
                "recommendation_metadata": recommendations.get("metadata", {})
            }
        }
        
        # Add warnings if present
        if inference_result.get("warning"):
            response["image_warning"] = inference_result["warning"]
        
        if recommendations.get("uncertainty_warning"):
            response["uncertainty_warning"] = recommendations["uncertainty_warning"]
        
        # Add localized labels
        response["labels"] = self.translations.get(farmer_language, self.translations[self.default_language])
        
        return response
    
    def format_treatment_lookup_response(
        self,
        treatment_data: Dict[str, Any],
        farmer_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Format treatment lookup response for offline use.
        
        Args:
            treatment_data: Treatment data from recommendation engine
            farmer_language: Farmer's preferred language
            
        Returns:
            Formatted response dictionary
        """
        if not treatment_data:
            return {
                "error": "Treatment not found",
                "disease_id": None,
                "treatments": [],
                "labels": self.translations.get(farmer_language, self.translations[self.default_language])
            }
        
        # Ensure language is supported
        if farmer_language not in self.localization_config['supported_languages']:
            farmer_language = self.default_language
        
        return {
            "disease": treatment_data["disease"],
            "treatments": treatment_data["remedies"],
            "labels": self.translations.get(farmer_language, self.translations[self.default_language]),
            "metadata": {
                "language": farmer_language,
                "source": "offline_lookup"
            }
        }
    
    def format_health_check_response(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format health check response.
        
        Args:
            model_info: Model information from model loader
            
        Returns:
            Health check response dictionary
        """
        return {
            "status": "healthy",
            "service": "Sustainable Pesticide & Fertilizer Recommendation System",
            "version": "1.0.0",
            "model": model_info,
            "features": {
                "image_upload": True,
                "disease_detection": True,
                "treatment_recommendations": True,
                "anti_overuse_protection": True,
                "multilingual_support": True,
                "mock_mode": model_info.get("mock_mode", False)
            },
            "supported_languages": self.localization_config['supported_languages']
        }
    
    def format_error_response(
        self,
        error_message: str,
        error_code: str = "UNKNOWN_ERROR",
        farmer_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Format error response.
        
        Args:
            error_message: Error message
            error_code: Error code
            farmer_language: Farmer's preferred language
            
        Returns:
            Error response dictionary
        """
        # Ensure language is supported
        if farmer_language not in self.localization_config['supported_languages']:
            farmer_language = self.default_language
        
        return {
            "error": True,
            "error_code": error_code,
            "message": error_message,
            "language": farmer_language,
            "labels": self.translations.get(farmer_language, self.translations[self.default_language])
        }
    
    def generate_human_summary(
        self,
        disease_name: str,
        treatments: List[Dict[str, Any]],
        farmer_language: str = "en"
    ) -> str:
        """
        Generate a human-readable summary of the recommendations.
        
        Args:
            disease_name: Name of detected disease
            treatments: List of treatment recommendations
            farmer_language: Farmer's preferred language
            
        Returns:
            Human-readable summary string
        """
        if not treatments:
            return f"No specific treatment needed for {disease_name}."
        
        # Get translations
        labels = self.translations.get(farmer_language, self.translations[self.default_language])
        
        # Separate organic and chemical treatments
        organic_treatments = [t for t in treatments if t['type'] == 'organic']
        chemical_treatments = [t for t in treatments if t['type'] == 'chemical']
        
        summary_parts = [f"{labels['disease_detected']}: {disease_name}"]
        
        if organic_treatments:
            top_organic = organic_treatments[0]
            summary_parts.append(
                f"{labels['organic_treatment']}: {top_organic['name']} "
                f"({top_organic['dosage']})"
            )
        
        if chemical_treatments:
            top_chemical = chemical_treatments[0]
            ppe_list = ", ".join(top_chemical['safety'].get('PPE', []))
            phi = top_chemical['safety'].get('pre_harvest_interval', '0')
            
            summary_parts.append(
                f"{labels['chemical_treatment']}: {top_chemical['name']} "
                f"({top_chemical['dosage']}) — {labels['ppe_required']}: {ppe_list} "
                f"— {labels['pre_harvest_interval']}: {phi} days"
            )
        
        return " | ".join(summary_parts)
    
    def add_visual_indicators(self, treatments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add visual indicators and icons for frontend display.
        
        Args:
            treatments: List of treatment recommendations
            
        Returns:
            Treatments with added visual indicators
        """
        for treatment in treatments:
            # Add type-specific icons
            if treatment['type'] == 'organic':
                treatment['icon'] = "🌱"
                treatment['badge'] = "organic"
                treatment['color'] = "green"
            else:  # chemical
                treatment['icon'] = "⚠️"
                treatment['badge'] = "chemical"
                treatment['color'] = "orange"
            
            # Add safety level indicators
            ppe_count = len(treatment['safety'].get('PPE', []))
            if ppe_count == 0:
                treatment['safety_level'] = "low"
                treatment['safety_icon'] = "✅"
            elif ppe_count <= 2:
                treatment['safety_level'] = "medium"
                treatment['safety_icon'] = "⚠️"
            else:
                treatment['safety_level'] = "high"
                treatment['safety_icon'] = "🚨"
            
            # Add cost indicator
            cost_str = treatment.get('cost_estimate_per_hectare', 'USD 0')
            if 'USD 0' in cost_str:
                treatment['cost_level'] = "free"
                treatment['cost_icon'] = "💰"
            elif 'USD' in cost_str:
                cost_value = float(cost_str.split('USD ')[1])
                if cost_value <= 20:
                    treatment['cost_level'] = "low"
                    treatment['cost_icon'] = "💰"
                elif cost_value <= 50:
                    treatment['cost_level'] = "medium"
                    treatment['cost_icon'] = "💰💰"
                else:
                    treatment['cost_level'] = "high"
                    treatment['cost_icon'] = "💰💰💰"
        
        return treatments
