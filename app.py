import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

st.title("Stock Performance Comparison (Normalized)")

# Input for two tickers
col1, col2 = st.columns(2)
with col1:
    ticker1 = st.text_input("Enter first ticker symbol (e.g., AAPL, RELIANCE.NS):").strip().upper()
with col2:
    ticker2 = st.text_input("Enter second ticker symbol (e.g., MSFT, TCS.NS):").strip().upper()

if st.button("Fetch and Compare"):
    if not ticker1 or not ticker2:
        st.error("Please enter both ticker symbols.")
    elif ticker1 == ticker2:
        st.error("Please enter different ticker symbols.")
    else:
        # Calculate date range: last 5 years monthly
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        tickers = [ticker1, ticker2]
        data = {}
        valid_tickers = []
        
        # Validate and fetch data for each ticker
        for ticker in tickers:
            try:
                temp_data = yf.download(ticker, start=start_date, end=end_date, interval="1mo", progress=False)
                if temp_data.empty:
                    raise ValueError("No data returned")
                # Robust Adj Close extraction [web:11][web:35]
                if 'Adj Close' in temp_data.columns:
                    adj_close = temp_data['Adj Close']
                elif 'Close' in temp_data.columns:
                    adj_close = temp_data['Close']  # Often pre-adjusted in recent yfinance
                else:
                    raise ValueError("'Adj Close' or 'Close' not available (check ticker or yfinance version)")
                data[ticker] = adj_close.dropna()
                valid_tickers.append(ticker)
                st.success(f"✓ Valid data for {ticker}: {len(data[ticker])} months")
            except Exception as e:
                st.error(f"❌ Invalid ticker '{ticker}': {str(e)}. Please check the symbol. [web:18][web:22]")
        
        if len(valid_tickers) == 2:
            # Align data by common index (monthly dates)
            common_index = data[ticker1].index.intersection(data[ticker2].index)
            if len(common_index) < 12:  # At least 1 year
                st.error("Insufficient overlapping monthly data for comparison.")
            else:
                aligned_data = pd.DataFrame({
                    ticker1: data[ticker1].loc[common_index],
                    ticker2: data[ticker2].loc[common_index]
                })
                
                # Normalize: divide by first value *100 for index-like plot [web:17]
                normed_data = (aligned_data / aligned_data.iloc[0]) * 100
                
                # Plot with matplotlib
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(normed_data.index, normed_data[ticker1], label=ticker1, linewidth=2)
                ax.plot(normed_data.index, normed_data[ticker2], label=ticker2, linewidth=2)
                ax.set_title(f"Normalized Adjusted Close (Last 5 Years Monthly): {ticker1} vs {ticker2}", fontsize=16)
                ax.set_ylabel("Normalized Price (Starting at 100)", fontsize=14)
                ax.set_xlabel("Date", fontsize=14)
                ax.legend(fontsize=12)
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # Display 
