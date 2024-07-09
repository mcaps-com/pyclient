import asyncio
import websockets
import requests
import time
import logging
import traceback

# ws errors
# let specificStatusCodeMappings = {
#     '1000': 'Normal Closure',
#     '1001': 'Going Away',
#     '1002': 'Protocol Error',
#     '1003': 'Unsupported Data',
#     '1004': '(For future)',
#     '1005': 'No Status Received',
#     '1006': 'Abnormal Closure',
#     '1007': 'Invalid frame payload data',
#     '1008': 'Policy Violation',
#     '1009': 'Message too big',
#     '1010': 'Missing Extension',
#     '1011': 'Internal Error',
#     '1012': 'Service Restart',
#     '1013': 'Try Again Later',
#     '1014': 'Bad Gateway',
#     '1015': 'TLS Handshake'
# };


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#baseURL = 'http://www.mcaps.com/api/v0'
baseURL = 'http://mcaps.com/api/v0'

#https://pumpportal.fun/api/data/token-info?ca=Da34vU8FEqia19XGBNFHunpRy8yBZAxKqwQsEXd31WPg

def get_price(token):
    url = f"{baseURL}/price/pump/{token}"
    print(url)
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

def poll():
    # Example usage
    while True:
        #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
        #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
        get_price('9EWgLt2g1GNiEvp8gaQirrejwpcJjfzFaM4fEuiXpump')
        time.sleep(3.0)


async def test_time():
    uri = "wss://stream.mcaps.com/ws/time"
    print('connect ', uri)    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")

async def price_feed():
    uri = "wss://stream.mcaps.com/ws/price"
    print('connect ', uri)
    #uri = "ws://mcaps.com/pricefeed"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logging.error(traceback.format_exc())



def stream():
    asyncio.run(price_feed())
    #asyncio.run(test_time())

stream()
#poll()
