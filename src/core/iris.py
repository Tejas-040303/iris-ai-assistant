"""
IRIS Core Intelligence Module
Basic AI reasoning and response generation
"""

import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime
from src.core.hybrid_intelligence import hybrid_ai

class IRISCore:
    """Core IRIS intelligence system"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_context = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize IRIS core systems"""
        print("🤖 Initializing IRIS Core Intelligence...")
        # Simulate initialization
        await asyncio.sleep(1)
        self.is_initialized = True
        print("✅ IRIS Core initialized successfully!")
    
    async def process_message(self, message: str, user_id: str = "default") -> Dict:
        """Process user message using hybrid intelligence"""
        
        if not self.is_initialized:
            await self.initialize()
        
        # Store message in conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message": message,
            "type": "user"
        })
        
        # Get user context
        context = self.user_context.get(user_id, {})
        context["conversation_history"] = self.get_conversation_history(user_id, 5)
        
        # Process through hybrid AI system
        ai_result = await hybrid_ai.process_request(message, user_id, context)
        
        response = ai_result["response"]
        
        # Store response in history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message": response,
            "type": "iris",
            "provider": ai_result["provider_used"],
            "confidence": ai_result["confidence"]
        })
        
        return {
            "response": response,
            "confidence": ai_result["confidence"],
            "intent": self._detect_intent(message),
            "context": context,
            "provider_used": ai_result["provider_used"],
            "processing_time": ai_result.get("processing_time", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_response(self, message: str, user_id: str) -> str:
        """Generate response based on message"""
        
        message_lower = message.lower()
        
        # Basic intent-based responses
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            return "🤖 Hello! I'm IRIS, your intelligent voice assistant. How can I help you today?"
        
        elif any(word in message_lower for word in ["how are you", "how do you do"]):
            return "🤖 I'm functioning perfectly! All systems are operational and ready to assist you."
        
        elif any(word in message_lower for word in ["name", "who are you"]):
            return "🤖 I'm IRIS - Intelligent Responsive Interface System. I'm here to help you with various tasks through voice interaction!"
        
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return """🤖 I can help you with:
            • Voice conversations and natural language processing
            • Task planning and execution
            • Web searching and information retrieval
            • Calendar and scheduling management
            • File processing and document analysis
            • And much more! I'm still learning and growing."""
        
        elif any(word in message_lower for word in ["time", "date"]):
            return f"🤖 The current time is {datetime.now().strftime('%H:%M:%S')} on {datetime.now().strftime('%Y-%m-%d')}"
        
        elif any(word in message_lower for word in ["weather"]):
            return "🤖 Weather integration is coming soon! I'll be able to check current weather and forecasts for you."
        
        elif any(word in message_lower for word in ["bye", "goodbye", "see you"]):
            return "🤖 Goodbye! It was great talking with you. I'll be here whenever you need assistance!"
        
        else:
            return f"🤖 I understand you said: '{message}'. I'm still learning, but I'm processing your request. More advanced AI capabilities are coming soon!"
    
    def _detect_intent(self, message: str) -> str:
        """Basic intent detection"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "greeting"
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return "help_request"
        elif any(word in message_lower for word in ["time", "date"]):
            return "time_query"
        elif any(word in message_lower for word in ["weather"]):
            return "weather_query"
        elif any(word in message_lower for word in ["bye", "goodbye"]):
            return "farewell"
        else:
            return "general_query"
    
    def get_conversation_history(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        user_history = [
            msg for msg in self.conversation_history 
            if msg.get("user_id") == user_id
        ]
        return user_history[-limit:]

# Global IRIS instance
iris_core = IRISCore()
