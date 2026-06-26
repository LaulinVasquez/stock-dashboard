from __future__ import annotations

from html import escape

import streamlit as st
import plotly.graph_objects as go

from src.dashboard_utils import get_stock_summary, parse_tickers


def render_dashboard() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp { background: linear-gradient(135deg, #07111f 0%, #111c33 45%, #172554 100%); }
        .block-container { padding-top: 1.3rem; padding-bottom: 2rem; }
        [data-testid="stMetric"] { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 0.75rem 0.9rem; box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
        .stTextInput > div > div > input, .stSelectbox > div > div > div { border-radius: 12px; }
        .hero-card { background: linear-gradient(135deg, rgba(79,140,255,0.18), rgba(255,255,255,0.06)); border: 1px solid rgba(255,255,255,0.12); border-radius: 20px; padding: 1.2rem 1.25rem; margin-bottom: 1rem; }
        .company-glass-card { background: rgba(8, 16, 32, 0.58); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.18); box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28); border-radius: 20px; padding: 1rem 1.1rem; margin-top: 1.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.title("📈 Stock Market Dashboard")
    st.caption("A polished, free dashboard for tracking a few tickers without depending on Yahoo’s rate-limited API.")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Controls")
        st.radio("Navigate", ["Dashboard", "About me"], key="page_nav")
        input_ticker = st.text_input("Ticker(s)", value="MSFT,AAPL", help="Separate tickers with commas.")
        interval = st.selectbox(
            "Interval",
            options=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "1wk", "1mo"],
            index=0,
        )
        if st.button("Refresh data", use_container_width=True):
            st.session_state.pop("dashboard_cache", None)
        st.caption("Free mode uses Yahoo's public chart endpoint with no API key required.")

    tickers = parse_tickers(input_ticker)

    if not tickers:
        st.info("Enter one or more tickers such as MSFT, AAPL, or NVDA to begin.")
        return

    cache_key = ("|".join(tickers), interval)
    if "dashboard_cache" not in st.session_state:
        st.session_state.dashboard_cache = {}

    cache = st.session_state.dashboard_cache
    if cache_key not in cache:
        cache[cache_key] = {"results": {}}

    results = cache[cache_key]["results"]

    with st.spinner("Loading fresh market data…"):
        for symbol in tickers:
            if symbol not in results:
                results[symbol] = get_stock_summary(symbol, interval)

    fig = go.Figure()
    for symbol in tickers:
        result = results.get(symbol, {})
        if result.get("error") or result.get("history") is None:
            st.warning(f"{symbol}: {result.get('error', 'No data available')}")
            continue
        data = result["history"]
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name=symbol))

    if len(fig.data) > 0:
        fig.update_layout(
            title=f"Price movement for {', '.join(tickers)}",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("The current query did not produce any chartable prices.")

    primary_symbol = tickers[0]
    primary_result = results.get(primary_symbol, {})
    if primary_result.get("error"):
        st.error(primary_result["error"])
        return

    st.subheader(f"{primary_result['name']} · {primary_symbol}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Price", f"${primary_result['price']:.2f}" if primary_result.get("price") is not None else "N/A", delta=f"{primary_result['change_percent']:.2f}%" if primary_result.get("change_percent") is not None else None)
    with col2:
        st.metric("Volume", f"{primary_result['volume']:,}" if primary_result.get("volume") is not None else "N/A", delta="Latest session")
    with col3:
        st.metric("Avg Volume", f"{primary_result['avg_volume']:,}" if primary_result.get("avg_volume") is not None else "N/A", delta="Reference")

    if primary_result.get("change") is not None:
        if primary_result["change"] > 0:
            st.success(f"{primary_result['name']} is trending up today. 📈")
        elif primary_result["change"] < 0:
            st.error(f"{primary_result['name']} is trending down today. 📉")
        else:
            st.info(f"{primary_result['name']} is flat for the current session.")

    profile = primary_result.get("profile", {})
    company_description = profile.get("description") or primary_result.get("summary") or "No summary available yet."
    st.markdown(
        f"""
        <div class="company-glass-card">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:0.7rem; margin-bottom:0.55rem;">
                <h4 style="margin:0; color:#f8fbff;">Company description</h4>
                <span style="padding:0.28rem 0.65rem; border-radius:999px; background:rgba(79,140,255,0.2); border:1px solid rgba(255,255,255,0.16); color:#dceaff; font-size:0.85rem;">{escape(primary_symbol)}</span>
            </div>
            <p style="margin:0; line-height:1.7; color:#f3f7ff;">{escape(company_description)}</p>
            <div style="margin-top:0.8rem; display:flex; flex-wrap:wrap; gap:0.75rem; color:#dce8ff; font-size:0.95rem;">
                {f'<span>Industry: {escape(profile["industry"])}</span>' if profile.get("industry") else ''}
                {f'<span>Website: <a href="{escape(profile["website"], quote=True)}" target="_blank" rel="noopener noreferrer" style="color:#8ec5ff;">{escape(profile["website"])}</a></span>' if profile.get("website") else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Built with care by Laurin Vasquez")


def main() -> None:
    st.set_page_config(page_title="Stock Market Compass", page_icon="📈", layout="wide")
    if st.session_state.get("page_nav") == "About me":
        from src.about_me import show_about_page

        show_about_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
