# Installation Guide

## Quick Start

### Option 1: Basic Installation (Recommended)
```bash
# Install core dependencies only
pip install -r requirements.txt

# Run the system (will use mock mode)
python main.py
```

### Option 2: Full Installation with ML Support
```bash
# Install core dependencies
pip install -r requirements.txt

# Install ML dependencies (optional)
pip install -r requirements-ml.txt

# Run the system
python main.py
```

### Option 3: Using setup.py
```bash
# Install as a package
pip install -e .

# Or with ML support
pip install -e .[ml]
```

## Troubleshooting Common Issues

### 1. Python Version Issues

**Error**: `ERROR: Package requires a different Python`
**Solution**: Ensure you're using Python 3.8 or higher
```bash
python --version
# Should show Python 3.8.x or higher

# If not, install Python 3.8+ from python.org
```

### 2. TensorFlow Installation Issues

**Error**: `ERROR: Could not find a version that satisfies the requirement tensorflow`
**Solutions**:

**Option A**: Skip TensorFlow (use mock mode)
```bash
# Install without ML dependencies
pip install -r requirements.txt
# The system will automatically use mock mode
```

**Option B**: Install TensorFlow separately
```bash
# For CPU only
pip install tensorflow

# For GPU support (if you have CUDA)
pip install tensorflow-gpu
```

**Option C**: Use conda instead of pip
```bash
conda install tensorflow
```

### 3. OpenCV Installation Issues

**Error**: `ERROR: Could not find a version that satisfies the requirement opencv-python`
**Solutions**:

**Option A**: Skip OpenCV (heatmaps won't work)
```bash
pip install -r requirements.txt
# System will work but without Grad-CAM heatmaps
```

**Option B**: Install OpenCV separately
```bash
pip install opencv-python
```

**Option C**: Use conda
```bash
conda install opencv
```

### 4. Pillow Installation Issues

**Error**: `ERROR: Failed building wheel for Pillow`
**Solution**:
```bash
# Install system dependencies first (Ubuntu/Debian)
sudo apt-get install libjpeg-dev zlib1g-dev

# Then install Pillow
pip install pillow
```

### 5. NumPy Installation Issues

**Error**: `ERROR: Failed building wheel for numpy`
**Solution**:
```bash
# Install pre-compiled wheel
pip install --only-binary=all numpy

# Or use conda
conda install numpy
```

### 6. Permission Issues

**Error**: `ERROR: Could not install packages due to an EnvironmentError`
**Solutions**:

**Option A**: Use user installation
```bash
pip install --user -r requirements.txt
```

**Option B**: Use virtual environment (recommended)
```bash
# Create virtual environment
python -m venv plant_care_env

# Activate it
# On Windows:
plant_care_env\Scripts\activate
# On macOS/Linux:
source plant_care_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 7. Windows-Specific Issues

**Error**: `Microsoft Visual C++ 14.0 is required`
**Solution**:
1. Install Microsoft Visual C++ Build Tools
2. Or use conda instead of pip:
```bash
conda install -c conda-forge pillow numpy pyyaml click
```

### 8. macOS-Specific Issues

**Error**: `clang: error: unsupported option '-fopenmp'`
**Solution**:
```bash
# Install with conda instead
conda install -c conda-forge pillow numpy pyyaml click
```

## Minimal Installation (No ML Dependencies)

If you want to run the system without any ML dependencies (mock mode only):

```bash
# Install only essential packages
pip install pillow pyyaml click python-dotenv

# Run the system
python main.py
```

## Verification

After installation, verify everything works:

```bash
# Test basic functionality
python main.py diseases

# Test image analysis (with a sample image)
python main.py analyze sample_image.jpg --output text
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- 1GB disk space

### Recommended Requirements
- Python 3.9+
- 4GB RAM
- 2GB disk space
- GPU (for real model inference)

### Supported Operating Systems
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+
- CentOS 7+

## Getting Help

If you're still having issues:

1. **Check Python version**: `python --version`
2. **Check pip version**: `pip --version`
3. **Try upgrading pip**: `pip install --upgrade pip`
4. **Check for conflicting packages**: `pip list`
5. **Try installing in a fresh virtual environment**

## Alternative Installation Methods

### Using Conda
```bash
# Create conda environment
conda create -n plant_care python=3.9

# Activate environment
conda activate plant_care

# Install packages
conda install -c conda-forge pillow numpy pyyaml click python-dotenv

# Optional: Install ML packages
conda install -c conda-forge tensorflow opencv
```

### Using Docker (if you have Docker installed)
```bash
# Create a simple Dockerfile
cat > Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
EOF

# Build and run
docker build -t plant-care .
docker run -it plant-care
```
