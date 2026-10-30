"""VecTrade API resource modules."""

from vectrade.resources.ai import AI, AIChunk, AsyncAI
from vectrade.resources.analyst import Analyst, AsyncAnalyst
from vectrade.resources.developer import AsyncDeveloper, Developer
from vectrade.resources.earnings import AsyncEarnings, Earnings
from vectrade.resources.etf import ETF, AsyncETF
from vectrade.resources.fundamentals import AsyncFundamentals, Fundamentals
from vectrade.resources.historical import AsyncHistorical, Historical
from vectrade.resources.insider import AsyncInsider, Insider
from vectrade.resources.news import AsyncNews, News
from vectrade.resources.options import AsyncOptions, Options
from vectrade.resources.profile import AsyncProfile, Profile
from vectrade.resources.quotes import AsyncQuotes, Quotes
from vectrade.resources.screener import AsyncScreener, Screener
from vectrade.resources.sentiment import AsyncSentiment, Sentiment
from vectrade.resources.technicals import AsyncTechnicals, Technicals
from vectrade.resources.webhooks import AsyncWebhooks, Webhooks

__all__ = [
    "AI",
    "ETF",
    "AIChunk",
    "Analyst",
    "AsyncAI",
    "AsyncAnalyst",
    "AsyncDeveloper",
    "AsyncETF",
    "AsyncEarnings",
    "AsyncFundamentals",
    "AsyncHistorical",
    "AsyncInsider",
    "AsyncNews",
    "AsyncOptions",
    "AsyncProfile",
    "AsyncQuotes",
    "AsyncScreener",
    "AsyncSentiment",
    "AsyncTechnicals",
    "AsyncWebhooks",
    "Developer",
    "Earnings",
    "Fundamentals",
    "Historical",
    "Insider",
    "News",
    "Options",
    "Profile",
    "Quotes",
    "Screener",
    "Sentiment",
    "Technicals",
    "Webhooks",
]
