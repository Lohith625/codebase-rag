"""LLM Client - Production Ready with Latest Gemini Models"""

import os
from typing import Optional
from backend.utils import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Base LLM Client interface (for backwards compatibility)."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        raise NotImplementedError("Subclass must implement generate()")


class MockLLMClient(LLMClient):
    """Mock LLM for testing."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        prompt_lower = prompt.lower()
        
        if 'error' in prompt_lower or 'debug' in prompt_lower:
            return """Based on the code context:

1. **Check initialization** - Ensure variables are properly set
2. **Verify imports** - Confirm all dependencies are available
3. **Review error handling** - Add appropriate try-catch blocks

See the source references for working examples."""
        
        return """Based on the retrieved code:

The implementation follows standard patterns for this functionality. 
Key components work together through well-defined interfaces.

Review the source references for specific implementation details."""


class GeminiClient(LLMClient):
    """Google Gemini Client - LATEST MODELS (2025)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        
        # ⭐ Latest available models from your API
        self.models_to_try = [
            'gemini-2.5-flash',       # 🏆 NEWEST - Jan 2025, fastest & smartest
            'gemini-flash-latest',    # Latest stable alias
            'gemini-2.0-flash',       # Stable 2.0 version
            'gemini-pro-latest',      # Pro version alias
            'gemini-2.5-pro',         # Pro version (may have lower quota)
        ]
        self.working_model = None
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("⚠️ No valid Gemini API key")
            return
        
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            
            # Find first working model
            for model in self.models_to_try:
                try:
                    # Quick test
                    test_response = self.client.models.generate_content(
                        model=model,
                        contents='Hi'
                    )
                    self.working_model = model
                    logger.info(f"✅ Gemini ready with model: {model}")
                    break
                except Exception as e:
                    error_str = str(e)
                    if 'RESOURCE_EXHAUSTED' in error_str:
                        logger.warning(f"⚠️ Quota exhausted for {model}")
                        continue
                    elif 'NOT_FOUND' in error_str:
                        logger.debug(f"Model not available: {model}")
                        continue
                    else:
                        logger.warning(f"⚠️ {model} failed: {error_str[:50]}")
                        continue
            
            if not self.working_model:
                logger.error("❌ No working Gemini model found")
                logger.error("💡 Your quota may be exhausted - try again later or create new API key")
                self.client = None
                
        except ImportError:
            logger.error("❌ Run: pip install google-genai")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Gemini init failed: {e}")
            self.client = None
    
    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client or not self.working_model:
            logger.warning("⚠️ Using mock response (Gemini unavailable)")
            return MockLLMClient().generate(prompt, **kwargs)
        
        try:
            response = self.client.models.generate_content(
                model=self.working_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"❌ Generation failed: {str(e)[:100]}")
            return MockLLMClient().generate(prompt, **kwargs)


class OpenAIClient(LLMClient):
    """OpenAI Client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI client ready")
        except Exception as e:
            logger.error(f"❌ OpenAI init failed: {e}")
            self.client = None
    
    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return MockLLMClient().generate(prompt, **kwargs)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ OpenAI failed: {e}")
            return MockLLMClient().generate(prompt, **kwargs)
