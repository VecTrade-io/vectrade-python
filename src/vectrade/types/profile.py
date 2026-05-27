"""Company profile response models."""

from __future__ import annotations

from pydantic import BaseModel


class CompanyInfo(BaseModel):
    """Company basic info."""

    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    exchange: str | None = None
    website: str | None = None
    security_type: str | None = None


class LocationInfo(BaseModel):
    """Company location."""

    country: str | None = None
    state: str | None = None
    city: str | None = None
    address: str | None = None
    phone: str | None = None


class ProfileResponse(BaseModel):
    """Company profile data."""

    model_config = {"populate_by_name": True}

    ticker: str
    source: str | None = None
    company: CompanyInfo | None = None
    location: LocationInfo | None = None
    overview: dict | None = None
