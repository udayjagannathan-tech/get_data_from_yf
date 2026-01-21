import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Normed 5Y Monthly Returns Comparison")

# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    ticker1 = st.text_input("Ticker 1", value="AAPL")
with col2:
    ticker2 = st.text_input("Ticker 2", value="MSFT")

if st.button("Run analysis"):
    tickers = [ticker1.strip().upper(), ticker2.strip().upper()]

    # --- Download 5-year monthly data ---
    data = yf.download(
        tickers=tickers,
        period="5y",          # last 5 years
        interval="1mo",       # monthly data
        auto_adjust=True,
        progress=False
    )  # MultiIndex columns if multiple tickers[web:11]

    # Handle single vs multiple ticker column structure
    if isinstance(data.columns, pd.MultiIndex):
        px = data["Close"].copy()
    else:
        px = data[["Close"]].copy()
        px.columns = tickers  # name the single column

    # Drop rows with all NaNs
    px = px.dropna(how="all")

    # --- Normed returns (index starting at 1) ---
    normed = px.div(px.iloc[0])  # divide each row by first row values[web:9]

    st.subheader("Normed price series (start = 1.0)")
    st.dataframe(normed.tail())

    # --- Plot both tickers on same chart ---
    st.subheader("Normed 5Y Monthly Performance")
    st.line_chart(normed)  # each column is a separate line, index on x-axis[web:13]
