class ARCameraScanner {
    constructor() {
        this.stream = null;
        this.isSelecting = false;
        this.selectedRegion = null;
        this.analysisResult = null;
        this.confirmationData = null;
        
        this.initializeElements();
        this.bindEvents();
        this.checkCameraSupport();
    }
    
    initializeElements() {
        this.cameraFeed = document.getElementById('camera-feed');
        this.cameraCanvas = document.getElementById('camera-canvas');
        this.arOverlay = document.getElementById('ar-overlay');
        this.scanIndicator = document.getElementById('scan-indicator');
        this.selectionBox = document.getElementById('selection-box');
        this.detectedItemsContainer = document.getElementById('detected-items');
        
        // Controls
        this.startCameraBtn = document.getElementById('start-camera-btn');
        this.captureBtn = document.getElementById('capture-btn');
        this.selectRegionBtn = document.getElementById('select-region-btn');
        this.stopCameraBtn = document.getElementById('stop-camera-btn');
        this.imageUpload = document.getElementById('image-upload');
        
        // Results sections
        this.extractedSection = document.getElementById('extracted-section');
        this.fullTextDiv = document.getElementById('full-extracted-text');
        this.questionsList = document.getElementById('questions-list');
        this.complexitySelect = document.getElementById('complexity-select');
        this.languageSelect = document.getElementById('language-select');
    }
    
    bindEvents() {
        this.startCameraBtn.addEventListener('click', () => this.startCamera());
        this.captureBtn.addEventListener('click', () => this.captureImage());
        this.selectRegionBtn.addEventListener('click', () => this.toggleRegionSelection());
        this.stopCameraBtn.addEventListener('click', () => this.stopCamera());
        this.imageUpload.addEventListener('change', (e) => this.handleImageUpload(e));
        
        // Touch/click events for camera feed
        this.cameraFeed.addEventListener('click', (e) => this.handleCameraClick(e));
        this.cameraFeed.addEventListener('touchstart', (e) => this.handleCameraTouch(e));
    }
    
    async checkCameraSupport() {
        try {
            const response = await fetch('/api/camera-support');
            const support = await response.json();
            
            if (!support.camera_supported) {
                this.showCameraWarning(support);
            }
        } catch (error) {
            console.log('Camera support check failed:', error);
        }
    }
    
    showCameraWarning(support) {
        const warningDiv = document.getElementById('camera-warning');
        if (warningDiv) {
            warningDiv.style.display = 'block';
        }
        
        // Update scan text
        const scanText = document.getElementById('scan-text');
        if (scanText) {
            scanText.textContent = '📷 Camera not available - use image upload below';
        }
        
        // Disable camera button
        this.startCameraBtn.disabled = true;
        this.startCameraBtn.textContent = '📱 Camera Not Available';
    }
    
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'environment', // Use back camera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            this.cameraFeed.srcObject = this.stream;
            this.cameraFeed.style.display = 'block';
            
            // Update button states
            this.startCameraBtn.style.display = 'none';
            this.captureBtn.style.display = 'inline-block';
            this.selectRegionBtn.style.display = 'inline-block';
            this.stopCameraBtn.style.display = 'inline-block';
            
