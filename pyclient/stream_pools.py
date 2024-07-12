import asyncio
import websockets
import requests
import time
import logging
import traceback


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def pools_feed():
    uri = "wss://stream.mcaps.com/ws/pools"
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
    asyncio.run(pools_feed())

stream()
