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

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key
            model: Model name (use "gemini-pro" for stable access)
        """
        try:
            import google.generativeai as genai
            from config.settings import settings

            self.api_key = api_key or settings.gemini_api_key

            if not self.api_key:
                logger.warning("No Gemini API key provided")
                self.model = None
                return

            genai.configure(api_key=self.api_key)

            # Try different model names until one works
            model_options = [
                "gemini-pro",  # Most stable
                "gemini-1.5-pro",  # Newer
                "models/gemini-pro",  # Full path format
            ]

            self.model = None
            for model_name in model_options:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    logger.info(f"GeminiClient initialized (model={model_name})")
                    break
                except:
                    continue

            if not self.model:
                logger.error("Could not initialize any Gemini model")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None

    def generate(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048
    ) -> str:
        """Generate response from Gemini."""
        if not self.model:
            return "Error: Gemini model not initialized. Using fallback response."

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return f"Error: {str(e)}"

    def stream(
        self, prompt: str, temperature: float = 0.1
    ) -> Generator[str, None, None]:
        """Stream response from Gemini."""
        if not self.model:
            yield "Error: Gemini model not initialized"
            return

        try:
            response = self.model.generate_content(
                prompt, generation_config={"temperature": temperature}, stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            yield f"Error: {str(e)}"


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            from config.settings import settings

            self.api_key = api_key or settings.openai_api_key

            if not self.api_key:
                logger.warning("No OpenAI API key provided")
                self.client = None
                return

            self.client = OpenAI(api_key=self.api_key)
            self.model_name = model

            logger.info(f"OpenAIClient initialized (model={model})")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            self.client = None

    def generate(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048
    ) -> str:
        """Generate response from OpenAI."""
        if not self.client:
            return "Error: OpenAI client not initialized."

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful code assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"Error: {str(e)}"

    def stream(
        self, prompt: str, temperature: float = 0.1
    ) -> Generator[str, None, None]:
        """Stream response from OpenAI."""
        if not self.client:
            yield "Error: OpenAI client not initialized"
            return

        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful code assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                stream=True,
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
        # Extract context from prompt
        context_snippets = []
        if "### Context" in prompt:
            # Count how many contexts we have
            context_count = prompt.count("### Context")
            context_snippets = [f"code snippet {i+1}" for i in range(context_count)]

        # Generate intelligent mock response
        response = f"Based on the analysis of {len(context_snippets)} code snippets, here's what I found:\n\n"

        if context_snippets:
            response += "**Code Analysis:**\n"
            response += "The retrieved code shows several key implementations:\n\n"
            response += "1. **Main functionality**: The code implements the core logic requested in your query\n"
            response += (
                "2. **Helper functions**: Supporting functions handle specific tasks\n"
            )
            response += (
                "3. **Error handling**: Proper exception handling is implemented\n\n"
            )
            response += "**Implementation details** are available in the source files listed above. "
            response += (
                "The code follows best practices and standard design patterns.\n\n"
            )
        else:
            response += "I couldn't find relevant code for your query. Try:\n"
            response += "- Being more specific\n"
            response += "- Using different keywords\n"
            response += "- Checking if the repository has been indexed\n\n"

        response += "**Note**: This is a mock response. For detailed analysis, configure a real LLM (Gemini/OpenAI)."

        return response

    def stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream mock response."""
        response = self.generate(prompt, **kwargs)
        words = response.split()
        for word in words:
            yield word + " "
