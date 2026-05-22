"""Tests for the LangChain integration toolkit."""

from unittest.mock import MagicMock, patch

from vectrade.integrations import VecTradeToolkit


class TestVecTradeToolkit:
    @patch("vectrade.integrations.VecTrade")
    def test_init_creates_client(self, mock_client_cls) -> None:
        VecTradeToolkit(api_key="vq_test_key123456789")
        mock_client_cls.assert_called_once_with(api_key="vq_test_key123456789", sandbox=False)

    @patch("vectrade.integrations.VecTrade")
    def test_init_sandbox(self, mock_client_cls) -> None:
        VecTradeToolkit(sandbox=True)
        mock_client_cls.assert_called_once_with(api_key=None, sandbox=True)

    @patch("vectrade.integrations.VecTrade")
    def test_get_tools_returns_all(self, mock_client_cls) -> None:
        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        tools = toolkit.get_tools()
        assert len(tools) == 6
        names = [t.name for t in tools]
        assert "vectrade_get_quote" in names
        assert "vectrade_get_fundamentals" in names
        assert "vectrade_get_technicals" in names
        assert "vectrade_get_news" in names
        assert "vectrade_ai_analyze" in names
        assert "vectrade_screen_stocks" in names

    @patch("vectrade.integrations.VecTrade")
    def test_get_tools_with_include_filter(self, mock_client_cls) -> None:
        toolkit = VecTradeToolkit(api_key="vq_test_key123456789", include=["vectrade_get_quote"])
        tools = toolkit.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "vectrade_get_quote"

    @patch("vectrade.integrations.VecTrade")
    def test_get_quote_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_quote = MagicMock()
        mock_quote.symbol = "AAPL"
        mock_quote.price = 195.0
        mock_quote.change_pct = 1.3
        mock_quote.volume = 50000000
        mock_client.quotes.get.return_value = mock_quote
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._get_quote("aapl")
        assert "AAPL" in result
        assert "$195.00" in result
        mock_client.quotes.get.assert_called_once_with("AAPL")

    @patch("vectrade.integrations.VecTrade")
    def test_get_fundamentals_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_data = MagicMock()
        mock_data.company_name = "Apple Inc."
        mock_data.symbol = "AAPL"
        mock_data.market = "NASDAQ"
        mock_data.market_cap = 3e12
        mock_data.fifty_two_week_high = 305.0
        mock_data.fifty_two_week_low = 193.0
        mock_data.sma50 = 270.0
        mock_data.sma200 = 260.0
        mock_client.fundamentals.get.return_value = mock_data
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._get_fundamentals("AAPL")
        assert "Apple Inc." in result
        assert "NASDAQ" in result

    @patch("vectrade.integrations.VecTrade")
    def test_get_technicals_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_data = MagicMock()
        mock_data.symbol = "AAPL"
        mock_data.technical_score = 72.0
        mock_data.rsi_14 = 58.3
        mock_data.summary = {"overall": "buy"}
        mock_client.technicals.get.return_value = mock_data
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._get_technicals("AAPL")
        assert "72.0" in result
        assert "58.3" in result
        assert "buy" in result

    @patch("vectrade.integrations.VecTrade")
    def test_get_news_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_article = MagicMock()
        mock_article.title = "Apple Hits Record"
        mock_article.source = "Reuters"
        mock_client.news.list.return_value = [mock_article]
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._get_news("AAPL")
        assert "Apple Hits Record" in result
        assert "Reuters" in result

    @patch("vectrade.integrations.VecTrade")
    def test_ai_analyze_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Apple is "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "strong."
        mock_client.ai.stream.return_value = iter([mock_chunk1, mock_chunk2])
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._ai_analyze("Analyze AAPL")
        assert result == "Apple is strong."

    @patch("vectrade.integrations.VecTrade")
    def test_screen_stocks_tool(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.symbol = "AAPL"
        mock_result.company_name = "Apple Inc."
        mock_result.price = 195.0
        mock_result.change_pct = 1.3
        mock_client.screener.run.return_value = iter([mock_result])
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._screen_stocks('{"sector": "Technology"}')
        assert "AAPL" in result
        assert "Apple Inc." in result

    @patch("vectrade.integrations.VecTrade")
    def test_screen_stocks_empty(self, mock_client_cls) -> None:
        mock_client = MagicMock()
        mock_client.screener.run.return_value = iter([])
        mock_client_cls.return_value = mock_client

        toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
        result = toolkit._screen_stocks('{"sector": "Unknown"}')
        assert "No stocks matched" in result

    @patch("vectrade.integrations.VecTrade")
    def test_make_tool_without_langchain(self, mock_client_cls) -> None:
        """When langchain is not installed, falls back to SimpleTool."""
        with patch.dict("sys.modules", {"langchain_core": None, "langchain_core.tools": None}):
            toolkit = VecTradeToolkit(api_key="vq_test_key123456789")
            tool = toolkit._make_tool(name="test", description="A test tool", func=lambda x: x)
            assert tool.name == "test"
            assert tool.description == "A test tool"
            assert tool.func("hello") == "hello"