            this.scanIndicator.innerHTML = '<div class="scan-corners"></div><p>📸 Tap to scan or select region</p>';
            
        } catch (error) {
            console.error('Camera access error:', error);
            alert('Camera access denied or not available. Please use image upload instead.');
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.cameraFeed.style.display = 'none';
        
        // Reset button states
        this.startCameraBtn.style.display = 'inline-block';
        this.captureBtn.style.display = 'none';
        this.selectRegionBtn.style.display = 'none';
        this.stopCameraBtn.style.display = 'none';
        
        this.clearDetectedItems();
    }
    
    toggleRegionSelection() {
        this.isSelecting = !this.isSelecting;
        
        if (this.isSelecting) {
            this.selectRegionBtn.textContent = '❌ Cancel Selection';
            this.scanIndicator.innerHTML = '<p>🎯 Click and drag to select region</p>';
            this.arOverlay.style.cursor = 'crosshair';
        } else {
            this.selectRegionBtn.textContent = '🎯 Select Region';
            this.scanIndicator.innerHTML = '<div class="scan-corners"></div><p>📸 Tap to scan or select region</p>';
            this.arOverlay.style.cursor = 'default';
            this.hideSelectionBox();
        }
    }
    
    handleCameraClick(event) {
        if (this.isSelecting) {
            this.handleRegionSelection(event);
        } else {
            this.captureImage();
        }
    }
    
    handleCameraTouch(event) {
        event.preventDefault();
        if (this.isSelecting) {
            this.handleRegionSelection(event.touches[0]);
        } else {
            this.captureImage();
        }
    }
    
    handleRegionSelection(event) {
        const rect = this.cameraFeed.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        if (!this.selectedRegion) {
            // Start selection
            this.selectedRegion = { startX: x, startY: y };
            this.showSelectionBox(x, y, 0, 0);
        } else {
            // End selection
            const width = x - this.selectedRegion.startX;
            const height = y - this.selectedRegion.startY;
            
            this.selectedRegion.width = Math.abs(width);
            this.selectedRegion.height = Math.abs(height);
            this.selectedRegion.x = width > 0 ? this.selectedRegion.startX : x;
            this.selectedRegion.y = height > 0 ? this.selectedRegion.startY : y;
            
            this.captureImage(this.selectedRegion);
            this.toggleRegionSelection();
            this.selectedRegion = null;
        }
    }
    
    showSelectionBox(x, y, width, height) {
        this.selectionBox.style.display = 'block';
        this.selectionBox.style.left = `${x}px`;
        this.selectionBox.style.top = `${y}px`;
        this.selectionBox.style.width = `${width}px`;
        this.selectionBox.style.height = `${height}px`;
    }
    
    hideSelectionBox() {
        this.selectionBox.style.display = 'none';
    }
    
async captureImage(region = null) {
    try {
        // Show loading
        this.showARLoading('📸 Capturing and analyzing with AI Vision...');
        
        // Set up canvas
        const canvas = this.cameraCanvas;
        const ctx = canvas.getContext('2d');
        
        canvas.width = this.cameraFeed.videoWidth;
        canvas.height = this.cameraFeed.videoHeight;
        
        // Draw current frame
        ctx.drawImage(this.cameraFeed, 0, 0);
        
        // Convert canvas to base64 data URL
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
        
        console.log('[DEBUG] Canvas to data URL conversion completed');
        console.log('[DEBUG] Data URL length:', imageDataUrl.length);
        console.log('[DEBUG] Data URL header:', imageDataUrl.substring(0, 50));
        
        // Prepare form data for camera capture endpoint
        const formData = new FormData();
        formData.append('image_data', imageDataUrl);
        
        if (region) {
            formData.append('selected_region', JSON.stringify(region));
            console.log('[DEBUG] Added region data:', region);
        }
        
        console.log('[DEBUG] FormData prepared for camera capture');
        
        // Process the captured image
        await this.processCameraCapture(formData);
        
    } catch (error) {
        console.error('Capture error:', error);
        this.hideARLoading();
        alert('Image capture failed: ' + error.message);
    }
}

async handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        this.showARLoading('📷 Analyzing uploaded image with AI Vision...');
        
        console.log('[DEBUG] Processing uploaded file:', file.name, file.type, file.size);
        
        // For file uploads, use the analyze-educational-image endpoint
        const formData = new FormData();
        formData.append('image', file);
        
        console.log('[DEBUG] FormData prepared for image upload');
        
        // Process the uploaded image
        await this.processImageUpload(formData);
        
    } catch (error) {
        console.error('Upload error:', error);
        this.hideARLoading();
        alert('Image upload failed: ' + error.message);
    }
}

