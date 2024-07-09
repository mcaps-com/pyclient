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
