import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time




st.title("Stock Market Analysis App")

# Get stock data from Yahoo Finance
def get_stock_data(ticker, interval="1m"):
    
    stock = yf.Ticker(ticker)
    
    # get historical market data
    data = stock.history(period="1d", interval=interval)
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    info = stock.info
    
    if data.empty:
        return{"error": "No data found. Market migh be closed"}
    
    latest_price = data["Close"].iloc[-1]
    open_price = data["Open"].iloc[0]
    change = ((latest_price - open_price) / open_price) * 100
    return {
        "Name": info.get("longName", "N/A"),
        "price": latest_price,
        "open": open_price,
        "change_percent": round(change,2),
        "volume": info.get("averageVolume", "N/A"),
        "avg_volume": info.get("averageVolume"),
        "longBusinessSummary": info.get("longBusinessSummary", "N/A"),
        "change": change,
        "history": data,
    }


# this where graph functionality will be
fig = go.Figure()

ticker = st.text_input("Enter stock ticker", value="MSFT")

# backend data information
for x in get_stock_data(ticker):
    print(f"{x}: {get_stock_data(ticker)[x]}")


interval = st.selectbox(
    "Select interval",
    options=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "1wk", "1mo"],
    index=0
)
if ticker:
    with st.spinner('Loading...'):
        time.sleep(1)        
    result = get_stock_data(ticker, interval)
    
    if "error" in result:
        st.error(result["error"])
    else:
        st.subheader(result["Name"])
        st.write(result["longBusinessSummary"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Open Price", f"{result["price"]:.2f}", f"{result["change_percent"]}%")
        with col2:
            st.metric("volume", f"{result["volume"]:,}", f"Avg: {result["avg_volume"]:,}")
        with col3:
            st.metric("price Change", f"{result["change_percent"]:.2f}%", delta_color="inverse")
            
        status = st.empty()
        if result["change"] > 0:
            status.success("📈 Gainer")
        elif result["change"] < 0:
            status.error("📉 Loser")
        time.sleep(5)    
        status.empty()    
        # Chart 
        fig.add_trace(
            go.Scatter(
                x=result["history"].index,
                y=result["history"]["Close"],
                mode="lines",
                name=ticker,
                line=dict(color="royalblue", width=1),
                hovertemplate="<b>%{x}</b><br>Price: $ %{y:.2f}<extra></extra>")
        )
        fig.add_trace(
            go.Scatter(
                x=result["history"].index,
                y=result["history"]["SMA_5"],
                mode="lines",
                name="5-min SMA",
                line=dict(color="orange", width=2, dash="dash"))
        )
        fig.update_layout(
            title=f"{result['Name']} Price Movement ({interval})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
if result["volume"] and result["avg_volume"]:
    if result["volume"] > result["avg_volume"] * 1.5:
        st.warning("⚠️ Abnormally high trading volume!")       
