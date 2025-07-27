"""
IRIS API Server
FastAPI-based web server for the voice assistant
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.iris import iris_core
import os
import uvicorn
from typing import List
import json
import asyncio

from src.speech.tts import iris_tts, TTSEngine
from src.speech.stt import iris_stt

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="IRIS - Intelligent Responsive Interface System",
        description="Smart AI Voice Assistant API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store active WebSocket connections
    active_connections: List[WebSocket] = []
    
    @app.get("/")
    async def root():
        """Root endpoint - health check"""
        return {
            "message": "🤖 IRIS Voice Assistant is running!",
            "version": "0.1.0",
            "status": "active",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "voice_interface": "/voice_interface",
                "websocket": "/ws",
                "chat": "/chat"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "IRIS Voice Assistant",
            "timestamp": "2025-07-27T13:00:00Z"
        }
    
    @app.post("/chat")
    async def chat_endpoint(message: dict):
        """Enhanced chat endpoint with IRIS intelligence"""
        user_message = message.get("message", "")
        user_id = message.get("user_id", "default")

        # Process message through IRIS core
        result = await iris_core.process_message(user_message, user_id)
    
        return {
            "user_message": user_message,
            "iris_response": result["response"],
            "confidence": result["confidence"],
            "intent": result["intent"],
            "timestamp": result["timestamp"],
            "status": "success"
        }
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time communication with hybrid AI"""
        await websocket.accept()
        active_connections.append(websocket)

        try:
            await websocket.send_text(json.dumps({
                "type": "connection",
                "message": "🤖 Connected to IRIS! I'm powered by hybrid AI and ready to assist.",
                "status": "connected"
            }))

            while True:
                # Wait for message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                user_id = message_data.get("user_id", "default")
                language = message_data.get("language", "en-US")

                if user_message:
                    try:
                        # Process through IRIS hybrid AI system (NOT the old echo logic)
                        ai_result = await iris_core.process_message(user_message, user_id)

                        # Send AI response back via WebSocket
                        response = {
                            "type": "response",
                            "user_message": user_message,
                            "iris_response": ai_result["response"],
                            "confidence": ai_result["confidence"],
                            "intent": ai_result["intent"],
                            "provider_used": ai_result.get("provider_used", "unknown"),
                            "processing_time": ai_result.get("processing_time", 0),
                            "language": language,
                            "timestamp": ai_result["timestamp"]
                        }

                        await websocket.send_text(json.dumps(response))

                    except Exception as e:
                        # Send error response
                        error_response = {
                            "type": "error",
                            "message": f"🤖 I encountered an error: {str(e)}. Let me try to help anyway.",
                            "user_message": user_message,
                            "iris_response": f"I heard '{user_message}' but had trouble processing it. Please try again.",
                            "status": "error"
                        }
                        await websocket.send_text(json.dumps(error_response))

        except WebSocketDisconnect:
            active_connections.remove(websocket)
            print("📱 Client disconnected from IRIS")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            if websocket in active_connections:
                active_connections.remove(websocket)

    @app.get("/voice-interface")
    async def voice_interface():
        """Advanced voice interface with real Web Speech API"""
        return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
            <title>IRIS Advanced Voice Interface</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .iris-logo {
            font-size: 72px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        h1 { margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { opacity: 0.8; margin-bottom: 30px; font-size: 1.2em; }
        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        button {
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            min-width: 150px;
        }
        .primary-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .secondary-btn {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
        }
        .danger-btn {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-left: 4px solid #4CAF50;
        }
        .conversation {
            text-align: left;
            max-height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            margin-top: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
        }
        .user-message {
            background: rgba(76, 175, 80, 0.3);
            margin-left: auto;
            text-align: right;
        }
        .iris-message {
            background: rgba(33, 150, 243, 0.3);
            margin-right: auto;
        }
        .settings {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        select {
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
        }
        select option { background: #333; color: white; }
        .visualizer {
            height: 60px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin: 20px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .wave {
            width: 4px;
            height: 20px;
            background: #4CAF50;
            margin: 0 2px;
            border-radius: 2px;
            animation: wave 1s infinite ease-in-out;
        }
        .wave:nth-child(2) { animation-delay: 0.1s; }
        .wave:nth-child(3) { animation-delay: 0.2s; }
        .wave:nth-child(4) { animation-delay: 0.3s; }
        .wave:nth-child(5) { animation-delay: 0.4s; }
        @keyframes wave {
            0%, 100% { height: 20px; }
            50% { height: 40px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="iris-logo">🤖</div>
        <h1>IRIS Voice Interface</h1>
        <p class="subtitle">Advanced Speech Recognition & AI Assistant</p>
        
        <div class="settings">
            <select id="languageSelect">
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
                <option value="hi-IN">Hindi</option>
            </select>
            <select id="voiceSelect">
                <option value="female">Female Voice</option>
                <option value="male">Male Voice</option>
            </select>
        </div>
        
        <div class="controls">
            <button id="startBtn" class="primary-btn">🎤 Start Listening</button>
            <button id="stopBtn" class="danger-btn" disabled>⏹️ Stop Listening</button>
            <button id="connectBtn" class="secondary-btn">🔗 Connect to IRIS</button>
        </div>
        
        <div id="visualizer" class="visualizer" style="display: none;">
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
        </div>
        
        <div id="status" class="status">
            <strong>Status:</strong> <span id="statusText">Ready to start</span>
        </div>
        
        <div id="conversation" class="conversation">
            <div class="message iris-message">
                <strong>🤖 IRIS:</strong> Welcome! I'm ready to listen and respond to your voice commands.
            </div>
        </div>
    </div>

    <script>
        // Web Speech API Implementation
        class IRISVoiceInterface {
            constructor() {
                this.recognition = null;
                this.synthesis = window.speechSynthesis;
                this.isListening = false;
                this.ws = null;
                this.currentLanguage = 'en-US';
                this.currentVoice = 'female';
                
                this.initializeElements();
                this.setupEventListeners();
                this.checkSpeechSupport();
            }
            
            initializeElements() {
                this.startBtn = document.getElementById('startBtn');
                this.stopBtn = document.getElementById('stopBtn');
                this.connectBtn = document.getElementById('connectBtn');
                this.statusText = document.getElementById('statusText');
                this.conversation = document.getElementById('conversation');
                this.visualizer = document.getElementById('visualizer');
                this.languageSelect = document.getElementById('languageSelect');
                this.voiceSelect = document.getElementById('voiceSelect');
            }
            
            setupEventListeners() {
                this.startBtn.onclick = () => this.startListening();
                this.stopBtn.onclick = () => this.stopListening();
                this.connectBtn.onclick = () => this.connectWebSocket();
                this.languageSelect.onchange = (e) => this.changeLanguage(e.target.value);
                this.voiceSelect.onchange = (e) => this.changeVoice(e.target.value);
            }
            
            checkSpeechSupport() {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    this.updateStatus('❌ Speech recognition not supported in this browser');
                    this.startBtn.disabled = true;
                    return false;
                }
                
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                this.recognition = new SpeechRecognition();
                this.setupSpeechRecognition();
                return true;
            }
            
            setupSpeechRecognition() {
                this.recognition.continuous = true;
                this.recognition.interimResults = true;
                this.recognition.lang = this.currentLanguage;
                
                this.recognition.onstart = () => {
                    this.isListening = true;
                    this.updateStatus('🎤 Listening...');
                    this.visualizer.style.display = 'flex';
                    this.startBtn.disabled = true;
                    this.stopBtn.disabled = false;
                };
                
                this.recognition.onresult = (event) => {
                    let finalTranscript = '';
                    let interimTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    
                    if (finalTranscript) {
                        this.handleSpeechResult(finalTranscript, event.results[event.resultIndex][0].confidence);
                    }
                    
                    // Show interim results
                    if (interimTranscript) {
                        this.updateStatus(`🎤 Hearing: "${interimTranscript}"`);
                    }
                };
                
                this.recognition.onerror = (event) => {
                    this.updateStatus(`❌ Speech recognition error: ${event.error}`);
                    this.stopListening();
                };
                
                this.recognition.onend = () => {
                    if (this.isListening) {
                        // Restart recognition if it was stopped unexpectedly
                        setTimeout(() => this.recognition.start(), 100);
                    }
                };
            }
            
            async handleSpeechResult(transcript, confidence) {
                this.addMessage(transcript, 'user');
                this.updateStatus(`✅ Heard: "${transcript}" (${Math.round(confidence * 100)}% confidence)`);
                
                // Send to IRIS via WebSocket
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        message: transcript,
                        confidence: confidence,
                        language: this.currentLanguage
                    }));
                } else {
                    // Fallback to REST API
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: transcript})
                        });
                        const data = await response.json();
                        this.handleIRISResponse(data.iris_response);
                    } catch (error) {
                        this.addMessage('❌ Connection error. Please try connecting to IRIS.', 'iris');
                    }
                }
            }
            
            handleIRISResponse(response) {
                this.addMessage(response, 'iris');
                this.speakResponse(response);
            }
            
            speakResponse(text) {
                // Cancel any ongoing speech
                this.synthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = this.currentLanguage;
                utterance.rate = 0.9;
                utterance.pitch = this.currentVoice === 'female' ? 1.2 : 0.8;
                
                // Select appropriate voice
                const voices = this.synthesis.getVoices();
                const targetVoice = voices.find(voice => 
                    voice.lang.startsWith(this.currentLanguage.split('-')[0]) &&
                    voice.name.toLowerCase().includes(this.currentVoice)
                ) || voices.find(voice => voice.lang.startsWith(this.currentLanguage.split('-')[0]));
                
                if (targetVoice) utterance.voice = targetVoice;
                
                utterance.onstart = () => this.updateStatus('🔊 IRIS is speaking...');
                utterance.onend = () => this.updateStatus('🎤 Ready for your next command');
                
                this.synthesis.speak(utterance);
            }
            
            startListening() {
                if (this.recognition) {
                    this.recognition.start();
                }
            }
            
            stopListening() {
                this.isListening = false;
                if (this.recognition) {
                    this.recognition.stop();
                }
                this.visualizer.style.display = 'none';
                this.startBtn.disabled = false;
                this.stopBtn.disabled = true;
                this.updateStatus('⏹️ Stopped listening');
            }
            
            connectWebSocket() {
                this.ws = new WebSocket('ws://localhost:8000/ws');
                
                this.ws.onopen = () => {
                    this.updateStatus('✅ Connected to IRIS WebSocket');
                    this.connectBtn.textContent = '✅ Connected';
                    this.connectBtn.disabled = true;
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.iris_response) {
                        this.handleIRISResponse(data.iris_response);
                    }
                };
                
                this.ws.onclose = () => {
                    this.updateStatus('❌ Disconnected from IRIS');
                    this.connectBtn.textContent = '🔗 Connect to IRIS';
                    this.connectBtn.disabled = false;
                };
                
                this.ws.onerror = (error) => {
                    this.updateStatus('❌ WebSocket error');
                    console.error('WebSocket error:', error);
                };
            }
            
            changeLanguage(language) {
                this.currentLanguage = language;
                if (this.recognition) {
                    this.recognition.lang = language;
                }
                this.updateStatus(`🌐 Language changed to ${language}`);
            }
            
            changeVoice(voice) {
                this.currentVoice = voice;
                this.updateStatus(`🎵 Voice changed to ${voice}`);
            }
            
            addMessage(message, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.innerHTML = `<strong>${sender === 'user' ? '👤 You' : '🤖 IRIS'}:</strong> ${message}`;
                this.conversation.appendChild(messageDiv);
                this.conversation.scrollTop = this.conversation.scrollHeight;
            }
            
            updateStatus(status) {
                this.statusText.textContent = status;
            }
        }
        
        // Initialize the voice interface when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new IRISVoiceInterface();
        });
    </script>
