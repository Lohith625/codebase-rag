"""
Prompt Templates
Templates for LLM interactions.
"""

from typing import List, Dict


CODE_ASSISTANT_SYSTEM_PROMPT = """You are an expert code assistant helping developers understand and navigate codebases.

Your capabilities:
- Explain code functionality clearly and concisely
- Provide accurate information based on retrieved code context
- Reference specific files and line numbers
- Suggest best practices and improvements
- Help debug issues

Guidelines:
- Always cite your sources (file names and line numbers)
- If you're not sure, say so
- Keep explanations clear and practical
- Use code examples when helpful
- Be concise but thorough
"""


def create_search_prompt(query: str, context: List[Dict]) -> str:
    """
    Create prompt for code search query.
    
    Args:
        query: User's question
        context: Retrieved code context
    
    Returns:
        Formatted prompt
    """
    prompt = f"{CODE_ASSISTANT_SYSTEM_PROMPT}\n\n"
    prompt += "## Retrieved Code Context\n\n"
    
    for i, item in enumerate(context, 1):
        metadata = item.get('metadata', {})
        content = item.get('content', metadata.get('content', ''))
        
        prompt += f"### Context {i}\n"
        prompt += f"**File**: {metadata.get('file_path', 'N/A')}\n"
        prompt += f"**Type**: {metadata.get('type', 'code')}\n"
        if metadata.get('name'):
            prompt += f"**Name**: {metadata.get('name')}\n"
        prompt += f"**Lines**: {metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}\n"
        prompt += f"**Language**: {metadata.get('language', 'N/A')}\n"
        prompt += f"\n```{metadata.get('language', '')}\n{content}\n```\n\n"
    
    prompt += f"## User Question\n{query}\n\n"
    prompt += "## Instructions\n"
    prompt += "Based on the code context above, answer the user's question. "
    prompt += "Include specific references to files and line numbers. "
    prompt += "If the context doesn't contain enough information, say so.\n\n"
    prompt += "Answer:"
    
    return prompt


def create_explanation_prompt(code: str, language: str) -> str:
    """Create prompt for code explanation."""
    prompt = f"{CODE_ASSISTANT_SYSTEM_PROMPT}\n\n"
    prompt += f"## Code to Explain\n\n"
    prompt += f"```{language}\n{code}\n```\n\n"
    prompt += "Explain what this code does, including:\n"
    prompt += "1. Main purpose and functionality\n"
    prompt += "2. Key components and their roles\n"
    prompt += "3. Important details or patterns used\n"
    prompt += "4. Potential issues or improvements\n\n"
    prompt += "Explanation:"
    
    return prompt


def create_debug_prompt(error: str, context: List[Dict]) -> str:
    """Create prompt for debugging assistance."""
    prompt = f"{CODE_ASSISTANT_SYSTEM_PROMPT}\n\n"
    prompt += f"## Error/Issue\n{error}\n\n"
    prompt += "## Related Code Context\n\n"
    
    for i, item in enumerate(context, 1):
        metadata = item.get('metadata', {})
        content = item.get('content', metadata.get('content', ''))
        
        prompt += f"### Context {i}\n"
        prompt += f"**File**: {metadata.get('file_path', 'N/A')}\n"
        prompt += f"```{metadata.get('language', '')}\n{content}\n```\n\n"
    
    prompt += "## Task\n"
    prompt += "Analyze the error and code context to:\n"
    prompt += "1. Identify the likely cause\n"
    prompt += "2. Suggest a fix\n"
    prompt += "3. Explain why this error occurred\n\n"
    prompt += "Analysis:"
    
    return prompt


def create_implementation_prompt(task: str, examples: List[Dict]) -> str:
    """Create prompt for implementation guidance."""
    prompt = f"{CODE_ASSISTANT_SYSTEM_PROMPT}\n\n"
    prompt += f"## Task\n{task}\n\n"
    
    if examples:
        prompt += "## Similar Code Examples\n\n"
        for i, ex in enumerate(examples, 1):
            metadata = ex.get('metadata', {})
            content = ex.get('content', metadata.get('content', ''))
            prompt += f"### Example {i}\n"
            prompt += f"```{metadata.get('language', '')}\n{content}\n```\n\n"
    
    prompt += "## Instructions\n"
    prompt += "Provide guidance on how to implement this task, including:\n"
    prompt += "1. High-level approach\n"
    prompt += "2. Key components needed\n"
    prompt += "3. Code structure/skeleton\n"
    prompt += "4. Important considerations\n\n"
    prompt += "Guidance:"
    
    return prompt
