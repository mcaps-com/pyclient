import asyncio
import websockets
import requests
import time
import traceback
import json
from log_config import get_logger
logger = get_logger("pools")

# Configure logging

async def socials_feed():
    uri = "wss://stream.mcaps.com/ws/pump/socials"
    logger.info(f'connect {uri}')
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            while True:
                msg = await websocket.recv()
                info = json.loads(msg)
                print(info)
                

    except Exception as e:
        logger.error(f"Failed to connect or an error occurred: {e}")
        logger.error(traceback.format_exc())


asyncio.run(socials_feed())
