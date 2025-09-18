#!/usr/bin/env python3
"""
Simple web server for Plant Care System
Handles image uploads and runs analysis
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from main import analyze_image_programmatically

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlantCareHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_html()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/analyze':
            self.handle_analyze()
        else:
            self.send_error(404, "Not Found")

    def serve_html(self):
        """Serve the main HTML page"""
        try:
            with open('plant_care_website.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "HTML file not found")
        except Exception as e:
            logger.error(f"Error serving HTML: {e}")
            self.send_error(500, f"Error serving page: {str(e)}")

    def handle_analyze(self):
        """Handle image analysis requests"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Content-Type must be multipart/form-data")
                return

            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No content provided")
                return

            body = self.rfile.read(content_length)
            
            # Parse multipart data (simplified)
            boundary = content_type.split('boundary=')[1]
            parts = body.split(f'--{boundary}'.encode())
            
            image_data = None
            crop_type = None
            growth_stage = None
            location = None
            language = 'en'
            
            for part in parts:
                if b'name="file"' in part:
                    # Extract image data
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        image_data = part[header_end + 4:]
                        # Remove trailing boundary markers
                        if image_data.endswith(b'\r\n'):
                            image_data = image_data[:-2]
                elif b'name="crop_type"' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        crop_type = part[header_end + 4:].decode('utf-8').strip()
                        if crop_type.endswith('\r\n'):
                            crop_type = crop_type[:-2]
                elif b'name="growth_stage"' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        growth_stage = part[header_end + 4:].decode('utf-8').strip()
                        if growth_stage.endswith('\r\n'):
                            growth_stage = growth_stage[:-2]
                elif b'name="location"' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        location = part[header_end + 4:].decode('utf-8').strip()
                        if location.endswith('\r\n'):
                            location = location[:-2]
                elif b'name="language"' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        language = part[header_end + 4:].decode('utf-8').strip()
                        if language.endswith('\r\n'):
                            language = language[:-2]

            if not image_data:
                self.send_error(400, "No image file provided")
                return

            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_image_path = temp_file.name

            try:
                # Analyze the image using our programmatic function
                result = analyze_image_programmatically(
                    temp_image_path,
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                    location=location,
                    language=language
                )

                if result:
                    # Format the response for the frontend
                    response = {
                        "disease": {
                            "name": result.get("disease", {}).get("name", "Unknown"),
                            "confidence": result.get("disease", {}).get("confidence", 0.0)
                        },
                        "recommended_treatments": result.get("recommended_treatments", []),
                        "notes": result.get("notes", ""),
                        "uncertainty_warning": result.get("uncertainty_warning", ""),
                        "image_warning": result.get("image_warning", ""),
                        "supporting_heatmap_base64": result.get("supporting_heatmap_base64", "")
                    }
                    self.send_json_response(response)
                else:
                    self.send_error(500, "Analysis failed")
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_image_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"Error in analyze handler: {e}")
            self.send_error(500, f"Analysis failed: {str(e)}")

    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, PlantCareHandler)
    
    logger.info(f"Starting Plant Care web server on port {port}")
    logger.info(f"Open http://localhost:{port} to view the website")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Plant Care System Web Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    
    run_server(args.port)
