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
    #uri = "wss://stream.mcaps.com/ws/pools"
    uri = "wss://95.179.251.158/ws/pools"
    logger.info(f'connect {uri}')
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            while True:
                msg = await websocket.recv()
                poolinfo = json.loads(msg)['pool']
                token, bc, abc = poolinfo['token'], poolinfo['bondingcurve'], poolinfo['ascbondingcurve']
                logger.info(f"new pool: {token} {bc} {abc}")

    except Exception as e:
        logger.error(f"Failed to connect or an error occurred: {e}")
        logger.error(traceback.format_exc())


def stream():
    asyncio.run(pools_feed())

stream()
