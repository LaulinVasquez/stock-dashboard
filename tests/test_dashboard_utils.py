import unittest
from unittest.mock import patch

from yfinance.exceptions import YFRateLimitError

from dashboard_utils import get_stock_summary, parse_tickers


class ParseTickersTests(unittest.TestCase):
    def test_single_ticker_is_normalized(self):
        self.assertEqual(parse_tickers("msft"), ["MSFT"])

    def test_multiple_tickers_are_split_and_normalized(self):
        self.assertEqual(parse_tickers("msft, aapl, tsla"), ["MSFT", "AAPL", "TSLA"])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(parse_tickers(" ,  "), [])


class FetchHistoryTests(unittest.TestCase):
    @patch("src.dashboard_utils._fetch_history_from_yahoo_chart")
    @patch("src.dashboard_utils._fetch_history_with_retry")
    def test_returns_error_result_when_rate_limited(self, retry_fetch, yahoo_fetch):
        yahoo_fetch.return_value = {"error": "Unable to load free market data", "history": None}
        retry_fetch.return_value = {"error": "Rate limit reached. Please wait a moment and try again.", "history": None}

        result = get_stock_summary("MSFT", "1m")

        self.assertIn("error", result)
        self.assertIsNone(result["history"])
        self.assertIn("Rate limit", result["error"])


if __name__ == "__main__":
    unittest.main()