async processCameraCapture(formData) {
    try {
        this.updateLoadingProgress(20, 'Processing camera capture...');
        
        console.log('[DEBUG] Sending request to /api/process-camera-capture');
        
        const response = await fetch('/api/process-camera-capture', {
            method: 'POST',
            body: formData
        });
        
        console.log('[DEBUG] Response status:', response.status);
        console.log('[DEBUG] Response headers:', response.headers);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[ERROR] Response not OK:', response.status, errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('[DEBUG] Response parsed successfully');
        
        if (result.success) {
            this.updateLoadingProgress(60, 'Processing AI analysis results...');
            
            this.analysisResult = result.analysis;
            this.confirmationData = result.confirmation_data;
            
            this.updateLoadingProgress(80, 'Preparing intelligent confirmation...');
            
            console.log('Vision AI Analysis:', result.analysis);
            console.log('Confirmation Data:', result.confirmation_data);
            
            // Show intelligent confirmation interface
            this.showIntelligentConfirmation(result.confirmation_data);
            
            this.updateLoadingProgress(100, 'Ready for confirmation!');
            
            setTimeout(() => {
                this.hideARLoading();
            }, 500);
            
        } else {
            throw new Error(result.message || 'Camera capture analysis failed');
        }
        
    } catch (error) {
        console.error('Camera capture processing error:', error);
        this.hideARLoading();
        alert('Camera capture failed: ' + error.message);
    }
}

