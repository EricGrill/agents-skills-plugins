"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import Optional, Any


class OptimizeOptions(BaseModel):
    """Options for prompt optimization."""
    
    preserve_structure: bool = Field(
        default=True,
        description="Whether to preserve the overall structure of the prompt"
    )
    verbose_changelog: bool = Field(
        default=False,
        description="Whether to include detailed explanations in the changelog"
    )
    include_logs: bool = Field(
        default=True,
        description="Whether to include agent execution logs in the response"
    )


class OptimizeRequest(BaseModel):
    """Request model for the /optimize endpoint."""
    
    prompt: str = Field(
        ...,
        description="The original prompt to optimize",
        min_length=1
    )
    providers: list[str] = Field(
        ...,
        description="List of provider names to optimize for",
        min_length=1
    )
    options: OptimizeOptions = Field(
        default_factory=OptimizeOptions,
        description="Optimization options"
    )


class PromptChange(BaseModel):
    """A single change made to the prompt."""
    
    category: str = Field(
        ...,
        description="Category of the change (e.g., 'formatting', 'structure', 'clarity')"
    )
    description: str = Field(
        ...,
        description="Description of what was changed and why"
    )
    before: Optional[str] = Field(
        default=None,
        description="The original text (if applicable)"
    )
    after: Optional[str] = Field(
        default=None,
        description="The modified text (if applicable)"
    )


class AgentLogEntry(BaseModel):
    """A single log entry from agent execution."""
    
    timestamp: str = Field(..., description="ISO timestamp of the event")
    elapsed_ms: int = Field(..., description="Milliseconds since agent started")
    type: str = Field(..., description="Event type (system, tool_call, llm_response, etc.)")
    content: str = Field(..., description="Log content (may be truncated)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class OptimizedPrompt(BaseModel):
    """Result of optimizing a prompt for a single provider."""
    
    provider: str = Field(
        ...,
        description="The provider this prompt was optimized for"
    )
    prompt: str = Field(
        ...,
        description="The optimized prompt"
    )
    changes: list[PromptChange] = Field(
        default_factory=list,
        description="List of changes made to the prompt"
    )
    success: bool = Field(
        default=True,
        description="Whether the optimization was successful"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if optimization failed"
    )
    agent_logs: Optional[list[dict]] = Field(
        default=None,
        description="Detailed logs of agent execution (tool calls, LLM responses, etc.)"
    )


class OptimizeResponse(BaseModel):
    """Response model for the /optimize endpoint."""
    
    original: str = Field(
        ...,
        description="The original prompt"
    )
    optimized: dict[str, OptimizedPrompt] = Field(
        ...,
        description="Map of provider name to optimized prompt result"
    )
