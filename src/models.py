from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class ShortenRequest(BaseModel):
    original_url: HttpUrl = Field(..., description="The original target URL to shorten")
    custom_alias: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Optional custom alias (3-30 chars, alphanumeric/hyphens/underscores)",
    )


class ShortenResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    clicks: int = 0


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    total_clicks: int = Field(..., description="Total redirect clicks recorded")


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any | None = None
