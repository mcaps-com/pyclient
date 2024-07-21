import asyncio
import websockets
import requests
import time
import logging
import traceback
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

baseURL = 'https://mcaps.com/api/v0'

def plot(df, token):
    # Convert unix_time_utc to datetime and then to matplotlib date format
    df['Date'] = pd.to_datetime(df['unix_time_utc'])
    df['Date'] = df['Date'].apply(mdates.date2num)

    # Create a list of tuples with date, open, high, low, close values
    ohlc = [tuple(x) for x in df[['Date', 'open', 'high', 'low', 'close']].values]

    # Create a figure and an axis
    fig, ax = plt.subplots()

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc, width=0.00001, colorup='green', colordown='red')

    # Format the x-axis to show dates
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    # Rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    # Add grid
    ax.grid(True)

    # Add titles and labels
    plt.title(f'Chart {token}')
    plt.xlabel('Date')
    plt.ylabel('Price')

    # Show the plot
    plt.show()

def get_ohlc(token):
    url = f"{baseURL}/pump/ohlc/{token}"
    print('url ', url)
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()        

        df = pd.DataFrame(data)
        plot(df, token)
        

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error! Status: {http_err.response.status_code}")
    except Exception as err:
        print(f"Error: {err}")

def poll():    
    get_ohlc('CwkB9Esd2vv3oTEVWNUfcp74tkYpEbdifiRzDfgTpump')
    

poll()
