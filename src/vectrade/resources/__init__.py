"""VecTrade API resource modules."""

from vectrade.resources.quotes import Quotes, AsyncQuotes
from vectrade.resources.fundamentals import Fundamentals, AsyncFundamentals
from vectrade.resources.technicals import Technicals, AsyncTechnicals
from vectrade.resources.news import News, AsyncNews
from vectrade.resources.screener import Screener, AsyncScreener
from vectrade.resources.ai import AI, AsyncAI
from vectrade.resources.webhooks import Webhooks, AsyncWebhooks
from vectrade.resources.options import Options, AsyncOptions
from vectrade.resources.analyst import Analyst, AsyncAnalyst
from vectrade.resources.earnings import Earnings, AsyncEarnings
from vectrade.resources.insider import Insider, AsyncInsider
from vectrade.resources.developer import Developer, AsyncDeveloper

__all__ = [
    "Quotes",
    "AsyncQuotes",
    "Fundamentals",
    "AsyncFundamentals",
    "Technicals",
    "AsyncTechnicals",
    "News",
    "AsyncNews",
    "Screener",
    "AsyncScreener",
    "AI",
    "AsyncAI",
    "Webhooks",
    "AsyncWebhooks",
    "Options",
    "AsyncOptions",
    "Analyst",
    "AsyncAnalyst",
    "Earnings",
    "AsyncEarnings",
    "Insider",
    "AsyncInsider",
    "Developer",
    "AsyncDeveloper",
]
