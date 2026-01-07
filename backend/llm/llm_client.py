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
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            from config.settings import settings
            
            self.api_key = api_key or settings.gemini_api_key
            
            if not self.api_key:
                logger.warning("No Gemini API key provided")
                self.model = None
                return
            
            genai.configure(api_key=self.api_key)
            
            model_options = ["gemini-pro", "gemini-1.5-pro", "models/gemini-pro"]
            
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
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response from Gemini."""
        if not self.model:
            return "Error: Gemini model not initialized."
        
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
            return f"Error: {str(e)}"
    
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
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response from OpenAI."""
        if not self.client:
            return "Error: OpenAI client not initialized."
        
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
            return f"Error: {str(e)}"
    
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
    """Intelligent Mock LLM - generates contextual responses based on retrieved code."""
    
    def __init__(self):
        """Initialize mock client."""
        logger.info("MockLLMClient initialized (intelligent context-aware mode)")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate intelligent context-aware mock response."""
        
        # Extract query and context from prompt
        query = self._extract_query(prompt)
        contexts = self._extract_contexts(prompt)
        
        if not contexts:
            return self._no_results_response(query)
        
        # Generate contextual response based on retrieved code
        return self._generate_contextual_response(query, contexts)
    
    def _extract_query(self, prompt: str) -> str:
        """Extract user query from prompt."""
        if "User Question" in prompt:
            start = prompt.find("User Question") + len("User Question")
            end = prompt.find("##", start)
            if end > start:
                return prompt[start:end].strip()
        return "your query"
    
    def _extract_contexts(self, prompt: str) -> List[Dict]:
        """Extract code contexts from prompt."""
        contexts = []
        parts = prompt.split("### Context")
        
        for i, part in enumerate(parts[1:], 1):
            context = {}
            
            # Extract file name
            if "**File**:" in part:
                file_start = part.find("**File**:") + len("**File**:")
                file_end = part.find("\n", file_start)
                context['file'] = part[file_start:file_end].strip()
            
            # Extract type
            if "**Type**:" in part:
                type_start = part.find("**Type**:") + len("**Type**:")
                type_end = part.find("\n", type_start)
                context['type'] = part[type_start:type_end].strip()
            
            # Extract name
            if "**Name**:" in part:
                name_start = part.find("**Name**:") + len("**Name**:")
                name_end = part.find("\n", name_start)
                context['name'] = part[name_start:name_end].strip()
            
            # Extract code
            if "```" in part:
                code_start = part.find("```") + 3
                # Skip language identifier
                if "\n" in part[code_start:code_start+20]:
                    code_start = part.find("\n", code_start) + 1
                code_end = part.find("```", code_start)
                if code_end > code_start:
                    context['code'] = part[code_start:code_end].strip()
            
            if context:
                contexts.append(context)
        
        return contexts
    
    def _generate_contextual_response(self, query: str, contexts: List[Dict]) -> str:
        """Generate intelligent response based on actual retrieved code."""
        
        # Analyze the contexts
        function_names = [c.get('name', '') for c in contexts if c.get('type') == 'function']
        class_names = [c.get('name', '') for c in contexts if c.get('type') == 'class']
        files = list(set([c.get('file', '') for c in contexts if c.get('file')]))
        
        response_parts = []
        
        # Opening based on query
        if any(word in query.lower() for word in ['how', 'explain', 'what']):
            response_parts.append(f"Based on the codebase analysis, here's how **{query.lower().replace('how does ', '').replace('how ', '').replace('what ', '').strip('?')}** works:\n")
        elif 'where' in query.lower():
            response_parts.append(f"I found **{len(contexts)} relevant code locations** for your query:\n")
        else:
            response_parts.append(f"Here's what I found regarding **{query}**:\n")
        
        # Main findings
        if function_names:
            response_parts.append(f"\n**Key Functions:**")
            for name in function_names[:3]:
                response_parts.append(f"- `{name}()` - Handles core functionality")
        
        if class_names:
            response_parts.append(f"\n**Related Classes:**")
            for name in class_names[:2]:
                response_parts.append(f"- `{name}` - Main implementation class")
        
        # Code snippets analysis
        response_parts.append(f"\n**Implementation Details:**")
        
        for i, ctx in enumerate(contexts[:2], 1):
            if ctx.get('code'):
                code_preview = ctx['code'][:150]
                response_parts.append(f"\n{i}. In `{ctx.get('file', 'unknown')}` ({ctx.get('type', 'code')}):")
                
                # Analyze code patterns
                if 'def ' in code_preview or 'function ' in code_preview:
                    response_parts.append("   - Defines functionality")
                if 'class ' in code_preview:
                    response_parts.append("   - Object-oriented implementation")
                if 'return' in code_preview:
                    response_parts.append("   - Returns processed results")
                if 'import' in code_preview or 'from ' in code_preview:
                    response_parts.append("   - Uses external dependencies")
                if '@' in code_preview:
                    response_parts.append("   - Decorated with special behavior")
        
        # File locations
        if files:
            response_parts.append(f"\n**Source Files:**")
            for file in files[:3]:
                response_parts.append(f"- `{file}`")
        
        # Conclusion
        response_parts.append(f"\n**Summary:**")
        response_parts.append(f"The implementation uses {len(contexts)} code components across {len(files)} file(s). ")
        
        if function_names:
            response_parts.append(f"The main entry point is `{function_names[0]}()`. ")
        
        response_parts.append("Check the source files above for complete implementation details.")
        
        # Note about Mock LLM
        response_parts.append(f"\n\n*Note: This is an intelligent mock response based on retrieved code context. Configure Gemini/OpenAI API keys for even more detailed AI analysis.*")
        
        return "\n".join(response_parts)
    
    def _no_results_response(self, query: str) -> str:
        """Response when no code is found."""
        return f"""I couldn't find relevant code for **{query}** in the indexed repository.

**Suggestions:**
1. Make sure the repository has been indexed
2. Try rephrasing your query with different keywords
3. Check if the code exists in the repository
4. Use more specific search terms

**Current Status:**
- If the index is empty, use the "Ingest Repository" page to add code
- The system searches across all indexed code files

*Note: This is a mock response. Configure real LLM (Gemini/OpenAI) for better results.*"""
    
    def stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream mock response word by word."""
        response = self.generate(prompt, **kwargs)
        words = response.split()
        for word in words:
            yield word + " "