async processImageUpload(formData) {
    try {
        this.updateLoadingProgress(20, 'Analyzing uploaded image...');
        
        console.log('[DEBUG] Sending request to /api/analyze-educational-image');
        
        const response = await fetch('/api/analyze-educational-image', {
            method: 'POST',
            body: formData
        });
        
        console.log('[DEBUG] Upload response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[ERROR] Upload response not OK:', response.status, errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('[DEBUG] Upload response parsed successfully');
        
        if (result.success) {
            this.updateLoadingProgress(60, 'Processing AI analysis results...');
            
            this.analysisResult = result.analysis;
            this.confirmationData = result.confirmation_data;
            
            this.updateLoadingProgress(80, 'Preparing intelligent confirmation...');
            
            console.log('Vision AI Analysis:', result.analysis);
            console.log('Confirmation Data:', result.confirmation_data);
            
            // Show intelligent confirmation interface
            this.showIntelligentConfirmation(result.confirmation_data);
            
            this.updateLoadingProgress(100, 'Ready for confirmation!');
            
            setTimeout(() => {
                this.hideARLoading();
            }, 500);
            
        } else {
            throw new Error(result.message || 'Image analysis failed');
        }
        
    } catch (error) {
        console.error('Image upload processing error:', error);
        this.hideARLoading();
        alert('Image analysis failed: ' + error.message);
    }
}

// Remove the old processImage method and replace it with these two specific methods
// Also update the method calls in other parts of the code

// Update the existing method calls
// Replace this.processImage(formData, true) with this.processCameraCapture(formData)
// Replace this.processImage(formData, false) with this.processImageUpload(formData)

    
    async handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            this.showARLoading('📷 Analyzing uploaded image with AI Vision...');
            
            const formData = new FormData();
            formData.append('image', file);
            
            await this.processImage(formData, false); // false for file upload
            
        } catch (error) {
            console.error('Upload error:', error);
            this.hideARLoading();
            alert('Image upload failed: ' + error.message);
        }
    }
    
    async processImage(formData, isCamera = false) {
        try {
            this.updateLoadingProgress(20, 'Analyzing with AI Vision...');
            
            // Use the correct endpoint based on source
            const endpoint = isCamera ? '/api/process-camera-capture' : '/api/analyze-educational-image';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateLoadingProgress(60, 'Processing AI analysis results...');
                
                this.analysisResult = result.analysis;
                this.confirmationData = result.confirmation_data;
                
                this.updateLoadingProgress(80, 'Preparing intelligent confirmation...');
                
                console.log('Vision AI Analysis:', result.analysis);
                console.log('Confirmation Data:', result.confirmation_data);
                
                // Show intelligent confirmation interface
                this.showIntelligentConfirmation(result.confirmation_data);
                
                this.updateLoadingProgress(100, 'Ready for confirmation!');
                
                setTimeout(() => {
                    this.hideARLoading();
                }, 500);
                
            } else {
                throw new Error(result.message || 'Vision AI analysis failed');
            }
            
        } catch (error) {
            console.error('Processing error:', error);
            this.hideARLoading();
            alert('Image analysis failed: ' + error.message);
        }
    }
    
    showIntelligentConfirmation(confirmationData) {
        // Hide loading and show confirmation interface
        this.hideARLoading();
        
        // Create and show confirmation overlay
        this.createConfirmationOverlay(confirmationData);
    }
    
    createConfirmationOverlay(confirmationData) {
        // Remove any existing confirmation overlay
        const existingOverlay = document.getElementById('confirmation-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        const overlay = document.createElement('div');
        overlay.id = 'confirmation-overlay';
        overlay.className = 'confirmation-overlay';
        
        const detectedContent = confirmationData.detected_content;
        const recommendations = confirmationData.recommendations;
        const bestOption = recommendations.best_option;
        
        overlay.innerHTML = `
            <div class="confirmation-content">
                <h2>🤖 AI Vision Analysis Results</h2>
                <p class="confidence-info">Overall Confidence: ${(recommendations.confidence_score * 100).toFixed(0)}%</p>
                
                <div class="analysis-summary">
                    <h3>📋 What I Found</h3>
                    <div class="main-concept">
                        <h4>🎯 Main Concept</h4>
                        <div class="concept-card ${bestOption.type === 'concept' ? 'recommended' : ''}">
                            <div class="concept-header">
                                <span class="concept-title">${detectedContent.primary_concept.display_text}</span>
                                <span class="confidence-badge">${(detectedContent.primary_concept.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <p class="concept-description">${detectedContent.primary_concept.description}</p>
                        </div>
                    </div>
                    
                    ${detectedContent.questions.length > 0 ? `
                        <div class="detected-questions">
                            <h4>❓ Questions Found</h4>
                            ${detectedContent.questions.map((q, index) => `
                                <div class="question-card ${bestOption.type === 'question' && bestOption.content.text === q.text ? 'recommended' : ''}" data-type="question" data-index="${index}">
                                    <div class="question-header">
                                        <span class="question-type">${q.type.toUpperCase()}</span>
                                        <span class="confidence-badge">${(q.confidence * 100).toFixed(0)}%</span>
                                        ${q.can_solve ? '<span class="solvable-badge">🧮 Solvable</span>' : ''}
                                    </div>
                                    <div class="question-text">${q.display_text}</div>
                                    <div class="question-meta">
                                        <span>Subject: ${q.subject}</span>
                                        <span>Output: ${q.expected_output}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${detectedContent.topics.length > 0 ? `
                        <div class="detected-topics">
                            <h4>📚 Topics Found</h4>
                            ${detectedContent.topics.map((t, index) => `
                                <div class="topic-card ${bestOption.type === 'topic' && bestOption.content.name === t.name ? 'recommended' : ''}" data-type="topic" data-index="${index}">
                                    <div class="topic-header">
                                        <span class="topic-name">${t.display_text}</span>
                                        <span class="confidence-badge">${(t.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                    <div class="topic-description">${t.description}</div>
                                    <div class="educational-value">💡 ${t.educational_value}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="recommendation-section">
                    <h3>🎯 AI Recommendation</h3>
                    <div class="recommendation-card">
                        <div class="recommendation-header">
                            <span class="recommendation-title">Best Option: ${bestOption.type.toUpperCase()}</span>
                            <span class="recommendation-action">${recommendations.recommended_action}</span>
                        </div>
                        <p class="recommendation-reason">${bestOption.reason}</p>
                    </div>
                </div>
                
                <div class="input-section">
                    <h3>✏️ Confirm or Edit Input</h3>
                    <div class="input-group">
                        <label for="confirmed-input">Selected Input:</label>
                        <textarea id="confirmed-input" rows="3" placeholder="Edit or confirm the detected content...">${confirmationData.user_options.default_selection}</textarea>
                    </div>
                    <div class="options-row">
                        <select id="confirmed-complexity">
                            <option value="beginner">🟢 Beginner</option>
                            <option value="intermediate" selected>🟡 Intermediate</option>
                            <option value="advanced">🔴 Advanced</option>
                        </select>
                        <select id="confirmed-language">
                            <option value="english">🇺🇸 English</option>
                            <option value="hindi">🇮🇳 Hindi</option>
                            <option value="tamil">🇮🇳 Tamil</option>
                            <option value="bengali">🇮🇳 Bengali</option>
                        </select>
                    </div>
                </div>
                
                ${recommendations.processing_suggestions.length > 0 ? `
                    <div class="suggestions-section">
                        <h4>💡 Suggestions</h4>
                        <ul>
                            ${recommendations.processing_suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="confirmation-controls">
                    <button class="btn btn-primary" onclick="arCamera.proceedWithConfirmedInput()">🚀 Generate Content</button>
                    <button class="btn btn-secondary" onclick="arCamera.retakePhoto()">📷 Retake Photo</button>
                    <button class="btn btn-outline" onclick="arCamera.closeConfirmation()">❌ Cancel</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Add click handlers for option selection
        this.bindConfirmationEvents();
    }
    
    bindConfirmationEvents() {
        const overlay = document.getElementById('confirmation-overlay');
        if (!overlay) return;
        
        // Add click handlers for question and topic cards
        const questionCards = overlay.querySelectorAll('.question-card');
        const topicCards = overlay.querySelectorAll('.topic-card');
        const conceptCard = overlay.querySelector('.concept-card');
        const confirmedInput = overlay.querySelector('#confirmed-input');
        
        questionCards.forEach(card => {
            card.addEventListener('click', () => {
                this.selectOption(card, 'question', confirmedInput);
            });
        });
        
        topicCards.forEach(card => {
            card.addEventListener('click', () => {
                this.selectOption(card, 'topic', confirmedInput);
            });
        });
        
        if (conceptCard) {
            conceptCard.addEventListener('click', () => {
                this.selectOption(conceptCard, 'concept', confirmedInput);
            });
        }
    }
    
    selectOption(cardElement, type, inputElement) {
        // Remove previous selections
        document.querySelectorAll('.question-card, .topic-card, .concept-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Mark as selected
        cardElement.classList.add('selected');
        
        // Update input text based on selection
        let selectedText = '';
        
        if (type === 'question') {
            const index = cardElement.dataset.index;
            selectedText = this.confirmationData.detected_content.questions[index].suggested_input;
        } else if (type === 'topic') {
            const index = cardElement.dataset.index;
            selectedText = this.confirmationData.detected_content.topics[index].suggested_input;
        } else if (type === 'concept') {
            selectedText = this.confirmationData.detected_content.primary_concept.suggested_input;
        }
        
        inputElement.value = selectedText;
    }
    
    async proceedWithConfirmedInput() {
        const overlay = document.getElementById('confirmation-overlay');
        const confirmedInput = overlay.querySelector('#confirmed-input').value.trim();
        const complexity = overlay.querySelector('#confirmed-complexity').value;
        const language = overlay.querySelector('#confirmed-language').value;
        
        if (!confirmedInput) {
            alert('Please enter or select content to proceed');
            return;
        }
        
        try {
            // Close confirmation overlay
            this.closeConfirmation();
            
            // Show processing overlay
            this.showARLoading('🤖 Processing confirmed input...');
            this.updateLoadingProgress(10, 'Preparing content generation...');
            
            const formData = new FormData();
            formData.append('input_text', confirmedInput);
            formData.append('complexity', complexity);
            formData.append('language', language);
            
            this.updateLoadingProgress(30, 'Generating educational content...');
            
            const response = await fetch('/api/generate-content', {
                method: 'POST',
                body: formData
            });
            
            this.updateLoadingProgress(70, 'Creating video and narration...');
            
            const result = await response.json();
            
            if (result.success) {
                this.updateLoadingProgress(100, 'Content ready!');
                
                setTimeout(() => {
                    this.hideARLoading();
                    this.showARResults(result);
                }, 1000);
                
            } else {
                throw new Error(result.error || 'Generation failed');
            }
            
        } catch (error) {
            console.error('Processing error:', error);
            this.hideARLoading();
            alert('Content generation failed: ' + error.message);
        }
    }
    
    retakePhoto() {
        this.closeConfirmation();
        // Reset to camera mode
        this.clearDetectedItems();
    }
    
    closeConfirmation() {
        const overlay = document.getElementById('confirmation-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    showARResults(result) {
        const arResults = document.getElementById('ar-results');
        const arVideo = document.getElementById('ar-video');
        const arVideoPlaceholder = document.getElementById('ar-video-placeholder');
        const arGenerationInfo = document.getElementById('ar-generation-info');
        const arDocumentLinks = document.getElementById('ar-document-links');
        
        // Show video if available
        const videoUrl = result.video_urls?.narrated || result.video_urls?.original;
        if (videoUrl) {
            arVideo.src = videoUrl;
            arVideo.style.display = 'block';
            arVideoPlaceholder.style.display = 'none';
        }
        
        // Show generation info
        arGenerationInfo.innerHTML = `
            <h4>📊 Generation Info</h4>
            <p><strong>Type:</strong> ${result.input_processing?.input_type || 'Unknown'}</p>
            <p><strong>Time:</strong> ${result.generation_time?.toFixed(1) || 0}s</p>
            <p><strong>Language:</strong> ${result.input_processing?.language || 'english'}</p>
        `;
        
        // Show document links
        let documentLinksHtml = '<h4>📚 Educational Documents</h4>';
        const documents = result.documents || {};
        
        if (documents.solution_url) {
            documentLinksHtml += `<a href="${documents.solution_url}" target="_blank" class="document-link">🧮 Solution Document</a>`;
        }
        if (documents.explanation_url) {
            documentLinksHtml += `<a href="${documents.explanation_url}" target="_blank" class="document-link">📖 Explanation Document</a>`;
        }
        if (documents.summary_url) {
            documentLinksHtml += `<a href="${documents.summary_url}" target="_blank" class="document-link">📄 Summary Document</a>`;
        }
        
        arDocumentLinks.innerHTML = documentLinksHtml;
        
        // Show AR results overlay
        arResults.style.display = 'flex';
    }
    
    clearDetectedItems() {
        this.detectedItemsContainer.innerHTML = '';
        this.analysisResult = null;
        this.confirmationData = null;
        this.extractedSection.style.display = 'none';
    }
    
    showARLoading(message) {
        const arLoading = document.getElementById('ar-loading');
        const loadingMessage = document.getElementById('ar-loading-message');
        const progressBar = document.getElementById('progress-bar');
        
        loadingMessage.textContent = message;
        progressBar.style.width = '0%';
        arLoading.style.display = 'flex';
    }
    
    updateLoadingProgress(percentage, message) {
        const loadingMessage = document.getElementById('ar-loading-message');
        const progressBar = document.getElementById('progress-bar');
        
        if (message) loadingMessage.textContent = message;
        progressBar.style.width = `${percentage}%`;
    }
    
    hideARLoading() {
        const arLoading = document.getElementById('ar-loading');
        arLoading.style.display = 'none';
    }
}

// Global functions for AR results
function downloadContent() {
    // Implementation for downloading generated content
    alert('Download functionality will be implemented');
}

function shareArContent() {
    // Implementation for sharing AR content
    if (navigator.share) {
        navigator.share({
            title: 'AI Generated Educational Content',
            text: 'Check out this AI-generated educational content!',
            url: window.location.href
        });
    } else {
        // Fallback for browsers without Web Share API
        navigator.clipboard.writeText(window.location.href);
        alert('URL copied to clipboard!');
    }
}

function closeArResults() {
    const arResults = document.getElementById('ar-results');
    arResults.style.display = 'none';
}

// Make arCamera globally accessible
let arCamera;

// Initialize AR Camera Scanner when page loads
document.addEventListener('DOMContentLoaded', () => {
    arCamera = new ARCameraScanner();
});
