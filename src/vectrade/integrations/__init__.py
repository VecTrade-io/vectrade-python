"""VecTrade LangChain integration — provides financial data tools for LLM agents.

Usage:
    from vectrade.integrations.langchain import VecTradeToolkit

    toolkit = VecTradeToolkit()
    tools = toolkit.get_tools()
    # Pass `tools` to your LangChain agent
"""

from __future__ import annotations

from typing import Any, Optional

from vectrade import VecTrade


class VecTradeToolkit:
    """LangChain-compatible toolkit providing VecTrade financial tools.

    Each tool follows LangChain's BaseTool interface pattern.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        sandbox: bool = False,
        include: Optional[list[str]] = None,
    ) -> None:
        """Initialize the toolkit.

        Args:
            api_key: VecTrade API key. Falls back to VECTRADE_API_KEY env var.
            sandbox: Use sandbox environment.
            include: Subset of tools to include. None = all tools.
        """
        self._client = VecTrade(api_key=api_key, sandbox=sandbox)
        self._include = include

    def get_tools(self) -> list[Any]:
        """Return LangChain-compatible tool definitions.

        Returns a list of tool objects with name, description, and func attributes.
        """
        all_tools = [
            self._make_tool(
                name="vectrade_get_quote",
                description="Get a real-time stock quote. Input: stock ticker symbol (e.g., 'AAPL').",
                func=self._get_quote,
            ),
            self._make_tool(
                name="vectrade_get_fundamentals",
                description="Get company fundamentals (PE ratio, market cap, sector). Input: stock ticker symbol.",
                func=self._get_fundamentals,
            ),
            self._make_tool(
                name="vectrade_get_technicals",
                description="Get technical indicators (RSI, MACD, SMA). Input: stock ticker symbol.",
                func=self._get_technicals,
            ),
            self._make_tool(
                name="vectrade_get_news",
                description="Get latest financial news for a symbol. Input: stock ticker symbol.",
                func=self._get_news,
            ),
            self._make_tool(
                name="vectrade_ai_analyze",
                description="Run AI-powered financial analysis. Input: analysis prompt (e.g., 'Compare AAPL vs MSFT').",
                func=self._ai_analyze,
            ),
            self._make_tool(
                name="vectrade_screen_stocks",
                description=(
                    "Screen stocks by criteria. Input: JSON object with filter keys "
                    "(market_cap_min, pe_ratio_max, sector, dividend_yield_min)."
                ),
                func=self._screen_stocks,
            ),
        ]

        if self._include:
            return [t for t in all_tools if t.name in self._include]
        return all_tools

    def _get_quote(self, symbol: str) -> str:
        """Fetch and format a stock quote."""
        quote = self._client.quotes.get(symbol.strip().upper())
        return (
            f"{quote.symbol}: ${quote.price:.2f} "
            f"({quote.change_pct:+.2f}%) "
            f"Volume: {quote.volume:,}"
        )

    def _get_fundamentals(self, symbol: str) -> str:
        """Fetch and format company fundamentals."""
        data = self._client.fundamentals.get(symbol.strip().upper())
        return (
            f"{data.company_name} ({data.symbol})\n"
            f"Sector: {data.sector} | Industry: {data.industry}\n"
            f"Market Cap: ${data.market_cap:,.0f}\n"
            f"P/E Ratio: {data.pe_ratio}\n"
            f"EPS: ${data.eps:.2f}\n"
            f"Dividend Yield: {data.dividend_yield or 0:.2%}"
        )

    def _get_technicals(self, symbol: str) -> str:
        """Fetch and format technical indicators."""
        data = self._client.technicals.get(
            symbol.strip().upper(),
            indicators=["rsi", "macd", "sma"],
        )
        lines = [f"Technical Indicators for {data.symbol}:"]
        for name, values in data.indicators.items():
            if values:
                latest = values[-1]
                lines.append(f"  {name}: {latest.value:.2f}")
        return "\n".join(lines)

    def _get_news(self, symbol: str) -> str:
        """Fetch and format recent news."""
        articles = self._client.news.list(symbols=symbol.strip().upper(), limit=5)
        lines = [f"Recent news for {symbol.upper()}:"]
        for article in articles:
            lines.append(f"  • [{article.source}] {article.title}")
        return "\n".join(lines)

    def _ai_analyze(self, prompt: str) -> str:
        """Run AI analysis and collect full response."""
        chunks: list[str] = []
        for chunk in self._client.ai.stream(prompt):
            chunks.append(chunk.text)
        return "".join(chunks)

    def _screen_stocks(self, criteria_json: str) -> str:
        """Screen stocks based on JSON criteria."""
        import json
        criteria = json.loads(criteria_json) if isinstance(criteria_json, str) else criteria_json
        results = list(self._client.screener.run(**criteria))
        if not results:
            return "No stocks matched the given criteria."
        lines = ["Matching stocks:"]
        for r in results[:20]:
            lines.append(f"  {r.symbol} ({r.company_name}): ${r.price:.2f} ({r.change_pct:+.2f}%)")
        return "\n".join(lines)

    @staticmethod
    def _make_tool(name: str, description: str, func: Any) -> Any:
        """Create a simple tool-like object compatible with LangChain."""
        try:
            from langchain_core.tools import StructuredTool
            return StructuredTool.from_function(
                func=func,
                name=name,
                description=description,
            )
        except ImportError:
            # Fallback: return a simple namespace if langchain not installed
            class SimpleTool:
                pass
            tool = SimpleTool()
            tool.name = name  # type: ignore[attr-defined]
            tool.description = description  # type: ignore[attr-defined]
            tool.func = func  # type: ignore[attr-defined]
            return tool
