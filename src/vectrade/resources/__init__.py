"""VecTrade API resource modules."""

from vectrade.resources.ai import AI, AsyncAI
from vectrade.resources.analyst import Analyst, AsyncAnalyst
from vectrade.resources.developer import AsyncDeveloper, Developer
from vectrade.resources.earnings import AsyncEarnings, Earnings
from vectrade.resources.fundamentals import AsyncFundamentals, Fundamentals
from vectrade.resources.insider import AsyncInsider, Insider
from vectrade.resources.news import AsyncNews, News
from vectrade.resources.options import AsyncOptions, Options
from vectrade.resources.quotes import AsyncQuotes, Quotes
from vectrade.resources.screener import AsyncScreener, Screener
from vectrade.resources.technicals import AsyncTechnicals, Technicals
from vectrade.resources.webhooks import AsyncWebhooks, Webhooks

__all__ = [
    "AI",
    "Analyst",
    "AsyncAI",
    "AsyncAnalyst",
    "AsyncDeveloper",
    "AsyncEarnings",
    "AsyncFundamentals",
    "AsyncInsider",
    "AsyncNews",
    "AsyncOptions",
    "AsyncQuotes",
    "AsyncScreener",
    "AsyncTechnicals",
    "AsyncWebhooks",
    "Developer",
    "Earnings",
    "Fundamentals",
    "Insider",
    "News",
    "Options",
    "Quotes",
    "Screener",
    "Technicals",
    "Webhooks",
]
