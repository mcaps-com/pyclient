import asyncio
import websockets
import requests
import time
import logging
import traceback
import json
import toml
import pumptx
from solana.rpc.api import Client, Keypair

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def pools_feed():
    with open("settings.toml", "r") as file:
            config = toml.load(file)

    RPC_HOST = config['NODE']['RPC_HOST']
    print(RPC_HOST)
    global rpc, wallet, positions
    positions = {}
    rpc = Client(RPC_HOST)

    uri = "wss://stream.mcaps.com/ws/pools"
    print('connect ', uri)
    #uri = "ws://mcaps.com/pricefeed"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                msg = await websocket.recv()
                poolinfo = json.loads(msg)['pool']
                token, bc, abc = poolinfo['token'], poolinfo['bondingcurve'], poolinfo['ascbondingcurve']
                print(f"new pool: {token} {bc} {abc}")

                #TODO amount here
                pumptx.buy_assist(rpc, wallet, token, bc, abc)


    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logging.error(traceback.format_exc())


def stream():
    asyncio.run(pools_feed())

stream()
