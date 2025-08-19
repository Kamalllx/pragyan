class ManualInputHandler {
    constructor() {
        this.form = document.getElementById('manual-form');
        this.inputText = document.getElementById('input-text');
        this.detectBtn = document.getElementById('detect-btn');
        this.generateBtn = document.getElementById('generate-btn');
        this.loadingSection = document.getElementById('loading-section');
        this.resultsSection = document.getElementById('results-section');
        this.detectionSection = document.getElementById('detection-section');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.detectBtn.addEventListener('click', () => this.detectInputType());
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Auto-detect on input change
        this.inputText.addEventListener('input', () => {
            if (this.inputText.value.length > 10) {
                this.detectBtn.style.display = 'inline-block';
            }
        });
    }
    
    async detectInputType() {
        const inputText = this.inputText.value.trim();
        if (!inputText) return;
        
        try {
            this.detectBtn.disabled = true;
            this.detectBtn.textContent = '🔍 Detecting...';
            
            const formData = new FormData();
            formData.append('input_text', inputText);
            
            const response = await fetch('/api/detect-input-type', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayDetectionResults(result.detection);
            } else {
                throw new Error('Detection failed');
            }
            
        } catch (error) {
            console.error('Detection error:', error);
            alert('Detection failed: ' + error.message);
        } finally {
            this.detectBtn.disabled = false;
            this.detectBtn.textContent = '🔍 Detect Type';
        }
    }
    
    displayDetectionResults(detection) {
        const detectionResults = document.getElementById('detection-results');
        
        detectionResults.innerHTML = `
            <div class="detection-item">
                <h4>📋 Input Type</h4>
                <p><strong>${detection.type}</strong> (${(detection.confidence * 100).toFixed(0)}% confidence)</p>
            </div>
            <div class="detection-item">
                <h4>📚 Subject Area</h4>
                <p>${detection.subject_area}</p>
            </div>
            <div class="detection-item">
                <h4>🎯 Complexity Hint</h4>
                <p>${detection.complexity_hint}</p>
            </div>
            <div class="detection-item">
                <h4>🤖 AI Reasoning</h4>
                <p>${detection.reasoning}</p>
            </div>
        `;
        
        this.detectionSection.style.display = 'block';
        
        // Auto-update complexity if detected
        if (detection.complexity_hint && detection.complexity_hint !== 'intermediate') {
            document.getElementById('complexity').value = detection.complexity_hint;
        }
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.form);
        
        try {
            this.showLoading();
            
            // Simulate loading steps
            this.updateLoadingStep(1, 'active');
            await this.delay(1000);
            
            this.updateLoadingStep(2, 'active');
            
            const response = await fetch('/api/generate-content', {
                method: 'POST',
                body: formData
            });
            
            this.updateLoadingStep(3, 'active');
            
            const result = await response.json();
            
            this.updateLoadingStep(4, 'active');
            
            console.log('Generation result:', result); // Debug log
            
            if (result.success) {
                this.updateLoadingStep(5, 'active');
                await this.delay(1000);
                
                // Mark all steps as completed
                for (let i = 1; i <= 5; i++) {
                    this.updateLoadingStep(i, 'completed');
                }
                
                await this.delay(500);
                this.hideLoading();
                this.displayResults(result);
            } else {
                throw new Error(result.error || 'Generation failed');
            }
            
        } catch (error) {
            console.error('Generation error:', error);
            this.hideLoading();
            alert('Generation failed: ' + error.message);
        }
    }
    
    showLoading() {
        this.form.style.display = 'none';
        this.detectionSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.loadingSection.style.display = 'block';
        
        // Reset all steps
        for (let i = 1; i <= 5; i++) {
            this.updateLoadingStep(i, '');
        }
    }
    
    hideLoading() {
        this.loadingSection.style.display = 'none';
    }
    
    updateLoadingStep(stepNumber, className) {
        const step = document.getElementById(`step-${stepNumber}`);
        if (step) {
            step.className = `step ${className}`;
        }
    }
    
    displayResults(result) {
        console.log('Displaying results:', result); // Debug log
        
        this.resultsSection.style.display = 'block';
        
        // Display video content - FIXED
        const videoContent = document.getElementById('video-content');
        const videoUrls = result.video_urls || {};
        
        console.log('Video URLs:', videoUrls); // Debug log
        
        let videoHtml = '';
        
        // Check for narrated video first
        if (videoUrls.narrated && videoUrls.narrated !== '') {
            videoHtml += `
                <div class="video-container">
                    <video controls style="width: 100%; max-width: 600px; margin-bottom: 10px;" preload="metadata">
                        <source src="${videoUrls.narrated}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <p><strong>🎵 Narrated Version</strong></p>
                    <a href="${videoUrls.narrated}" target="_blank" class="document-link">🔗 Open in New Tab</a>
                </div>
            `;
        }
        
        // Check for original video
        if (videoUrls.original && videoUrls.original !== '') {
            if (!videoUrls.narrated) {
                // If no narrated video, show original as main video
                videoHtml += `
                    <div class="video-container">
                        <video controls style="width: 100%; max-width: 600px; margin-bottom: 10px;" preload="metadata">
                            <source src="${videoUrls.original}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                        <p><strong>🎬 Generated Video</strong></p>
                        <a href="${videoUrls.original}" target="_blank" class="document-link">🔗 Open in New Tab</a>
                    </div>
                `;
            } else {
                // If narrated exists, show original as alternative
                videoHtml += `<a href="${videoUrls.original}" target="_blank" class="document-link">🎬 Original Video (No Audio)</a>`;
            }
        }
        
        // Check for code URL
        if (videoUrls.code && videoUrls.code !== '') {
            videoHtml += `<a href="${videoUrls.code}" target="_blank" class="document-link">📄 Source Code</a>`;
        }
        
        // Fallback if no videos found
        if (!videoHtml) {
            videoHtml = '<p>⚠️ Video generation completed but URLs not available. Check server logs.</p>';
            console.error('No video URLs found in result:', result);
        }
        
        videoContent.innerHTML = videoHtml;
        
        // Display document links
        const documentLinks = document.getElementById('document-links');
        const documents = result.documents || {};
        
        let documentsHtml = '';
        if (documents.solution_url) {
            documentsHtml += `<a href="${documents.solution_url}" target="_blank" class="document-link">🧮 Solution Document</a>`;
        }
        if (documents.explanation_url) {
            documentsHtml += `<a href="${documents.explanation_url}" target="_blank" class="document-link">📖 Explanation Document</a>`;
        }
        if (documents.summary_url) {
            documentsHtml += `<a href="${documents.summary_url}" target="_blank" class="document-link">📄 Summary Document</a>`;
        }
        
        documentLinks.innerHTML = documentsHtml || '<p>No additional documents generated.</p>';
        
        // Display generation info
        const generationInfo = document.getElementById('generation-info');
        const inputProcessing = result.input_processing || {};
        
        generationInfo.innerHTML = `
            <p><strong>Type:</strong> ${inputProcessing.input_type || 'Unknown'}</p>
            <p><strong>Processing Time:</strong> ${result.generation_time?.toFixed(1) || 0}s</p>
            <p><strong>Language:</strong> ${inputProcessing.language || 'english'}</p>
            <p><strong>Complexity:</strong> ${inputProcessing.complexity || 'intermediate'}</p>
        `;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global functions
function resetForm() {
    location.reload();
}

function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'AI Generated Educational Content',
            text: 'Check out this AI-generated educational content!',
            url: window.location.href
        });
    } else {
        navigator.clipboard.writeText(window.location.href);
        alert('URL copied to clipboard!');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ManualInputHandler();
});
