"""Sentiment analysis response models."""

from __future__ import annotations

from pydantic import BaseModel


class SocialSentiment(BaseModel):
    """Social media sentiment metrics."""

    twitter_sentiment: float | None = None
    reddit_sentiment: float | None = None
    stocktwits_sentiment: float | None = None
    mentions_24h: int | None = None


class NewsSentimentBreakdown(BaseModel):
    """News sentiment breakdown."""

    positive: int | None = None
    neutral: int | None = None
    negative: int | None = None


class SentimentResponse(BaseModel):
    """Sentiment analysis data."""

    model_config = {"populate_by_name": True}

    sentiment_score: float | None = None
    signal: str | None = None
    sentiment_trend: str | None = None
    news_sentiment_breakdown: NewsSentimentBreakdown | None = None
    social_sentiment: SocialSentiment | None = None
