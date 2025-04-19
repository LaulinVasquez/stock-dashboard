import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.title("Stock Market Analysis App")

# Get stock data from Yahoo Finance
def get_stock_data(ticker):
    
    stock = yf.Ticker(ticker)
    
    # get historical market data
    data = stock.history(period="1d", interval="1m")
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
        "history": data 
    }


# this where graph functionality will be
fig = go.Figure()




ticker = st.text_input("Enter stock ticker", value="MSFT")

# backend data information
for x in get_stock_data(ticker):
    print(f"{x}: {get_stock_data(ticker)[x]}")

if ticker:
    result = get_stock_data(ticker)
    
    if "error" in result:
        st.error(result["error"])
    else:
        st.subheader(result["Name"])
        st.metric("Curren Price", f"{result["price"]:.2f}", f"{result["change_percent"]}%")
        st.metric("volume", f"{result["volume"]:,}", f"Avg: {result["avg_volume"]:,}")
        fig.add_trace(
            go.Scatter(
                x=result["history"].index,
                y=result["history"]["Close"],
                mode="lines",
                name=ticker,
                line=dict(color="royalblue", width=1),
            )
        )
        fig.update_layout(
            title=f"{result['Name']} Price Movement in the last 30 days",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        
