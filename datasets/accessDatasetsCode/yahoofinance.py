import yfinance as yf
import pandas as pd


def monthly_sp500():
    pd.set_option('display.max_columns', None)

    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start="2003-01-01", end="2024-02-01", interval="1mo")
    df = df.reset_index()

    df['month'] = df['Date'].dt.to_period('M')

    df_final = pd.DataFrame({
        'month': df['month'],
        'close': df['Close']
    })

    return df_final
