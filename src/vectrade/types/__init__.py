"""Response types for the VecTrade API."""

from vectrade.types.quote import QuoteResponse
from vectrade.types.fundamental import FundamentalResponse, IncomeStatement, BalanceSheet
from vectrade.types.technical import TechnicalResponse, CandleData, IndicatorValue
from vectrade.types.news import NewsArticle
from vectrade.types.screener import ScreenerResult
from vectrade.types.webhook import WebhookEvent, WebhookSubscription
from vectrade.types.options import OptionContract, OptionsChain
from vectrade.types.analyst import AnalystConsensus, PriceTarget, AnalystRating
from vectrade.types.earnings import EarningsResult, EarningsCalendarEntry
from vectrade.types.insider import InsiderTransaction, InsiderSummary

__all__ = [
    "QuoteResponse",
    "FundamentalResponse",
    "IncomeStatement",
    "BalanceSheet",
    "TechnicalResponse",
    "CandleData",
    "IndicatorValue",
    "NewsArticle",
    "ScreenerResult",
    "WebhookEvent",
    "WebhookSubscription",
    "OptionContract",
    "OptionsChain",
    "AnalystConsensus",
    "PriceTarget",
    "AnalystRating",
    "EarningsResult",
    "EarningsCalendarEntry",
    "InsiderTransaction",
    "InsiderSummary",
]