</body>
</html>
    """)

    @app.post("/speak")
    async def speak_endpoint(request: dict):
        """Convert text to speech"""
        text = request.get("text", "")
        language = request.get("language", "en")
        engine = request.get("engine", "gtts")
    
        if not text:
            return {"error": "No text provided"}
    
        try:
            # Set TTS engine
            if engine == "espeak":
                iris_tts.engine = TTSEngine.ESPEAK
            elif engine == "festival":
                iris_tts.engine = TTSEngine.FESTIVAL
            else:
                iris_tts.engine = TTSEngine.GTTS
        
            result = await iris_tts.speak(text, language)
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": {
                    "use_browser_synthesis": True,
                    "text": text,
                    "language": language
                }
            }

    @app.get("/tts/languages")
    async def get_tts_languages():
        """Get supported TTS languages"""
        return iris_tts.get_supported_languages()

    @app.post("/process-voice")
    async def process_voice_command(request: dict):
        """Process voice command end-to-end (STT -> AI -> TTS)"""
        message = request.get("message", "")
        language = request.get("language", "en")
        user_id = request.get("user_id", "default")
    
        try:
            # Process through IRIS AI
            ai_result = await iris_core.process_message(message, user_id)
        
            # Generate speech response
            tts_result = await iris_tts.speak(ai_result["response"], language)

            return {
                "user_message": message,
                "iris_response": ai_result["response"],
                "audio_data": tts_result,
                "confidence": ai_result["confidence"],
                "intent": ai_result["intent"],
                "timestamp": ai_result["timestamp"],
                "status": "success"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    @app.get("/ai/providers")
    async def get_ai_providers():
        """Get status of all AI providers"""
        return hybrid_ai.get_provider_status()

    @app.post("/ai/strategy")
    async def set_ai_strategy(request: dict):
        """Change AI routing strategy"""
        strategy = request.get("strategy", "smart")

        try:
            hybrid_ai.set_routing_strategy(strategy)
            return {
                "success": True,
                "strategy": strategy,
                "message": f"AI routing strategy changed to {strategy}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }

    @app.get("/system/status")
    async def system_status():
        """Get complete system status"""
        return {
            "iris_core": "operational",
            "hybrid_ai": hybrid_ai.get_provider_status(),
            "tts_engines": iris_tts.get_supported_languages(),
            "stt_status": "web_speech_api_ready",
            "uptime": "connected",
            "version": "0.1.0"
        }
    
    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
