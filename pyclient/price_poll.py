import asyncio
import websockets
import requests
import time
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#baseURL = 'http://www.mcaps.com/api/v0'
baseURL = 'https://mcaps.com/api/v0'


def get_price(token):
    url = f"{baseURL}/pump/lastprice/{token}"
    print('url ', url)
    try:
        start_time = time.time()
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('elapsed_time ', elapsed_time)
        response.raise_for_status()  # Raise an exception for HTTP errors
        responseData = response.json()
        #print(responseData['price_sol'])
        pd = round(responseData['price_usd'],9)
        print('usd price', pd)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error! Status: {http_err.response.status_code}")
    except Exception as err:
        print(f"Error: {err}")

def get_history(token):
    url = f"{baseURL}/pump/history/{token}"
    print('url ', url)
    try:
        start_time = time.time()
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('elapsed_time ', elapsed_time)
        response.raise_for_status()  # Raise an exception for HTTP errors
        responseData = response.json()
        print(responseData)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error! Status: {http_err.response.status_code}")
    except Exception as err:
        print(f"Error: {err}")

def get_ohlc(token):
    url = f"{baseURL}/pump/ohlc/{token}"
    print('url ', url)
    try:
        start_time = time.time()
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('elapsed_time ', elapsed_time)
        response.raise_for_status()  # Raise an exception for HTTP errors
        responseData = response.json()
        print(responseData)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error! Status: {http_err.response.status_code}")
    except Exception as err:
        print(f"Error: {err}")

def poll():
    # Example usage
    #while True:
    #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
    #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
    #get_price('CwkB9Esd2vv3oTEVWNUfcp74tkYpEbdifiRzDfgTpump')
    #get_history('CwkB9Esd2vv3oTEVWNUfcp74tkYpEbdifiRzDfgTpump')
    get_ohlc('CwkB9Esd2vv3oTEVWNUfcp74tkYpEbdifiRzDfgTpump')
    #time.sleep(3.0)


poll()
