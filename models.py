from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WritingMode(str, Enum):
    """Supported writing modes with distinct persona, temperature, and toolsets."""
    BLOGGER = "blogger"
    RESEARCHER = "researcher"
    BOOK_AUTHOR = "book_author"


class GenerateRequest(BaseModel):
    """Request payload schema for the /generate endpoint."""
    mode: WritingMode = Field(
        ...,
        description="The target writing mode ('blogger', 'researcher', or 'book_author').",
        examples=["blogger", "researcher", "book_author"]
    )
    prompt: str = Field(
        ...,
        min_length=1,
        description="The primary user prompt or topic to generate content for.",
        examples=["Write an engaging post on 5 AI tools transforming productivity in 2026."]
    )
    context_data: Optional[str] = Field(
        default=None,
        description="Optional supplementary context, reference material, or notes.",
        examples=["Include references to multimodal agents and latency benchmarks."]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "mode": "blogger",
                "prompt": "Write an engaging post on AI tools for productivity.",
                "context_data": "Target audience is tech-savvy founders and developers."
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    service: str = "Multi-Mode Writing Platform Backend"
    version: str = "1.0.0"
