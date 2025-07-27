"""
IRIS Text-to-Speech Module
High-quality TTS using gTTS and alternatives
"""

import os
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict, Union
from enum import Enum
import io
import base64

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class TTSEngine(Enum):
    GTTS = "gtts"
    FESTIVAL = "festival"
    ESPEAK = "espeak"
    BROWSER_SYNTHESIS = "browser"

class IRISTextToSpeech:
    """Text-to-Speech handler for IRIS"""
    
    def __init__(self, engine: TTSEngine = TTSEngine.GTTS):
        self.engine = engine
        self.language = "en"
        self.voice_speed = 1.0
        self.voice_gender = "female"
        self.output_dir = Path("data/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def speak(self, text: str, language: str = None) -> Dict:
        """Convert text to speech and return audio data"""
        lang = language or self.language
        
        try:
            if self.engine == TTSEngine.GTTS and GTTS_AVAILABLE:
                return await self._gtts_speak(text, lang)
            elif self.engine == TTSEngine.ESPEAK:
                return await self._espeak_speak(text, lang)
            elif self.engine == TTSEngine.FESTIVAL:
                return await self._festival_speak(text, lang)
            else:
                return await self._browser_synthesis_speak(text, lang)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": await self._browser_synthesis_speak(text, lang)
            }
    
    async def _gtts_speak(self, text: str, language: str) -> Dict:
        """Generate speech using Google Text-to-Speech"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            
            # Read audio data
            with open(temp_file.name, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            # Convert to base64 for web transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "success": True,
                "engine": "gtts",
                "audio_format": "mp3",
                "audio_base64": audio_base64,
                "text": text,
                "language": language,
                "duration_estimate": len(text) * 0.1  # Rough estimate
            }
            
        except Exception as e:
            raise Exception(f"gTTS error: {str(e)}")
    
    async def _espeak_speak(self, text: str, language: str) -> Dict:
        """Generate speech using eSpeak (local)"""
        try:
            import subprocess
            
            # Map language codes
            lang_map = {
                "en": "en",
                "es": "es",
                "fr": "fr",
                "de": "de",
                "it": "it",
                "pt": "pt",
                "ru": "ru",
                "ja": "ja",
                "ko": "ko",
                "zh": "zh",
                "hi": "hi"
            }
            
            espeak_lang = lang_map.get(language[:2], "en")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            # Run eSpeak command
            cmd = [
                "espeak",
                "-v", espeak_lang,
                "-s", "150",  # Speed
                "-w", temp_file.name,  # Output file
                text
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                os.unlink(temp_file.name)
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                return {
                    "success": True,
                    "engine": "espeak",
                    "audio_format": "wav",
                    "audio_base64": audio_base64,
                    "text": text,
                    "language": language
                }
            else:
                raise Exception("eSpeak process failed")
                
        except Exception as e:
            raise Exception(f"eSpeak error: {str(e)}")
    
    async def _festival_speak(self, text: str, language: str) -> Dict:
        """Generate speech using Festival TTS"""
        try:
            import subprocess
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            # Create Festival script
            festival_script = f'''
            (set! text "{text}")
            (utt.save.wave (utt.synth (eval (list 'Utterance 'Text text))) "{temp_file.name}")
            '''
            
            process = await asyncio.create_subprocess_exec(
                "festival",
                "--batch",
                input=festival_script.encode(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0 and os.path.exists(temp_file.name):
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                os.unlink(temp_file.name)
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                return {
                    "success": True,
                    "engine": "festival",
                    "audio_format": "wav",
                    "audio_base64": audio_base64,
                    "text": text,
                    "language": language
                }
            else:
                raise Exception("Festival process failed")
                
        except Exception as e:
            raise Exception(f"Festival error: {str(e)}")
    
    async def _browser_synthesis_speak(self, text: str, language: str) -> Dict:
        """Fallback to browser-based speech synthesis"""
        return {
            "success": True,
            "engine": "browser",
            "use_browser_synthesis": True,
            "text": text,
            "language": language,
            "instructions": "Use Web Speech API speechSynthesis on client side"
        }
    
    def get_supported_languages(self) -> Dict:
        """Get supported languages for each TTS engine"""
        return {
            "gtts": [
                "en", "es", "fr", "de", "it", "pt", "ru", "ja", 
                "ko", "zh", "hi", "ar", "nl", "pl", "sv", "tr"
            ],
            "espeak": [
                "en", "es", "fr", "de", "it", "pt", "ru", "ja",
                "ko", "zh", "hi", "ar", "nl", "pl", "sv", "tr",
                "da", "fi", "no", "cs", "hu", "ro", "sk", "bg"
            ],
            "festival": ["en"],
            "browser": ["all"]  # Depends on browser support
        }

# Global TTS instance
iris_tts = IRISTextToSpeech()
