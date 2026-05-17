"""Response types for the VecTrade API."""

from vectrade.types.analyst import AnalystConsensus, AnalystRating, PriceTarget
from vectrade.types.earnings import EarningsCalendarEntry, EarningsResult
from vectrade.types.fundamental import BalanceSheet, FundamentalResponse, IncomeStatement
from vectrade.types.insider import InsiderSummary, InsiderTransaction
from vectrade.types.news import NewsArticle
from vectrade.types.options import OptionContract, OptionsChain
from vectrade.types.quote import QuoteResponse
from vectrade.types.screener import ScreenerResult
from vectrade.types.technical import CandleData, IndicatorValue, TechnicalResponse
from vectrade.types.webhook import WebhookEvent, WebhookSubscription

__all__ = [
    "AnalystConsensus",
    "AnalystRating",
    "BalanceSheet",
    "CandleData",
    "EarningsCalendarEntry",
    "EarningsResult",
    "FundamentalResponse",
    "IncomeStatement",
    "IndicatorValue",
    "InsiderSummary",
    "InsiderTransaction",
    "NewsArticle",
    "OptionContract",
    "OptionsChain",
    "PriceTarget",
    "QuoteResponse",
    "ScreenerResult",
    "TechnicalResponse",
    "WebhookEvent",
    "WebhookSubscription",
]
