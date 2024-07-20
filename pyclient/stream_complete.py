import asyncio
import websockets
import requests
import time
import logging
import traceback
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def price_feed():
    uri = "wss://stream.mcaps.com/ws/price"    
    print('connect ', uri)
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                jmsg = json.loads(message)
                solbc = jmsg['bondingcurve_sol']
                if solbc > 70:
                    print(f"SOL in BC: {solbc} {jmsg['token']}")
                if solbc >= 85.0:
                    print(f"COMPLETE {jmsg['token']}")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logging.error(traceback.format_exc())


def stream():
    asyncio.run(price_feed())

stream()
