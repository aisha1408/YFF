"""
Main entry point for the Sustainable Pesticide & Fertilizer Recommendation System.
Provides both CLI and programmatic interfaces.
"""

import sys
import os
import yaml
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.cli import PlantCareCLI, cli

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the CLI application."""
    try:
        # Load configuration
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        app_config = config['app']
        
        logger.info("Starting Sustainable Pesticide & Fertilizer Recommendation System")
        logger.info(f"Mock mode: {config['model']['mock_mode']}")
        logger.info(f"Debug mode: {app_config['debug']}")
        logger.info(f"Output format: {app_config['output_format']}")
        
        # Run the CLI
        cli()
        
    except FileNotFoundError:
        logger.error("Configuration file 'config.yaml' not found")
        raise
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


def analyze_image_programmatically(
    image_path: str,
    crop_type: str = None,
    growth_stage: str = None,
    location: str = None,
    language: str = "en"
) -> dict:
    """
    Analyze a plant image programmatically.
    
    Args:
        image_path: Path to the image file
        crop_type: Optional crop type
        growth_stage: Optional growth stage
        location: Optional location
        language: Farmer's preferred language
        
    Returns:
        Analysis results dictionary
    """
    cli_instance = PlantCareCLI()
    return cli_instance.analyze_image(
        image_path=image_path,
        crop_type=crop_type,
        growth_stage=growth_stage,
        location=location,
        language=language
    )


def get_treatment_info_programmatically(disease_id: str, language: str = "en") -> dict:
    """
    Get treatment information programmatically.
    
    Args:
        disease_id: Disease identifier
        language: Farmer's preferred language
        
    Returns:
        Treatment information dictionary
    """
    cli_instance = PlantCareCLI()
    return cli_instance.get_treatment_info(disease_id, language)


if __name__ == "__main__":
    main()
