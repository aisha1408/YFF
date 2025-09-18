"""
Command-line interface for the Sustainable Pesticide & Fertilizer Recommendation System.
Provides a simple CLI for image analysis and treatment recommendations.
"""

import click
import json
import yaml
from pathlib import Path
from typing import Optional
from .inference import InferenceEngine
from .recommender import RecommendationEngine
from .formatter import ResponseFormatter


class PlantCareCLI:
    """Command-line interface for the plant care system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the CLI with configuration."""
        self.config_path = config_path
        self.inference_engine = InferenceEngine(config_path)
        self.recommendation_engine = RecommendationEngine("diseases.yml", config_path)
        self.formatter = ResponseFormatter(config_path)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def analyze_image(
        self,
        image_path: str,
        crop_type: Optional[str] = None,
        growth_stage: Optional[str] = None,
        location: Optional[str] = None,
        language: str = "en",
        output_format: str = "json"
    ) -> dict:
        """
        Analyze a plant image and provide recommendations.
        
        Args:
            image_path: Path to the image file
            crop_type: Optional crop type
            growth_stage: Optional growth stage
            location: Optional location
            language: Farmer's preferred language
            output_format: Output format (json, text, table)
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Process image through inference
            inference_result = self.inference_engine.process_image(image_data, Path(image_path).name)
            
            # Get disease information
            disease_id = inference_result["disease"]["id"]
            confidence = inference_result["disease"]["confidence"]
            
            # Generate recommendations
            recommendations = self.recommendation_engine.get_recommendations(
                disease_id=disease_id,
                confidence=confidence,
                crop_type=crop_type,
                growth_stage=growth_stage,
                location=location,
                farmer_language=language
            )
            
            # Format complete response
            response = self.formatter.format_detection_response(
                inference_result=inference_result,
                recommendations=recommendations,
                farmer_language=language
            )
            
            # Add visual indicators
            response["recommended_treatments"] = self.formatter.add_visual_indicators(
                response["recommended_treatments"]
            )
            
            return response
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Analysis failed: {str(e)}",
                "image_path": image_path
            }
    
    def get_treatment_info(self, disease_id: str, language: str = "en") -> dict:
        """
        Get treatment information for a specific disease.
        
        Args:
            disease_id: Disease identifier
            language: Farmer's preferred language
            
        Returns:
            Treatment information dictionary
        """
        try:
            treatment_data = self.recommendation_engine.get_treatment_by_id(disease_id)
            
            if not treatment_data:
                return {
                    "error": True,
                    "message": f"Treatment not found for disease: {disease_id}"
                }
            
            # Format response
            response = self.formatter.format_treatment_lookup_response(
                treatment_data=treatment_data,
                farmer_language=language
            )
            
            # Add visual indicators
            response["treatments"] = self.formatter.add_visual_indicators(response["treatments"])
            
            return response
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to get treatment info: {str(e)}"
            }
    
    def list_diseases(self) -> dict:
        """
        List all available diseases in the system.
        
        Returns:
            Dictionary with list of diseases
        """
        try:
            diseases = []
            for disease_id, disease_info in self.recommendation_engine.diseases_db.items():
                diseases.append({
                    "id": disease_id,
                    "name": disease_info["name"],
                    "remedy_count": len(disease_info.get("remedies", []))
                })
            
            return {"diseases": diseases}
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to list diseases: {str(e)}"
            }
    
    def validate_dosage(
        self,
        disease_id: str,
        remedy_name: str,
        requested_dosage: str
    ) -> dict:
        """
        Validate requested dosage against anti-overuse rules.
        
        Args:
            disease_id: Disease identifier
            remedy_name: Name of the remedy
            requested_dosage: Requested dosage string
            
        Returns:
            Validation result dictionary
        """
        try:
            result = self.recommendation_engine.validate_dosage(
                disease_id=disease_id,
                remedy_name=remedy_name,
                requested_dosage=requested_dosage
            )
            return result
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Dosage validation failed: {str(e)}"
            }
    
    def format_output(self, data: dict, output_format: str) -> str:
        """
        Format output data according to the specified format.
        
        Args:
            data: Data to format
            output_format: Output format (json, text, table)
            
        Returns:
            Formatted string
        """
        if output_format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif output_format == "text":
            return self._format_text_output(data)
        
        elif output_format == "table":
            return self._format_table_output(data)
        
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _format_text_output(self, data: dict) -> str:
        """Format data as human-readable text."""
        if data.get("error"):
            return f"Error: {data['message']}"
        
        output = []
        
        # Disease information
        if "disease" in data:
            disease = data["disease"]
            output.append(f"🌱 Disease: {disease['name']}")
            if 'confidence' in disease:
                output.append(f"📊 Confidence: {disease['confidence']:.1%}")
            output.append("")
        
        # Treatments
        if "recommended_treatments" in data:
            treatments = data["recommended_treatments"]
            if treatments:
                output.append("💊 Treatment Recommendations:")
                output.append("=" * 50)
                
                for i, treatment in enumerate(treatments, 1):
                    output.append(f"\n{i}. {treatment['name']} ({treatment['type'].upper()})")
                    output.append(f"   Dosage: {treatment['dosage']}")
                    output.append(f"   Frequency: {treatment['frequency']}")
                    output.append(f"   Best Time: {treatment['best_time']}")
                    output.append(f"   Cost: {treatment['cost_estimate_per_hectare']}")
                    
                    if treatment['safety'].get('PPE'):
                        output.append(f"   PPE Required: {', '.join(treatment['safety']['PPE'])}")
                    
                    if treatment['safety'].get('warning'):
                        output.append(f"   ⚠️  Warning: {treatment['safety']['warning']}")
            else:
                output.append("No specific treatments recommended.")
        
        # Note: SDG information is available in the separate SDG UI
        
        # Summary
        if "notes" in data:
            output.append(f"\n📝 Summary: {data['notes']}")
        
        # Warnings
        if "uncertainty_warning" in data and data["uncertainty_warning"]:
            output.append(f"\n⚠️  {data['uncertainty_warning']}")
        
        return "\n".join(output)
    
    def _format_table_output(self, data: dict) -> str:
        """Format data as a table (simplified version)."""
        if data.get("error"):
            return f"Error: {data['message']}"
        
        output = []
        
        # Disease information table
        if "disease" in data:
            disease = data["disease"]
            output.append("DISEASE DETECTION")
            output.append("=" * 50)
            output.append(f"Name: {disease['name']}")
            output.append(f"Confidence: {disease['confidence']:.1%}")
            output.append("")
        
        # Treatments table
        if "recommended_treatments" in data:
            treatments = data["recommended_treatments"]
            if treatments:
                output.append("TREATMENT RECOMMENDATIONS")
                output.append("=" * 50)
                
                for i, treatment in enumerate(treatments, 1):
                    output.append(f"\n{i}. {treatment['name']}")
                    output.append(f"   Type: {treatment['type'].upper()}")
                    output.append(f"   Dosage: {treatment['dosage']}")
                    output.append(f"   Frequency: {treatment['frequency']}")
                    output.append(f"   Cost: {treatment['cost_estimate_per_hectare']}")
        
        return "\n".join(output)


# Click CLI commands
@click.group()
@click.option('--config', default='config.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Sustainable Pesticide & Fertilizer Recommendation System CLI."""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = PlantCareCLI(config)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--crop-type', help='Type of crop (e.g., Tomato, Rice)')
@click.option('--growth-stage', type=click.Choice(['seedling', 'vegetative', 'flowering', 'fruiting', 'mature']), help='Growth stage')
@click.option('--location', help='Geographic location')
@click.option('--language', default='en', type=click.Choice(['en', 'es', 'fr', 'hi', 'pt']), help='Farmer language')
@click.option('--output', 'output_format', default='json', type=click.Choice(['json', 'text', 'table']), help='Output format')
@click.pass_context
def analyze(ctx, image_path, crop_type, growth_stage, location, language, output_format):
    """Analyze a plant image for diseases and get treatment recommendations."""
    cli_instance = ctx.obj['cli']
    
    result = cli_instance.analyze_image(
        image_path=image_path,
        crop_type=crop_type,
        growth_stage=growth_stage,
        location=location,
        language=language,
        output_format=output_format
    )
    
    click.echo(cli_instance.format_output(result, output_format))


