from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class ShortenRequest(BaseModel):
    original_url: HttpUrl = Field(..., description="The original target URL to shorten")
    custom_alias: Optional[str] = Field(
        None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Optional custom alias (3-30 chars, alphanumeric/hyphens/underscores)",
    )


class ShortenResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    total_clicks: int = Field(..., description="Total redirect clicks recorded")
