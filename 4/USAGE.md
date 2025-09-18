# Usage Guide

## Command-Line Interface

The Sustainable Pesticide & Fertilizer Recommendation System provides a comprehensive command-line interface for analyzing plant images and getting treatment recommendations.

### Basic Usage

```bash
python main.py [COMMAND] [OPTIONS]
```

### Available Commands

#### 1. Analyze Plant Image

Analyze a plant image for diseases and get treatment recommendations.

```bash
python main.py analyze IMAGE_PATH [OPTIONS]
```

**Options:**
- `--crop-type TEXT`: Type of crop (e.g., Tomato, Rice, Wheat)
- `--growth-stage [seedling|vegetative|flowering|fruiting|mature]`: Growth stage
- `--location TEXT`: Geographic location
- `--language [en|es|fr|hi|pt]`: Farmer's preferred language (default: en)
- `--output [json|text|table]`: Output format (default: json)

**Examples:**
```bash
# Basic analysis
python main.py analyze plant_image.jpg

# With metadata
python main.py analyze plant_image.jpg \
  --crop-type Tomato \
  --growth-stage flowering \
  --location California \
  --language en

# Text output
python main.py analyze plant_image.jpg --output text

# Table output
python main.py analyze plant_image.jpg --output table
```

#### 2. Get Treatment Information

Get treatment information for a specific disease.

```bash
python main.py treatment DISEASE_ID [OPTIONS]
```

**Options:**
- `--language [en|es|fr|hi|pt]`: Farmer's preferred language (default: en)
- `--output [json|text|table]`: Output format (default: json)

**Examples:**
```bash
# Get treatment for powdery mildew
python main.py treatment powdery_mildew

# In Spanish
python main.py treatment powdery_mildew --language es --output text

# Get treatment for bacterial spot
python main.py treatment bacterial_spot --output table
```

#### 3. List Available Diseases

List all diseases available in the system.

```bash
python main.py diseases [OPTIONS]
```

**Options:**
- `--output [json|text|table]`: Output format (default: json)

**Examples:**
```bash
# List all diseases
python main.py diseases

# Table format
python main.py diseases --output table
```

#### 4. Validate Dosage

Validate a requested dosage against anti-overuse rules.

```bash
python main.py validate DISEASE_ID REMEDY_NAME REQUESTED_DOSAGE [OPTIONS]
```

**Options:**
- `--output [json|text|table]`: Output format (default: json)

**Examples:**
```bash
# Validate dosage
python main.py validate powdery_mildew "Neem oil 1% spray" "10 ml per L"

# Check if high dosage is allowed
python main.py validate powdery_mildew "Neem oil 1% spray" "20 ml per L"
```

### Output Formats

#### JSON Output (Default)
Structured data format suitable for programmatic use:

```json
{
  "disease": {
    "id": "powdery_mildew",
    "name": "Powdery Mildew",
    "confidence": 0.92
  },
  "recommended_treatments": [
    {
      "type": "organic",
      "name": "Neem oil 1% spray",
      "dosage": "10 ml per L",
      "frequency": "Every 7 days (max 4 times/season)",
      "safety": {
        "PPE": ["gloves", "mask"],
        "warning": "Safe for pollinators if not applied during bloom"
      }
    }
  ],
  "sdg_alignment": ["SDG 12: Responsible Consumption & Production"],
  "notes": "Detected: Powdery Mildew | Try: Neem oil 1% spray (10 ml per L)"
}
```

#### Text Output
Human-readable format for terminal display:

```
🌱 Disease: Powdery Mildew
📊 Confidence: 92.0%

💊 Treatment Recommendations:
==================================================

1. Neem oil 1% spray (ORGANIC)
   Dosage: 10 ml per L
   Frequency: Every 7 days (max 4 times/season)
   Best Time: Early morning or late evening, avoid flowering
   Cost: USD 12
   PPE Required: gloves, mask
   ⚠️  Warning: Safe for pollinators if not applied during bloom

🌍 Sustainable Development Goals:
   • SDG 12: Responsible Consumption & Production
   • SDG 3: Good Health & Well-being
   • SDG 15: Life on Land

📝 Summary: Detected: Powdery Mildew | Try: Neem oil 1% spray (10 ml per L)
```

