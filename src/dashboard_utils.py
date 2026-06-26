from __future__ import annotations

import random
import time
from functools import lru_cache

import pandas as pd
import requests
import yfinance as yf


def parse_tickers(raw_ticker: str):
    """Split and normalize ticker input into a list of uppercase symbols."""
    return [ticker.strip().upper() for ticker in raw_ticker.split(",") if ticker.strip()]


def _normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if cleaned.startswith("^") or "." in cleaned or ":" in cleaned:
        return cleaned
    return cleaned


def _fetch_history_from_yahoo_chart(symbol: str, interval: str = "1d"):
    """Fetch OHLC history from Yahoo's public chart endpoint with browser-like headers."""
    try:
        range_value = "1d" if interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m"} else "1mo"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{_normalize_symbol(symbol)}?interval={interval}&range={range_value}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return {"error": f"Unable to load free market data: {exc}", "history": None}

    result = payload.get("chart", {}).get("result", [])
    if not result:
        return {"error": payload.get("chart", {}).get("error", {}).get("description", "No data found for that symbol."), "history": None}

    chart = result[0]
    timestamps = chart.get("timestamp", [])
    quote = (chart.get("indicators", {}).get("quote", [{}])[0])
    if not timestamps or not quote:
        return {"error": "No data found for that symbol.", "history": None}

    rows = []
    for ts, open_price, high, low, close, volume in zip(
        timestamps,
        quote.get("open", []),
        quote.get("high", []),
        quote.get("low", []),
        quote.get("close", []),
        quote.get("volume", []),
    ):
        rows.append(
            {
                "Date": pd.to_datetime(ts, unit="s"),
                "Open": float(open_price) if open_price is not None else None,
                "High": float(high) if high is not None else None,
                "Low": float(low) if low is not None else None,
                "Close": float(close) if close is not None else None,
                "Volume": int(volume) if volume is not None else None,
            }
        )

    if not rows:
        return {"error": "No data found for that symbol.", "history": None}

    data = pd.DataFrame(rows).dropna(subset=["Close"]).sort_values("Date")
    data = data.set_index("Date")
    data.index.name = "Date"
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    return {"history": data, "meta": chart.get("meta", {})}


def _fetch_history_with_retry(symbol: str, interval: str = "1m"):
    """Fallback to Yahoo Finance if the free provider is unavailable."""
    for attempt in range(2):
        try:
            data = yf.Ticker(symbol).history(period="1d", interval=interval)
            if data.empty:
                return {"error": "No data found. Market might be closed.", "history": None}
            data["SMA_5"] = data["Close"].rolling(window=5).mean()
            return {"history": data}
        except yf.exceptions.YFRateLimitError as exc:
            if attempt == 1:
                return {"error": "Rate limit reached. Please wait a moment and try again.", "history": None, "details": str(exc)}
            time.sleep(1.5 + random.uniform(0, 0.3))
        except Exception as exc:
            return {"error": f"Failed to fetch data: {exc}", "history": None}

    return {"error": "Unable to load data right now.", "history": None}


@lru_cache(maxsize=256)
def get_company_profile(symbol: str):
    """Try to fetch a lightweight company profile for the selected ticker."""
    try:
        info = yf.Ticker(symbol).info or {}
        return {
            "description": info.get("longBusinessSummary") or info.get("industry") or "Company insights are currently unavailable.",
            "logo_url": info.get("logo_url") or info.get("image") or None,
            "industry": info.get("industry") or "Technology",
            "website": info.get("website") or None,
            "country": info.get("country") or None,
        }
    except Exception:
        return {
            "description": "Company details are not available right now.",
            "logo_url": None,
            "industry": "Market",
            "website": None,
            "country": None,
        }


@lru_cache(maxsize=256)
def get_stock_summary(symbol: str, interval: str = "1m"):
    """Return a compact summary for a ticker using a free history source first."""
    history_result = _fetch_history_from_yahoo_chart(symbol, interval)
    if "error" not in history_result and history_result.get("history") is not None:
        data = history_result["history"].copy()
        meta = history_result.get("meta", {})
        latest_price = float(data["Close"].iloc[-1])
        open_price = float(data["Open"].iloc[0])
        change = ((latest_price - open_price) / open_price * 100) if open_price else 0.0
        company_profile = get_company_profile(symbol)
        return {
            "symbol": symbol.upper(),
            "name": meta.get("longName", symbol.upper()),
            "price": latest_price,
            "open": open_price,
            "change_percent": round(change, 2),
            "volume": int(data["Volume"].iloc[-1]) if "Volume" in data.columns else None,
            "avg_volume": None,
            "summary": f"Live free market data from Yahoo's public chart endpoint. {meta.get('exchangeName', 'Market')} • {meta.get('currency', 'USD')}.",
            "change": change,
            "history": data,
            "profile": company_profile,
            "error": None,
        }

    fallback_result = _fetch_history_with_retry(symbol, interval)
    if "error" in fallback_result:
        return {
            "symbol": symbol.upper(),
            "name": symbol.upper(),
            "price": None,
            "change_percent": None,
            "volume": None,
            "avg_volume": None,
            "summary": None,
            "change": None,
            "history": None,
            "error": fallback_result["error"],
        }

    data = fallback_result["history"].copy()
    latest_price = float(data["Close"].iloc[-1])
    open_price = float(data["Open"].iloc[0])
    change = ((latest_price - open_price) / open_price * 100) if open_price else 0.0

    info = {}
    try:
        info = yf.Ticker(symbol).info or {}
    except Exception:
        info = {}

    company_profile = get_company_profile(symbol)
    return {
        "symbol": symbol.upper(),
        "name": info.get("longName", symbol.upper()),
        "price": latest_price,
        "open": open_price,
        "change_percent": round(change, 2),
        "volume": info.get("volume", None),
        "avg_volume": info.get("averageVolume", None),
        "summary": info.get("longBusinessSummary", "No company summary available yet."),
        "change": change,
        "history": data,
        "profile": company_profile,
        "error": None,
    }
