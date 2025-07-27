"""
IRIS Hybrid Intelligence System
Combines local and cloud AI services with smart routing
"""

import asyncio
import time
from typing import Dict, List, Optional, Union
from enum import Enum
import random

class AIProvider(Enum):
    OLLAMA_LOCAL = "ollama_local"
    HUGGINGFACE_LOCAL = "huggingface_local"
    HUGGINGFACE_CLOUD = "huggingface_cloud"
    OPENAI_CLOUD = "openai_cloud"
    FALLBACK_LOCAL = "fallback_local"

class ProviderStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

class HybridIntelligenceManager:
    """Manages multiple AI providers with intelligent routing"""
    
    def __init__(self):
        self.providers = {
            AIProvider.OLLAMA_LOCAL: {
                "status": ProviderStatus.AVAILABLE,
                "priority": 1,  # Highest priority (local, free, private)
                "cost": 0,
                "latency": 2.0,
                "quality": 0.85,
                "last_used": 0,
                "rate_limit": None,
                "error_count": 0
            },
            AIProvider.HUGGINGFACE_LOCAL: {
                "status": ProviderStatus.AVAILABLE,
                "priority": 2,
                "cost": 0,
                "latency": 3.0,
                "quality": 0.80,
                "last_used": 0,
                "rate_limit": None,
                "error_count": 0
            },
            AIProvider.HUGGINGFACE_CLOUD: {
                "status": ProviderStatus.AVAILABLE,
                "priority": 3,
                "cost": 0,  # Free tier
                "latency": 1.5,
                "quality": 0.88,
                "last_used": 0,
                "rate_limit": {"max_requests": 1000, "per_hour": 1, "current": 0},
                "error_count": 0
            },
            AIProvider.OPENAI_CLOUD: {
                "status": ProviderStatus.AVAILABLE,
                "priority": 4,
                "cost": 0.002,  # Per 1K tokens
                "latency": 1.2,
                "quality": 0.95,
                "last_used": 0,
                "rate_limit": {"max_requests": 60, "per_minute": 1, "current": 0},
                "error_count": 0
            },
            AIProvider.FALLBACK_LOCAL: {
                "status": ProviderStatus.AVAILABLE,
                "priority": 5,  # Last resort
                "cost": 0,
                "latency": 0.1,
                "quality": 0.50,
                "last_used": 0,
                "rate_limit": None,
                "error_count": 0
            }
        }
        
        self.routing_strategy = "smart"  # smart, cost_first, speed_first, quality_first
        self.fallback_enabled = True
        
    async def process_request(self, message: str, user_id: str, context: Dict = None) -> Dict:
        """Process AI request with intelligent provider selection"""
        
        # Select best provider
        selected_provider = self._select_provider(message, context)
        
        try:
            # Attempt processing with selected provider
            result = await self._process_with_provider(selected_provider, message, user_id, context)
            
            # Update provider stats on success
            self._update_provider_stats(selected_provider, success=True)
            
            return {
                "response": result["response"],
                "provider_used": selected_provider.value,
                "confidence": result.get("confidence", 0.8),
                "processing_time": result.get("processing_time", 0),
                "cost_estimate": self.providers[selected_provider]["cost"],
                "status": "success"
            }
            
        except Exception as e:
            # Update provider stats on failure
            self._update_provider_stats(selected_provider, success=False, error=str(e))
            
            # Try fallback providers
            if self.fallback_enabled:
                return await self._try_fallback_providers(message, user_id, context, exclude=selected_provider)
            else:
                raise e
    
    def _select_provider(self, message: str, context: Dict = None) -> AIProvider:
        """Select the best provider based on current strategy and conditions"""
        
        available_providers = [
            provider for provider, info in self.providers.items()
            if info["status"] == ProviderStatus.AVAILABLE and self._check_rate_limit(provider)
        ]
        
        if not available_providers:
            return AIProvider.FALLBACK_LOCAL
        
        if self.routing_strategy == "smart":
            return self._smart_selection(available_providers, message, context)
        elif self.routing_strategy == "cost_first":
            return min(available_providers, key=lambda p: self.providers[p]["cost"])
        elif self.routing_strategy == "speed_first":
            return min(available_providers, key=lambda p: self.providers[p]["latency"])
        elif self.routing_strategy == "quality_first":
            return max(available_providers, key=lambda p: self.providers[p]["quality"])
        else:
            return min(available_providers, key=lambda p: self.providers[p]["priority"])
    
    def _smart_selection(self, providers: List[AIProvider], message: str, context: Dict) -> AIProvider:
        """Intelligent provider selection based on multiple factors"""
        
        def calculate_score(provider: AIProvider) -> float:
            info = self.providers[provider]
            
            # Base score from quality and priority
            score = info["quality"] * 0.4 + (6 - info["priority"]) * 0.1
            
            # Penalize high latency
            score -= info["latency"] * 0.1
            
            # Penalize cost (prefer free)
            score -= info["cost"] * 10
            
            # Penalize recent errors
            score -= info["error_count"] * 0.05
            
            # Bonus for local providers (privacy)
            if "local" in provider.value.lower():
                score += 0.2
            
            # Consider message complexity
            if len(message) > 500:  # Complex query, prefer high-quality providers
                score += info["quality"] * 0.2
            
            return max(0, score)
        
        # Calculate scores and select best
        scored_providers = [(provider, calculate_score(provider)) for provider in providers]
        return max(scored_providers, key=lambda x: x[1])[0]
    
    async def _process_with_provider(self, provider: AIProvider, message: str, user_id: str, context: Dict) -> Dict:
        """Process request with specific provider"""
        
        start_time = time.time()
        
        if provider == AIProvider.OLLAMA_LOCAL:
            result = await self._ollama_process(message, context)
        elif provider == AIProvider.HUGGINGFACE_LOCAL:
            result = await self._huggingface_local_process(message, context)
        elif provider == AIProvider.HUGGINGFACE_CLOUD:
            result = await self._huggingface_cloud_process(message, context)
        elif provider == AIProvider.OPENAI_CLOUD:
            result = await self._openai_process(message, context)
        else:  # FALLBACK_LOCAL
            result = await self._fallback_process(message, context)
        
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        return result
    
    async def _ollama_process(self, message: str, context: Dict) -> Dict:
        """Process using local Ollama"""
        try:
            # Simulate Ollama API call (replace with actual implementation)
            await asyncio.sleep(0.5)  # Simulate processing time
            
            response = f"🤖 [Ollama/Llama3.1] {self._generate_contextual_response(message, context)}"
            
            return {
                "response": response,
                "confidence": 0.85
            }
        except Exception as e:
            raise Exception(f"Ollama processing failed: {str(e)}")
    
    async def _huggingface_local_process(self, message: str, context: Dict) -> Dict:
        """Process using local Hugging Face model"""
        try:
            await asyncio.sleep(0.8)  # Simulate processing time
            
            response = f"🤖 [HF/Local] {self._generate_contextual_response(message, context)}"
            
            return {
                "response": response,
                "confidence": 0.80
            }
        except Exception as e:
            raise Exception(f"Hugging Face local processing failed: {str(e)}")
    
    async def _huggingface_cloud_process(self, message: str, context: Dict) -> Dict:
        """Process using Hugging Face cloud API"""
        try:
            await asyncio.sleep(0.3)  # Simulate processing time
            
            response = f"🤖 [HF/Cloud] {self._generate_contextual_response(message, context)}"
            
            return {
                "response": response,
                "confidence": 0.88
            }
        except Exception as e:
            raise Exception(f"Hugging Face cloud processing failed: {str(e)}")
    
    async def _openai_process(self, message: str, context: Dict) -> Dict:
        """Process using OpenAI API"""
        try:
            await asyncio.sleep(0.2)  # Simulate processing time
            
            response = f"🤖 [OpenAI/GPT-4] {self._generate_contextual_response(message, context)}"
            
            return {
                "response": response,
                "confidence": 0.95
            }
        except Exception as e:
            raise Exception(f"OpenAI processing failed: {str(e)}")
    
    async def _fallback_process(self, message: str, context: Dict) -> Dict:
        """Basic fallback processing"""
        templates = [
            f"I understand you're asking about '{message}'. Let me help you with that.",
            f"That's an interesting question about '{message}'. Here's what I think...",
            f"Regarding '{message}', I can provide some insights.",
            f"I see you mentioned '{message}'. Let me assist you."
        ]
        
        response = random.choice(templates)
        
        return {
            "response": response,
            "confidence": 0.50
        }
    
    def _generate_contextual_response(self, message: str, context: Dict) -> str:
        """Generate contextual response based on message and context"""
        message_lower = message.lower()

        # Detect language and respond appropriately
        if any(word in message for word in ["नमस्ते", "हेलो"]):  # Hindi
            if any(word in message for word in ["नमस्ते"]):
                return "नमस्ते! मैं IRIS हूं, आपका बुद्धिमान सहायक। मैं आपकी कैसे मदद कर सकता हूं?"
            return "हैलो! मैं IRIS हूं। आपका स्वागत है!"

        elif any(word in message_lower for word in ["hello", "hi", "hey", "helo"]):
            return "Hello! I'm IRIS, powered by advanced AI. How can I assist you today?"

        elif any(word in message_lower for word in ["what can you do", "capabilities", "help"]):
            return (
                "I'm IRIS, your intelligent voice assistant! Here's what I can do for you:\n\n"
                "🎤 Voice Interaction: Natural speech recognition in multiple languages\n"
                "🧠 AI Intelligence: Powered by a hybrid local/cloud AI for optimal performance\n"
                "🌐 Web Integration: Search the web and gather information\n"
                "📅 Task Management: Assist with scheduling, reminders, and organization\n"
                "📂 File Processing: Read and analyze documents, PDFs, and text files\n"
                "🗣️ Multi-language Support: Communicate fluently in English, Hindi, and more\n"
                "🔒 Privacy-First: Prioritize local processing to keep your data secure\n\n"
                "Just speak naturally, and I'll understand exactly what you need!"
            )

        elif any(word in message_lower for word in ["okay", "ok", "good", "fine"]):
            return "Great! Is there anything specific you'd like me to help you with? I'm here and ready to assist!"

        elif any(word in message_lower for word in ["weather", "temperature"]):
            return "I can help with weather information. Weather integration is being enhanced with multiple data sources."

        elif any(word in message_lower for word in ["time", "date", "clock"]):
            return f"The current time is {time.strftime('%H:%M:%S')} on {time.strftime('%Y-%m-%d')}. I'm running in hybrid mode for optimal performance."

        else:
            return f"I understand you said: '{message}'. I'm processing this using my hybrid intelligence system that combines local privacy with cloud capabilities. How can I help you further?"

    
    async def _try_fallback_providers(self, message: str, user_id: str, context: Dict, exclude: AIProvider) -> Dict:
        """Try alternative providers when primary fails"""
        
        available_providers = [
            provider for provider in self.providers.keys()
            if provider != exclude and self.providers[provider]["status"] == ProviderStatus.AVAILABLE
        ]
        
        # Sort by priority
        available_providers.sort(key=lambda p: self.providers[p]["priority"])
        
        for provider in available_providers:
            try:
                result = await self._process_with_provider(provider, message, user_id, context)
                result["fallback_used"] = True
                result["original_provider_failed"] = exclude.value
                return result
            except Exception:
                continue
        
        # If all providers fail, use basic fallback
        return {
            "response": f"I apologize, but I'm experiencing technical difficulties. I understand you said: '{message}'. Please try again in a moment.",
            "provider_used": "emergency_fallback",
            "confidence": 0.1,
            "status": "degraded"
        }
    
    def _check_rate_limit(self, provider: AIProvider) -> bool:
        """Check if provider is within rate limits"""
        rate_limit = self.providers[provider].get("rate_limit")
        if not rate_limit:
            return True
        
        # Simple rate limiting check (implement more sophisticated logic as needed)
        current_time = time.time()
        if "per_hour" in rate_limit:
            # Reset hourly counters
            if current_time - self.providers[provider]["last_used"] > 3600:
                rate_limit["current"] = 0
        elif "per_minute" in rate_limit:
            # Reset minute counters
            if current_time - self.providers[provider]["last_used"] > 60:
                rate_limit["current"] = 0
        
        return rate_limit["current"] < rate_limit["max_requests"]
    
    def _update_provider_stats(self, provider: AIProvider, success: bool, error: str = None):
        """Update provider statistics"""
        self.providers[provider]["last_used"] = time.time()
        
        if success:
            self.providers[provider]["error_count"] = max(0, self.providers[provider]["error_count"] - 1)
            if self.providers[provider]["status"] == ProviderStatus.ERROR:
                self.providers[provider]["status"] = ProviderStatus.AVAILABLE
        else:
            self.providers[provider]["error_count"] += 1
            if self.providers[provider]["error_count"] >= 3:
                self.providers[provider]["status"] = ProviderStatus.ERROR
        
        # Update rate limit counters
        rate_limit = self.providers[provider].get("rate_limit")
        if rate_limit:
            rate_limit["current"] += 1
    
    def get_provider_status(self) -> Dict:
        """Get current status of all providers"""
        return {
            provider.value: {
                "status": info["status"].value,
                "priority": info["priority"],
                "quality": info["quality"],
                "latency": info["latency"],
                "cost": info["cost"],
                "error_count": info["error_count"]
            }
            for provider, info in self.providers.items()
        }
    
    def set_routing_strategy(self, strategy: str):
        """Change routing strategy"""
        valid_strategies = ["smart", "cost_first", "speed_first", "quality_first"]
        if strategy in valid_strategies:
            self.routing_strategy = strategy
        else:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")

# Global hybrid intelligence manager
hybrid_ai = HybridIntelligenceManager()
