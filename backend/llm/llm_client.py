"""
LLM Client
Interface for interacting with Language Models.
"""

from typing import List, Dict, Optional, Generator
from backend.utils import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Base class for LLM clients."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        raise NotImplementedError
    
    def stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream response from LLM."""
        raise NotImplementedError


class GeminiClient(LLMClient):
    """Google Gemini LLM client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model name
        """
        try:
            import google.generativeai as genai
            from config.settings import settings
            
            self.api_key = api_key or settings.gemini_api_key
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model)
            self.model_name = model
            
            logger.info(f"GeminiClient initialized (model={model})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """
        Generate response from Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        if not self.model:
            return "Error: Gemini model not initialized"
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def stream(self, prompt: str, temperature: float = 0.1) -> Generator[str, None, None]:
        """Stream response from Gemini."""
        if not self.model:
            yield "Error: Gemini model not initialized"
            return
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': temperature},
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            yield f"Error: {str(e)}"


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        try:
            from openai import OpenAI
            from config.settings import settings
            
            self.api_key = api_key or settings.openai_api_key
            self.client = OpenAI(api_key=self.api_key)
            self.model_name = model
            
            logger.info(f"OpenAIClient initialized (model={model})")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            self.client = None
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response from OpenAI."""
        if not self.client:
            return "Error: OpenAI client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful code assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def stream(self, prompt: str, temperature: float = 0.1) -> Generator[str, None, None]:
        """Stream response from OpenAI."""
        if not self.client:
            yield "Error: OpenAI client not initialized"
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful code assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield f"Error: {str(e)}"


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without API keys."""
    
    def __init__(self):
        """Initialize mock client."""
        logger.info("MockLLMClient initialized (for testing)")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response."""
        # Extract query from prompt
        if "User Question" in prompt:
            query_start = prompt.find("User Question") + len("User Question") + 1
            query_end = prompt.find("##", query_start)
            query = prompt[query_start:query_end].strip() if query_end > 0 else prompt[query_start:].strip()
        else:
            query = "the query"
        
        # Generate contextual mock response
        response = f"Based on the provided code context, here's what I found:\n\n"
        response += f"The code shows implementation details relevant to {query}. "
        response += f"Looking at the retrieved functions and classes, they handle the requested functionality. "
        response += f"\n\nKey points:\n"
        response += f"1. The main logic is implemented in the retrieved code snippets\n"
        response += f"2. You can find the relevant implementation in the specified files\n"
        response += f"3. The code follows standard patterns for this type of functionality\n\n"
        response += f"**Note**: This is a mock response for testing. "
        response += f"In production, a real LLM would provide detailed analysis based on the actual code context."
        
        return response
    
    def stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream mock response."""
        response = self.generate(prompt, **kwargs)
        # Simulate streaming by yielding words
        words = response.split()
        for word in words:
            yield word + " "