#### Table Output
Structured table format:

```
DISEASE DETECTION
==================================================
Name: Powdery Mildew
Confidence: 92.0%

TREATMENT RECOMMENDATIONS
==================================================

1. Neem oil 1% spray
   Type: ORGANIC
   Dosage: 10 ml per L
   Frequency: Every 7 days (max 4 times/season)
   Cost: USD 12
```

## Programmatic Usage

You can also use the system programmatically in your Python code:

```python
from main import analyze_image_programmatically, get_treatment_info_programmatically

# Analyze an image
result = analyze_image_programmatically(
    image_path="plant_image.jpg",
    crop_type="Tomato",
    growth_stage="flowering",
    location="California",
    language="en"
)

print(f"Detected: {result['disease']['name']}")
print(f"Confidence: {result['disease']['confidence']:.1%}")

# Get treatment information
treatment = get_treatment_info_programmatically("powdery_mildew", "en")
print(f"Treatments available: {len(treatment['treatments'])}")
```

## Configuration

The system behavior can be configured through `config.yaml`:

```yaml
# Model Configuration
model:
  mock_mode: true  # Set to false when model weights are available
  confidence_threshold: 0.7
  low_confidence_threshold: 0.5

# Image Processing
image:
  max_size_mb: 8
  min_dimensions: [224, 224]
  supported_formats: ["jpeg", "jpg", "png"]

# Anti-Overuse Protection
anti_overuse:
  max_applications_per_season: 4
  max_dosage_multiplier: 1.5
  require_confirmation_above: 1.2

# Application Settings
app:
  debug: true
  output_format: "json"  # Default output format
```

## Error Handling

The system provides clear error messages for common issues:

- **File not found**: "Analysis failed: [Errno 2] No such file or directory"
- **Invalid image format**: "Unsupported format. Supported: jpeg, jpg, png"
- **Image too small**: "Image too small. Minimum dimensions: 224x224"
- **File too large**: "File too large. Maximum size: 8 MB"
- **Unknown disease**: "Treatment not found for disease: unknown_disease"

## Examples

### Example 1: Basic Plant Analysis

```bash
# Analyze a tomato plant image
python main.py analyze tomato_leaf.jpg --crop-type Tomato --output text
```

### Example 2: Multilingual Support

```bash
# Get treatment information in Spanish
python main.py treatment powdery_mildew --language es --output text
```

### Example 3: Batch Processing

```bash
# Process multiple images (using shell scripting)
for image in images/*.jpg; do
  echo "Processing $image"
  python main.py analyze "$image" --output json > "results/$(basename "$image" .jpg).json"
done
```

### Example 4: Integration with Other Tools

```bash
# Use with jq for JSON processing
python main.py analyze plant.jpg --output json | jq '.disease.name'

# Save results to file
python main.py analyze plant.jpg --output text > analysis_report.txt
```

## Tips and Best Practices

1. **Image Quality**: Use clear, well-lit images of plant leaves for best results
2. **File Formats**: Supported formats are JPEG, JPG, and PNG
3. **Image Size**: Images should be at least 224x224 pixels
4. **Metadata**: Providing crop type, growth stage, and location improves recommendations
5. **Language**: Choose the appropriate language for your target users
6. **Output Format**: Use JSON for programmatic use, text for human reading
7. **Mock Mode**: The system runs in mock mode by default for testing

## Troubleshooting

### Common Issues

1. **"No such file or directory"**: Check that the image path is correct
2. **"Unsupported format"**: Convert your image to JPEG or PNG format
3. **"Image too small"**: Resize your image to at least 224x224 pixels
4. **"File too large"**: Compress your image to under 8MB
5. **"Analysis failed"**: Check that the image file is not corrupted

### Getting Help

- Run `python main.py --help` for general help
- Run `python main.py COMMAND --help` for command-specific help
- Check the logs for detailed error information
- Ensure all dependencies are installed correctly