@cli.command()
@click.argument('disease_id')
@click.option('--language', default='en', type=click.Choice(['en', 'es', 'fr', 'hi', 'pt']), help='Farmer language')
@click.option('--output', 'output_format', default='json', type=click.Choice(['json', 'text', 'table']), help='Output format')
@click.pass_context
def treatment(ctx, disease_id, language, output_format):
    """Get treatment information for a specific disease."""
    cli_instance = ctx.obj['cli']
    
    result = cli_instance.get_treatment_info(disease_id, language)
    
    click.echo(cli_instance.format_output(result, output_format))


@cli.command()
@click.option('--output', 'output_format', default='json', type=click.Choice(['json', 'text', 'table']), help='Output format')
@click.pass_context
def diseases(ctx, output_format):
    """List all available diseases in the system."""
    cli_instance = ctx.obj['cli']
    
    result = cli_instance.list_diseases()
    
    click.echo(cli_instance.format_output(result, output_format))


@cli.command()
@click.argument('disease_id')
@click.argument('remedy_name')
@click.argument('requested_dosage')
@click.option('--output', 'output_format', default='json', type=click.Choice(['json', 'text', 'table']), help='Output format')
@click.pass_context
def validate(ctx, disease_id, remedy_name, requested_dosage, output_format):
    """Validate dosage against anti-overuse rules."""
    cli_instance = ctx.obj['cli']
    
    result = cli_instance.validate_dosage(disease_id, remedy_name, requested_dosage)
    
    click.echo(cli_instance.format_output(result, output_format))


if __name__ == '__main__':
    cli()
