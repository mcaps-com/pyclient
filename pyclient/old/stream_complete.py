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
                
                unix_time_utc = jmsg['unix_time_utc']
                
                # Calculate the delta with the current Unix time
                current_unix_time = time.time()
                delta = current_unix_time - unix_time_utc
                
                solbc = jmsg['bondingcurve_sol']
                if solbc > 50:
                    #print(jmsg)
                    #print(f"Unix Time UTC: {unix_time_utc}")
                    #print(f"Delta with current time: {delta} seconds")
                    r = solbc/85.0
                    print(f"%complete {r:.2f} {jmsg['token']}")
                if solbc >= 85.0:
                    print(f"COMPLETE {jmsg['token']}")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logging.error(traceback.format_exc())

async def feed():
    uri = "wss://stream.mcaps.com/ws/poolcomplete"    
    print('connect ', uri)
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                jmsg = json.loads(message)
                
                
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logging.error(traceback.format_exc())


def stream():
    asyncio.run(feed())

stream()
