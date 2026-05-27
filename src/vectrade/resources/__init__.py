"""VecTrade API resource modules."""

from vectrade.resources.analyst import Analyst, AsyncAnalyst
from vectrade.resources.earnings import AsyncEarnings, Earnings
from vectrade.resources.etf import AsyncETF, ETF
from vectrade.resources.fundamentals import AsyncFundamentals, Fundamentals
from vectrade.resources.historical import AsyncHistorical, Historical
from vectrade.resources.insider import AsyncInsider, Insider
from vectrade.resources.news import AsyncNews, News
from vectrade.resources.options import AsyncOptions, Options
from vectrade.resources.profile import AsyncProfile, Profile
from vectrade.resources.quotes import AsyncQuotes, Quotes
from vectrade.resources.sentiment import AsyncSentiment, Sentiment
from vectrade.resources.technicals import AsyncTechnicals, Technicals

__all__ = [
    "Analyst",
    "AsyncAnalyst",
    "AsyncEarnings",
    "AsyncETF",
    "AsyncFundamentals",
    "AsyncHistorical",
    "AsyncInsider",
    "AsyncNews",
    "AsyncOptions",
    "AsyncProfile",
    "AsyncQuotes",
    "AsyncSentiment",
    "AsyncTechnicals",
    "Earnings",
    "ETF",
    "Fundamentals",
    "Historical",
    "Insider",
    "News",
    "Options",
    "Profile",
    "Quotes",
    "Sentiment",
    "Technicals",
]
