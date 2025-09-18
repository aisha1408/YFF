/**
 * Sustainable Pesticide & Fertilizer Recommendation System - Frontend JavaScript
 * Handles image upload, API communication, and result display
 */

class PlantCareApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentImage = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File upload handling
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');
        const removeImageBtn = document.getElementById('removeImage');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        const modalClose = document.getElementById('modalClose');

        // Upload area click
        uploadArea.addEventListener('click', () => {
            if (!this.currentImage) {
                imageInput.click();
            }
        });

        // File input change
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // Remove image
        removeImageBtn.addEventListener('click', () => {
            this.removeImage();
        });

        // Analyze button
        analyzeBtn.addEventListener('click', () => {
            this.analyzeImage();
        });

        // New analysis button
        newAnalysisBtn.addEventListener('click', () => {
            this.resetToUpload();
        });

        // Modal close
        modalClose.addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('safetyModal');
            if (e.target === modal) {
                this.closeModal();
            }
        });
    }

    handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid image file (JPEG or PNG)');
            return;
        }

        // Validate file size (8MB limit)
        const maxSize = 8 * 1024 * 1024; // 8MB in bytes
        if (file.size > maxSize) {
            this.showError('File size must be less than 8MB');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.currentImage = file;
            this.showImagePreview(e.target.result);
            this.enableAnalyzeButton();
        };
        reader.readAsDataURL(file);
    }

    showImagePreview(imageSrc) {
        const uploadArea = document.getElementById('uploadArea');
        const imagePreview = document.getElementById('imagePreview');
        const previewImage = document.getElementById('previewImage');

        uploadArea.style.display = 'none';
        previewImage.src = imageSrc;
        imagePreview.style.display = 'block';
    }

    removeImage() {
        this.currentImage = null;
        
        const uploadArea = document.getElementById('uploadArea');
        const imagePreview = document.getElementById('imagePreview');
        const imageInput = document.getElementById('imageInput');

        uploadArea.style.display = 'block';
        imagePreview.style.display = 'none';
        imageInput.value = '';
        this.disableAnalyzeButton();
    }

    enableAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = false;
    }

    disableAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = true;
    }

    async analyzeImage() {
        if (!this.currentImage) {
            this.showError('Please select an image first');
            return;
        }

        this.showLoading();

        try {
            const formData = new FormData();
            formData.append('file', this.currentImage);
            
            // Add optional metadata
            const cropType = document.getElementById('cropType').value;
            const growthStage = document.getElementById('growthStage').value;
            const location = document.getElementById('location').value;
            const language = document.getElementById('language').value;

            if (cropType) formData.append('crop_type', cropType);
            if (growthStage) formData.append('growth_stage', growthStage);
            if (location) formData.append('location', location);
            formData.append('farmer_language', language);

            const response = await fetch(`${this.apiBaseUrl}/api/detect`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const result = await response.json();
            this.displayResults(result);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
            this.showUpload();
        }
    }

    displayResults(result) {
        this.showResults();
        
        // Display disease information
        this.displayDiseaseInfo(result.disease);
        
        // Display heatmap if available
        this.displayHeatmap(result.supporting_heatmap_base64);
        
        // Display treatments
        this.displayTreatments(result.recommended_treatments);
        
        // SDG information is now in separate UI
        
        // Display summary
        this.displaySummary(result.notes);
        
        // Display warnings if any
        this.displayWarnings(result);
    }

    displayDiseaseInfo(disease) {
        const diseaseName = document.getElementById('diseaseName');
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceText = document.getElementById('confidenceText');

        diseaseName.textContent = disease.name;
        
        const confidence = Math.round(disease.confidence * 100);
        confidenceText.textContent = `${confidence}%`;
        
        // Set confidence bar
        confidenceFill.style.width = `${confidence}%`;
        
        // Set confidence level class
        confidenceFill.className = 'confidence-fill';
        if (confidence >= 70) {
            confidenceFill.classList.add('high');
        } else if (confidence >= 50) {
            confidenceFill.classList.add('medium');
        } else {
            confidenceFill.classList.add('low');
        }
    }

    displayHeatmap(heatmapBase64) {
        const heatmapContainer = document.getElementById('heatmapContainer');
        const heatmapImage = document.getElementById('heatmapImage');

        if (heatmapBase64) {
            heatmapImage.src = `data:image/png;base64,${heatmapBase64}`;
            heatmapContainer.style.display = 'block';
        } else {
            heatmapContainer.style.display = 'none';
        }
    }

    displayTreatments(treatments) {
        const organicList = document.getElementById('organicList');
        const chemicalList = document.getElementById('chemicalList');
        const organicSection = document.getElementById('organicTreatments');
        const chemicalSection = document.getElementById('chemicalTreatments');

        // Clear existing treatments
        organicList.innerHTML = '';
        chemicalList.innerHTML = '';

        // Separate organic and chemical treatments
        const organicTreatments = treatments.filter(t => t.type === 'organic');
        const chemicalTreatments = treatments.filter(t => t.type === 'chemical');

        // Display organic treatments
        if (organicTreatments.length > 0) {
            organicSection.style.display = 'block';
            organicTreatments.forEach(treatment => {
                const treatmentCard = this.createTreatmentCard(treatment);
                organicList.appendChild(treatmentCard);
            });
        } else {
            organicSection.style.display = 'none';
        }

        // Display chemical treatments
        if (chemicalTreatments.length > 0) {
            chemicalSection.style.display = 'block';
            chemicalTreatments.forEach(treatment => {
                const treatmentCard = this.createTreatmentCard(treatment);
                chemicalList.appendChild(treatmentCard);
            });
        } else {
            chemicalSection.style.display = 'none';
        }
    }

    createTreatmentCard(treatment) {
        const card = document.createElement('div');
        card.className = `treatment-card ${treatment.type}`;
        
        const safetyLevel = treatment.safety_level || 'low';
        const safetyIcon = treatment.safety_icon || '✅';
        const costIcon = treatment.cost_icon || '💰';
        const typeIcon = treatment.icon || (treatment.type === 'organic' ? '🌱' : '⚠️');

        card.innerHTML = `
            <div class="treatment-header">
                <div class="treatment-name">
                    <span>${typeIcon}</span>
                    ${treatment.name}
                </div>
                <div class="treatment-badge ${treatment.type}">
                    ${treatment.type}
                </div>
            </div>
            
            <div class="treatment-details">
                <div class="detail-item">
                    <div class="detail-label">Dosage</div>
                    <div class="detail-value">${treatment.dosage}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Application Volume</div>
                    <div class="detail-value">${treatment.application_volume}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Frequency</div>
                    <div class="detail-value">${treatment.frequency}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Best Time</div>
                    <div class="detail-value">${treatment.best_time}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Cost Estimate</div>
                    <div class="detail-value">${costIcon} ${treatment.cost_estimate_per_hectare}</div>
                </div>
            </div>
            
            <div class="treatment-safety">
                <div class="safety-header">
                    <span>${safetyIcon}</span>
                    Safety Information
                </div>
                ${treatment.safety.PPE && treatment.safety.PPE.length > 0 ? `
                    <div class="ppe-list">
                        ${treatment.safety.PPE.map(ppe => `<span class="ppe-item">${ppe}</span>`).join('')}
                    </div>
                ` : ''}
                ${treatment.safety.warning ? `
                    <div class="safety-warning">
                        <strong>Warning:</strong> ${treatment.safety.warning}
                    </div>
                ` : ''}
                ${treatment.safety.pre_harvest_interval ? `
                    <div class="detail-item">
                        <div class="detail-label">Pre-harvest Interval</div>
                        <div class="detail-value">${treatment.safety.pre_harvest_interval} days</div>
                    </div>
                ` : ''}
            </div>
        `;

        // Add click handler for safety modal
        card.addEventListener('click', () => {
            this.showSafetyModal(treatment);
        });

        return card;
    }

    // SDG information is now displayed in separate UI (sdg_ui.html)

    displaySummary(summary) {
        const summaryText = document.getElementById('summaryText');
        summaryText.textContent = summary;
    }

    displayWarnings(result) {
        const warningsSection = document.getElementById('warningsSection');
        const warningsList = document.getElementById('warningsList');
        
        const warnings = [];
        
        if (result.uncertainty_warning) {
            warnings.push(result.uncertainty_warning);
        }
        
        if (result.image_warning) {
            warnings.push(result.image_warning);
        }

        if (warnings.length > 0) {
            warningsList.innerHTML = '';
            warnings.forEach(warning => {
                const warningItem = document.createElement('div');
                warningItem.className = 'warning-item';
                warningItem.textContent = warning;
                warningsList.appendChild(warningItem);
            });
            warningsSection.style.display = 'block';
        } else {
            warningsSection.style.display = 'none';
        }
    }

    showSafetyModal(treatment) {
        const modal = document.getElementById('safetyModal');
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <h4>${treatment.name}</h4>
            <div class="treatment-details">
                <div class="detail-item">
                    <div class="detail-label">Type</div>
                    <div class="detail-value">${treatment.type.charAt(0).toUpperCase() + treatment.type.slice(1)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Dosage</div>
                    <div class="detail-value">${treatment.dosage}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Application Volume</div>
                    <div class="detail-value">${treatment.application_volume}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Frequency</div>
                    <div class="detail-value">${treatment.frequency}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Best Time</div>
                    <div class="detail-value">${treatment.best_time}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Cost Estimate</div>
                    <div class="detail-value">${treatment.cost_estimate_per_hectare}</div>
                </div>
            </div>
            
            <div class="treatment-safety">
                <h5>Safety Information</h5>
                ${treatment.safety.PPE && treatment.safety.PPE.length > 0 ? `
                    <p><strong>Required PPE:</strong> ${treatment.safety.PPE.join(', ')}</p>
                ` : ''}
                ${treatment.safety.disposal ? `
                    <p><strong>Disposal:</strong> ${treatment.safety.disposal}</p>
                ` : ''}
                ${treatment.safety.warning ? `
                    <div class="safety-warning">
                        <strong>Warning:</strong> ${treatment.safety.warning}
                    </div>
                ` : ''}
                ${treatment.safety.pre_harvest_interval ? `
                    <p><strong>Pre-harvest Interval:</strong> ${treatment.safety.pre_harvest_interval} days</p>
                ` : ''}
            </div>
        `;
        
        modal.style.display = 'block';
    }

    closeModal() {
        const modal = document.getElementById('safetyModal');
        modal.style.display = 'none';
    }

    showLoading() {
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('loadingSection').style.display = 'block';
    }

    showResults() {
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
    }

    showUpload() {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('uploadSection').style.display = 'block';
    }

    resetToUpload() {
        this.removeImage();
        this.showUpload();
        
        // Clear form fields
        document.getElementById('cropType').value = '';
        document.getElementById('growthStage').value = '';
        document.getElementById('location').value = '';
        document.getElementById('language').value = 'en';
    }

    showError(message) {
        // Simple error display - in production, you might want a more sophisticated error handling
        alert(`Error: ${message}`);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PlantCareApp();
});
