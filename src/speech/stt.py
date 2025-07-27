"""
IRIS Speech-to-Text Module
Web Speech API and offline alternatives
"""

import asyncio
import json
from typing import Optional, Dict, Callable
from enum import Enum

class STTEngine(Enum):
    WEB_SPEECH_API = "web_speech_api"
    WHISPER_LOCAL = "whisper_local" 
    DEEPSPEECH = "deepspeech"

class IRISSpeechToText:
    """Speech-to-Text handler for IRIS"""
    
    def __init__(self, engine: STTEngine = STTEngine.WEB_SPEECH_API):
        self.engine = engine
        self.is_listening = False
        self.confidence_threshold = 0.7
        self.language = "en-US"
        
    async def start_listening(self, callback: Callable = None):
        """Start continuous speech recognition"""
        self.is_listening = True
        return {
            "status": "listening",
            "engine": self.engine.value,
            "language": self.language
        }
    
    async def stop_listening(self):
        """Stop speech recognition"""
        self.is_listening = False
        return {"status": "stopped"}
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return [
            "en-US", "en-GB", "es-ES", "fr-FR", "de-DE",
            "it-IT", "pt-BR", "ru-RU", "ja-JP", "ko-KR",
            "zh-CN", "hi-IN"
        ]

# Global STT instance
iris_stt = IRISSpeechToText()
