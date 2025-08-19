class EnhancedAudioInput {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.audioDevices = [];
        this.selectedDeviceId = null;
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.waveformCanvas = null;
        this.waveformCtx = null;
        
        this.initializeAudio();
    }
    
    async initializeAudio() {
        try {
            // Get available audio devices
            await this.getAudioDevices();
            
            // Create waveform visualization
            this.createWaveformCanvas();
            
            console.log('✅ Enhanced audio input initialized');
        } catch (error) {
            console.error('❌ Audio initialization failed:', error);
        }
    }
    
    async getAudioDevices() {
        try {
            // Request permission first
            await navigator.mediaDevices.getUserMedia({ audio: true });
            
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.audioDevices = devices.filter(device => device.kind === 'audioinput');
            
            console.log('🎤 Available audio devices:', this.audioDevices);
            
            // Create device selector UI
            this.createDeviceSelector();
            
        } catch (error) {
            console.error('❌ Failed to get audio devices:', error);
        }
    }
    
    createDeviceSelector() {
        const voiceContainer = document.querySelector('.voice-container');
        if (!voiceContainer) return;
        
        // Remove existing selector
        const existingSelector = document.getElementById('audio-device-selector');
        if (existingSelector) existingSelector.remove();
        
        const deviceSelectorHTML = `
            <div id="audio-device-selector" class="device-selector">
                <label class="text-blue-100 mb-2 block">Select Microphone:</label>
                <select id="device-select" class="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white">
                    <option value="">Default Device</option>
                    ${this.audioDevices.map(device => 
                        `<option value="${device.deviceId}">${device.label || `Microphone ${device.deviceId.slice(0, 8)}`}</option>`
                    ).join('')}
                </select>
                
                <div id="audio-level-container" class="mt-3">
                    <label class="text-blue-100 text-sm">Audio Level:</label>
                    <canvas id="waveform-canvas" width="300" height="60" class="w-full bg-black/20 rounded mt-1"></canvas>
                    <div id="audio-level-text" class="text-blue-200 text-xs mt-1">No input detected</div>
                </div>
            </div>
        `;
        
        // Insert before recording button
        const recordButton = document.getElementById('voice-record-btn');
        recordButton.parentNode.insertBefore(
            this.createElementFromHTML(deviceSelectorHTML),
            recordButton
        );
        
        // Bind device selector
        document.getElementById('device-select').addEventListener('change', (e) => {
            this.selectedDeviceId = e.target.value || null;
            this.restartAudioMonitoring();
        });
        
        // Start audio monitoring
        this.restartAudioMonitoring();
    }
    
    createElementFromHTML(htmlString) {
        const div = document.createElement('div');
        div.innerHTML = htmlString.trim();
        return div.firstChild;
    }
    
    createWaveformCanvas() {
        // This will be created in the device selector
    }
    
    async restartAudioMonitoring() {
        try {
            // Stop existing monitoring
            if (this.audioContext) {
                this.audioContext.close();
            }
            
            // Get audio stream from selected device
            const constraints = {
                audio: {
                    deviceId: this.selectedDeviceId ? { exact: this.selectedDeviceId } : undefined,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            };
            
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Create audio context for monitoring
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            
            this.analyser.fftSize = 256;
            this.microphone.connect(this.analyser);
            
            // Setup waveform canvas
            this.waveformCanvas = document.getElementById('waveform-canvas');
            if (this.waveformCanvas) {
                this.waveformCtx = this.waveformCanvas.getContext('2d');
                this.drawWaveform();
            }
            
            // Store stream for recording
            this.currentStream = stream;
            
            console.log('✅ Audio monitoring started with device:', this.selectedDeviceId || 'default');
            
        } catch (error) {
            console.error('❌ Failed to start audio monitoring:', error);
            document.getElementById('audio-level-text').textContent = 'Microphone access denied';
        }
    }
    
    drawWaveform() {
        if (!this.analyser || !this.waveformCtx) return;
        
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            requestAnimationFrame(draw);
            
            this.analyser.getByteTimeDomainData(dataArray);
            
            // Clear canvas
            this.waveformCtx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            this.waveformCtx.fillRect(0, 0, this.waveformCanvas.width, this.waveformCanvas.height);
            
            // Draw waveform
            this.waveformCtx.lineWidth = 2;
            this.waveformCtx.strokeStyle = '#60A5FA';
            this.waveformCtx.beginPath();
            
            const sliceWidth = this.waveformCanvas.width / bufferLength;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * this.waveformCanvas.height / 2;
                
                if (i === 0) {
                    this.waveformCtx.moveTo(x, y);
                } else {
                    this.waveformCtx.lineTo(x, y);
                }
                
                x += sliceWidth;
            }
            
            this.waveformCtx.stroke();
            
            // Update audio level text
            const average = dataArray.reduce((sum, value) => sum + Math.abs(value - 128), 0) / bufferLength;
            const levelText = document.getElementById('audio-level-text');
            if (levelText) {
                if (average > 5) {
                    levelText.textContent = `🎤 Audio detected - Level: ${Math.round(average)}`;
                    levelText.style.color = '#10B981';
                } else {
                    levelText.textContent = 'No audio input detected';
                    levelText.style.color = '#6B7280';
                }
            }
        };
        
        draw();
    }
    
    async startRecording() {
        try {
            if (!this.currentStream) {
                await this.restartAudioMonitoring();
            }
            
            // Create new MediaRecorder with the current stream
            this.mediaRecorder = new MediaRecorder(this.currentStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                console.log('🎵 Recorded audio blob size:', audioBlob.size);
                
                // Trigger the callback
                if (this.onRecordingComplete) {
                    this.onRecordingComplete(audioBlob);
                }
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            console.log('🎤 Recording started with device:', this.selectedDeviceId || 'default');
            
        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            throw error;
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('⏹️ Recording stopped');
        }
    }
    
    setRecordingCompleteCallback(callback) {
        this.onRecordingComplete = callback;
    }
}

// Initialize enhanced audio input
let enhancedAudio = null;

document.addEventListener('DOMContentLoaded', () => {
    enhancedAudio = new EnhancedAudioInput();
});

// Export for use in main page
window.EnhancedAudioInput = EnhancedAudioInput;
