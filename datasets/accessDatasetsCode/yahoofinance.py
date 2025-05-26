import yfinance as yf
import pandas as pd
import requests


def maxSPY():
    pd.set_option('display.max_columns', None)
    # Get S&P 500 data since 2000 and print ALL of it
    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start="2000-01-01", period="max")

    # Format exactly like your original broken code expected
    df_final = pd.DataFrame({
        'date': df.index,
        'open': df['Open'],
        'high': df['High'],
        'low': df['Low'],
        'close': df['Close'],
        'volume': df['Volume']
    })

    # Print ALL the data
    return df_final
