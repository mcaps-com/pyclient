import asyncio
import websockets
import requests
import time

import traceback
import json
import toml
import pumptx
from solana.rpc.api import Client, Keypair
from log_config import get_logger
logger = get_logger("bot")


async def pools_feed():
    with open("settings.toml", "r") as file:
            config = toml.load(file)

    RPC_HOST = config["NODE"]["RPC_HOST"]
    logger.info(RPC_HOST)
    global rpc, wallet, positions
    positions = {}
    rpc = Client(RPC_HOST)

    uri = "wss://stream.mcaps.com/ws/pools"
    logger.info(f"connect {uri}")
    
    pkey = config["WALLET"]["PKEY"]
    wallet = Keypair.from_base58_string(pkey)
    walletpub = wallet.pubkey()
    logger.info(f"walletpub {walletpub}")

    solbal = rpc.get_balance(walletpub)
    sb = solbal.value/10**9
    logger.info(f"solbal {sb}")

    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            while True:
                msg = await websocket.recv()
                poolinfo = json.loads(msg)["pool"]
                token, bc, abc = poolinfo["token"], poolinfo["bondingcurve"], poolinfo["ascbondingcurve"]
                logger.info(f"new pool: \ntoken {token} \nbc {bc} \nabc {abc}")
                time.sleep(10.0)
                #TODO amount here   
                try:
                    # Since buy_assist is synchronous, use run_in_executor to run it in a thread pool
                    await asyncio.get_running_loop().run_in_executor(
                        None, pumptx.buy_assist, rpc, wallet, token, bc, abc
                    )
                except Exception as e:
                    logger.error(f"Error in buy_assist: {e}")
                    logger.error(traceback.format_exc())

    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
        logger.error(traceback.format_exc())


def stream():
    asyncio.run(pools_feed())

stream()
