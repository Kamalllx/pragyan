"use client";

import { useState, useRef } from "react";
import {
  Upload,
  Mic,
  MicOff,
  Send,
  Play,
  Download,
  Loader2,
  Volume2,
  FileText,
  Camera,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

// Types
interface VideoGenerationResult {
  success: boolean;
  transcription?: string;
  detected_language?: string;
  understood_parameters?: {
    subject: string;
    topic: string;
    complexity: string;
    intent: string;
    key_concepts: string[];
    specific_requirements: string;
  };
  video_urls?: {
    original: string;
    narrated: string;
    cloud_original: string;
    script: string;
  };
  quality_metrics?: {
    overall_score: number;
    execution_successful: boolean;
    video_generated: boolean;
    narration_added: boolean;
  };
  language_detection?: {
    detected_language: string;
    confidence: number;
    auto_selected: boolean;
  };
  debug_info?: {
    pipeline_timestamp: string;
    debug_audio_path: string;
    fallback_used?: boolean;
  };
  error_type?: string;
  error_message?: string;
  suggestions?: string[];
  error?: string;
}

interface ImageAnalysisResult {
  success: boolean;
  analysis?: {
    description: string;
    subject: string;
    difficulty: string;
    educational_value: string;
  };
  options?: {
    topics: string[];
    questions: string[];
    text_content: string;
  };
  analysis_method?: string;
  error?: string;
}

export default function PragyanAI() {
  // State management
  const [inputText, setInputText] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("auto");
  const [includeNarration, setIncludeNarration] = useState(true);
  const [complexity, setComplexity] = useState("intermediate");
  const [inputMode, setInputMode] = useState<"text" | "voice" | "image">(
    "text"
  );

  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const enhancedAudioRef = useRef<any>(null);

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [result, setResult] = useState<VideoGenerationResult | null>(null);

  // Image upload state
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageAnalysis, setImageAnalysis] =
    useState<ImageAnalysisResult | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // API Configuration - Updated for new NLP endpoints
  const API_BASE = "http://localhost:8000";

  // Languages
  const languages = [
    { value: "auto", label: "Auto-detect" },
    { value: "english", label: "English" },
    { value: "hindi", label: "Hindi" },
    { value: "tamil", label: "Tamil" },
    { value: "bengali", label: "Bengali" },
    { value: "gujarati", label: "Gujarati" },
    { value: "kannada", label: "Kannada" },
    { value: "malayalam", label: "Malayalam" },
    { value: "marathi", label: "Marathi" },
    { value: "odia", label: "Odia" },
    { value: "punjabi", label: "Punjabi" },
    { value: "telugu", label: "Telugu" },
    { value: "urdu", label: "Urdu" },
  ];

  // Voice Recording Functions (with Enhanced Audio Input support)
  const startRecording = async () => {
    try {
      // Use enhanced audio input if available
      if ((window as any).EnhancedAudioInput && !enhancedAudioRef.current) {
        enhancedAudioRef.current = new (window as any).EnhancedAudioInput();

        enhancedAudioRef.current.setRecordingCompleteCallback(
          (audioBlob: Blob) => {
            console.log(
              "✅ Enhanced recording complete, blob size:",
              audioBlob.size
            );
            setRecordedAudio(audioBlob);
          }
        );
      }

      if (enhancedAudioRef.current) {
        await enhancedAudioRef.current.startRecording();
        setIsRecording(true);
      } else {
        // Fallback to original method
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/wav",
          });
          setRecordedAudio(audioBlob);
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      alert(
        "Microphone access denied. Please check your audio device settings."
      );
    }
  };

  const stopRecording = () => {
    if (enhancedAudioRef.current && isRecording) {
      enhancedAudioRef.current.stopRecording();
      setIsRecording(false);
    } else if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Image Upload Functions
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      // Clear previous analysis
      setImageAnalysis(null);
    }
  };

  // Enhanced Video Generation Functions using Phase 1 NLP endpoints
  const generateVideoFromText = async () => {
    if (!inputText.trim()) return;

    setIsGenerating(true);
    setGenerationProgress(10);
    setResult(null);

    try {
      console.log("Sending text to NLP endpoint:", inputText);

      const response = await fetch(`${API_BASE}/api/nlp/text-to-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: inputText,
          language: selectedLanguage,
          complexity: complexity,
          include_narration: includeNarration,
        }),
      });

      const data = await response.json();
      console.log("NLP Text-to-video response:", data);

      setGenerationProgress(100);

      if (data.success) {
        setResult(data);
      } else {
        setResult({
          success: false,
          error_type: data.error_type || "Generation Error",
          error_message:
            data.error_message || data.error || "Text generation failed",
          suggestions: data.suggestions || [
            "Please try rephrasing your request",
            "Check if the topic is educational",
          ],
        });
      }
    } catch (error) {
      console.error("Text generation error:", error);
      setResult({
        success: false,
        error_type: "Network Error",
        error_message:
          error instanceof Error ? error.message : "Unknown network error",
        suggestions: [
          "Check your internet connection",
          "Verify the backend is running",
        ],
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const generateVideoFromVoice = async () => {
    if (!recordedAudio) return;

    setIsGenerating(true);
    setGenerationProgress(10);
    setResult(null);

    try {
      console.log("Processing voice input...");

      // Convert audio blob to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const audioBase64 = reader.result as string;

        setGenerationProgress(30);

        const response = await fetch(`${API_BASE}/api/nlp/voice-to-video`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            audio: audioBase64,
            language: selectedLanguage,
          }),
        });

        const data = await response.json();
        console.log("NLP Voice-to-video response:", data);

        setGenerationProgress(100);

        if (data.success) {
          setResult(data);
        } else {
          setResult({
            success: false,
            error_type: data.error_type || "Voice Processing Error",
            error_message:
              data.error_message || data.error || "Voice generation failed",
            suggestions: data.suggestions || [
              "Try speaking more clearly",
              "Check microphone quality",
            ],
            debug_info: data.debug_info,
          });
        }

        setIsGenerating(false);
      };
      reader.readAsDataURL(recordedAudio);
    } catch (error) {
      console.error("Voice generation error:", error);
      setResult({
        success: false,
        error_type: "Processing Error",
        error_message: error instanceof Error ? error.message : "Unknown error",
        suggestions: ["Try recording again", "Check audio quality"],
      });
      setIsGenerating(false);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;

    setIsGenerating(true);
    setGenerationProgress(10);
    setImageAnalysis(null);

    try {
      console.log("Analyzing image...");

      const reader = new FileReader();
      reader.onload = async () => {
        const imageBase64 = reader.result as string;

        setGenerationProgress(50);

        const response = await fetch(
          `${API_BASE}/api/analyze-educational-image`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              image: imageBase64,
            }),
          }
        );

        const data = await response.json();
        console.log("Image analysis response:", data);

        setGenerationProgress(70);
        setImageAnalysis(data);

        if (data.success && data.options?.topics?.length > 0) {
          // Auto-generate video from first detected topic
          const topic = data.options.topics[0];
          await generateVideoFromAnalyzedImage(topic, data);
        } else {
          setResult({
            success: false,
            error_type: "Image Analysis Error",
            error_message: data.error || "Could not analyze the image content",
            suggestions: [
              "Try uploading a clearer image",
              "Ensure the image contains educational content",
            ],
          });
          setIsGenerating(false);
        }
      };
      reader.readAsDataURL(selectedImage);
    } catch (error) {
      console.error("Image analysis error:", error);
      setResult({
        success: false,
        error_type: "Processing Error",
        error_message: error instanceof Error ? error.message : "Unknown error",
        suggestions: [
          "Try uploading the image again",
          "Check image format and size",
        ],
      });
      setIsGenerating(false);
    }
  };

  const generateVideoFromAnalyzedImage = async (
    topic: string,
    analysis: ImageAnalysisResult
  ) => {
    try {
      console.log("Generating video from analyzed topic:", topic);

      const response = await fetch(`${API_BASE}/api/nlp/text-to-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: `Explain ${topic} based on this educational content`,
          language: selectedLanguage,
          complexity: complexity,
          include_narration: includeNarration,
        }),
      });

      const data = await response.json();
      console.log("Video generation from image response:", data);

      setGenerationProgress(100);

      if (data.success) {
        setResult({
          ...data,
          image_analysis: analysis,
        });
      } else {
        setResult({
          success: false,
          error_type: "Video Generation Error",
          error_message:
            data.error_message ||
            "Failed to generate video from analyzed content",
          suggestions: data.suggestions || [
            "Try a different image",
            "Simplify the content",
          ],
        });
      }
    } catch (error) {
      console.error("Video generation from image error:", error);
      setResult({
        success: false,
        error_type: "Generation Error",
        error_message: error instanceof Error ? error.message : "Unknown error",
        suggestions: [
          "Try again with a different approach",
          "Check the backend connection",
        ],
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerate = () => {
    if (inputMode === "text") {
      generateVideoFromText();
    } else if (inputMode === "voice") {
      generateVideoFromVoice();
    } else if (inputMode === "image") {
      analyzeImage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-white mb-2">PragyanAI</h1>
          <p className="text-blue-100 text-lg">
            Generate educational videos with AI-powered natural language
            processing
          </p>
          <div className="flex items-center gap-2 mt-2">
            <div className="bg-green-500/20 text-green-300 px-2 py-1 rounded text-sm">
              Phase 1: Natural Language Processing
            </div>
            <div className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded text-sm">
              Multi-language Support
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-6">
              Create Your Video
            </h2>

            {/* Input Mode Selection */}
            <div className="flex mb-6 bg-white/5 rounded-lg p-1">
              {[
                { mode: "text", icon: FileText, label: "Text" },
                { mode: "voice", icon: Mic, label: "Voice" },
                { mode: "image", icon: Camera, label: "Image" },
              ].map(({ mode, icon: Icon, label }) => (
                <button
                  key={mode}
                  onClick={() => setInputMode(mode as any)}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-md transition-all ${
                    inputMode === mode
                      ? "bg-blue-600 text-white"
                      : "text-blue-100 hover:bg-white/10"
                  }`}
                >
                  <Icon size={20} />
                  {label}
                </button>
              ))}
            </div>

            {/* Text Input */}
            {inputMode === "text" && (
              <div className="mb-6">
                <label className="block text-blue-100 mb-2">
                  What would you like to learn?
                </label>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="E.g., 'Explain photosynthesis step by step', 'How do neural networks work?', 'Show me the Pythagorean theorem'"
                  className="w-full h-32 bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-blue-200 text-sm mt-2">
                  The AI will understand your request and generate appropriate
                  educational content
                </p>
              </div>
            )}

            {/* Voice Input */}
            {inputMode === "voice" && (
              <div className="mb-6">
                <label className="block text-blue-100 mb-2">
                  Record your question
                </label>
                <div className="flex flex-col items-center space-y-4">
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                      isRecording
                        ? "bg-red-500 hover:bg-red-600 animate-pulse"
                        : "bg-blue-600 hover:bg-blue-700"
                    }`}
                  >
                    {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
                  </button>
                  <p className="text-blue-100 text-center">
                    {isRecording
                      ? "Recording... Click to stop"
                      : "Click to start recording"}
                  </p>
                  {recordedAudio && (
                    <div className="text-green-400 text-center flex items-center gap-2">
                      <CheckCircle size={16} />
                      Audio recorded successfully
                    </div>
                  )}
                  <p className="text-blue-200 text-sm text-center">
                    Speak clearly in any supported language. AI will auto-detect
                    and process your request.
                  </p>
                </div>
              </div>
            )}

            {/* Image Input */}
            {inputMode === "image" && (
              <div className="mb-6">
                <label className="block text-blue-100 mb-2">
                  Upload educational content
                </label>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-white/30 rounded-lg p-8 text-center cursor-pointer hover:border-white/50 transition-colors"
                >
                  {imagePreview ? (
                    <div className="space-y-4">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="max-h-48 mx-auto rounded-lg"
                      />
                      <p className="text-blue-100">Click to change image</p>
                      {imageAnalysis && (
                        <div className="bg-white/10 rounded-lg p-3 text-left">
                          <p className="text-green-400 text-sm font-medium">
                            Analysis: {imageAnalysis.analysis?.subject} -{" "}
                            {imageAnalysis.analysis?.difficulty}
                          </p>
                          <p className="text-blue-200 text-sm">
                            {imageAnalysis.analysis?.description}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Upload size={48} className="mx-auto text-blue-300" />
                      <p className="text-blue-100">
                        Click to upload an image of educational content
                      </p>
                      <p className="text-blue-200 text-sm">
                        Supports textbooks, equations, diagrams, charts, etc.
                      </p>
                    </div>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </div>
            )}

            {/* Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {/* Language Selection */}
              <div>
                <label className="block text-blue-100 mb-2">Language</label>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {languages.map((lang) => (
                    <option
                      key={lang.value}
                      value={lang.value}
                      className="bg-gray-800"
                    >
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Complexity */}
              <div>
                <label className="block text-blue-100 mb-2">Complexity</label>
                <select
                  value={complexity}
                  onChange={(e) => setComplexity(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="beginner" className="bg-gray-800">
                    Beginner
                  </option>
                  <option value="intermediate" className="bg-gray-800">
                    Intermediate
                  </option>
                  <option value="advanced" className="bg-gray-800">
                    Advanced
                  </option>
                </select>
              </div>
            </div>

            {/* Include Narration */}
            <label className="flex items-center space-x-3 mb-6">
              <input
                type="checkbox"
                checked={includeNarration}
                onChange={(e) => setIncludeNarration(e.target.checked)}
                className="w-5 h-5 text-blue-600 bg-white/10 border-white/20 rounded focus:ring-blue-500"
              />
              <span className="text-blue-100">Include voice narration</span>
            </label>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={
                isGenerating ||
                (inputMode === "text" && !inputText.trim()) ||
                (inputMode === "voice" && !recordedAudio) ||
                (inputMode === "image" && !selectedImage)
              }
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-lg transition-all flex items-center justify-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing with AI...</span>
                </>
              ) : (
                <>
                  <Send size={20} />
                  <span>Generate Video</span>
                </>
              )}
            </button>
          </div>

          {/* Results Section */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-6">
              Generated Video
            </h2>

            {/* Loading State */}
            {isGenerating && (
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Loader2 className="animate-spin text-blue-400" size={24} />
                  <span className="text-blue-100">
                    {inputMode === "voice"
                      ? "Processing speech and generating video..."
                      : inputMode === "image"
                      ? "Analyzing image and creating content..."
                      : "Understanding request and creating video..."}
                  </span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${generationProgress}%` }}
                  ></div>
                </div>
                <p className="text-blue-200 text-sm">
                  Using enhanced AI natural language processing...
                </p>
              </div>
            )}

            {/* Success State */}
            {result && result.success && (
              <div className="space-y-6">
                {/* Transcription/Understanding Info */}
                {(result.transcription || result.understood_parameters) && (
                  <div className="bg-white/5 rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-2">
                      AI Understanding
                    </h3>
                    {result.transcription && (
                      <p className="text-blue-100 mb-2">
                        <strong>Transcription:</strong> "{result.transcription}"
                      </p>
                    )}
                    {result.understood_parameters && (
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="text-blue-200">
                          <strong>Subject:</strong>{" "}
                          {result.understood_parameters.subject}
                        </div>
                        <div className="text-blue-200">
                          <strong>Topic:</strong>{" "}
                          {result.understood_parameters.topic}
                        </div>
                        <div className="text-blue-200">
                          <strong>Intent:</strong>{" "}
                          {result.understood_parameters.intent}
                        </div>
                        <div className="text-blue-200">
                          <strong>Complexity:</strong>{" "}
                          {result.understood_parameters.complexity}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Video Player */}
                {result.video_urls?.cloud_original && (
                  <div className="bg-black rounded-lg overflow-hidden">
                    <video
                      controls
                      className="w-full"
                      poster="/api/placeholder/640/360"
                    >
                      <source
                        src={result.video_urls.cloud_original}
                        type="video/mp4"
                      />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}

                {/* Quality Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-2">
                      Quality Score
                    </h3>
                    <p className="text-2xl font-bold text-green-400">
                      {result.quality_metrics?.overall_score || 0}/100
                    </p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-2">Language</h3>
                    <p className="text-2xl font-bold text-blue-400">
                      {result.detected_language ||
                        result.language_detection?.detected_language ||
                        "N/A"}
                    </p>
                  </div>
                </div>

                {/* Download Links */}
                <div className="flex flex-wrap gap-3">
                  {result.video_urls?.cloud_original && (
                    <a
                      href={result.video_urls.cloud_original}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white transition-colors"
                    >
                      <Download size={16} />
                      <span>Download Video</span>
                    </a>
                  )}
                  {result.video_urls?.script && (
                    <a
                      href={result.video_urls.script}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-white transition-colors"
                    >
                      <FileText size={16} />
                      <span>View Script</span>
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Error State */}
            {result && !result.success && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle size={20} className="text-red-400" />
                  <h3 className="font-semibold text-red-400">
                    {result.error_type || "Generation Failed"}
                  </h3>
                </div>
                <p className="text-red-300 mb-3">
                  {result.error_message || result.error}
                </p>
                {result.suggestions && result.suggestions.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-200 mb-2">
                      Suggestions:
                    </h4>
                    <ul className="list-disc list-inside text-red-200 text-sm space-y-1">
                      {result.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.debug_info?.debug_audio_path && (
                  <div className="mt-3 text-red-200 text-sm">
                    <strong>Debug:</strong> Audio saved for analysis
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!isGenerating && !result && (
              <div className="text-center text-blue-200 py-12">
                <Play size={48} className="mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">
                  Your AI-generated video will appear here
                </p>
                <p className="text-sm opacity-75">
                  Powered by advanced natural language processing
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
