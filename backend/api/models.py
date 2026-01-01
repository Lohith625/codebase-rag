"""
API Models
Pydantic models for request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for code search query."""

    query: str = Field(..., description="User's natural language question")
    language: Optional[str] = Field(None, description="Filter by programming language")
    code_type: Optional[str] = Field(
        None, description="Filter by code type (function, class, etc.)"
    )
    top_k: Optional[int] = Field(5, description="Number of results to return")
    include_context: Optional[bool] = Field(
        True, description="Include full context in response"
    )


class SourceReference(BaseModel):
    """Source code reference."""

    file: str
    path: str
    type: str
    name: str
    lines: str
    language: str
    relevance: float


class QueryResponse(BaseModel):
    """Response model for code search query."""

    answer: str
    sources: List[SourceReference]
    num_sources: int
    query_info: Dict[str, Any]
    processing_time: float


class IngestRequest(BaseModel):
    """Request model for repository ingestion."""

    repo_url: str = Field(..., description="GitHub repository URL")
    branch: Optional[str] = Field("main", description="Branch to clone")
    extensions: Optional[List[str]] = Field(
        None, description="File extensions to index"
    )


class IngestResponse(BaseModel):
    """Response model for repository ingestion."""

    status: str
    message: str
    repo_name: str
    files_processed: int
    chunks_created: int
    chunks_indexed: int


class ExplainRequest(BaseModel):
    """Request model for code explanation."""

    code: str = Field(..., description="Code snippet to explain")
    language: Optional[str] = Field("python", description="Programming language")


class ExplainResponse(BaseModel):
    """Response model for code explanation."""

    explanation: str
    code_snippet: str
    language: str


class DebugRequest(BaseModel):
    """Request model for debug help."""

    error_message: str = Field(..., description="Error message or description")
    language: Optional[str] = Field(None, description="Programming language")


class DebugResponse(BaseModel):
    """Response model for debug help."""

    analysis: str
    related_code: List[SourceReference]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    index_stats: Dict[str, Any]
