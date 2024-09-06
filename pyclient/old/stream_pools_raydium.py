import asyncio
import websockets
import requests
import time
import traceback
import json
from log_config import get_logger
logger = get_logger("pools")

# Configure logging

async def pools_feed():
    uri = "wss://stream.mcaps.com/ws/raydium/pools"
    logger.info(f'connect {uri}')
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            while True:
                msg = await websocket.recv()
                poolinfo = json.loads(msg)                
                logger.info(f"new pool: {poolinfo}")

    except Exception as e:
        logger.error(f"Failed to connect or an error occurred: {e}")
        logger.error(traceback.format_exc())


def stream():
    asyncio.run(pools_feed())

stream()
