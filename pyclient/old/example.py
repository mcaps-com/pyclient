from dotenv import load_dotenv
import os
from solana.rpc.api import Client
import toml
import json
from solana.rpc.api import Client, Keypair
from util import get_token_balance_from_pubkey
from util import get_coin_data, confirm_txn, get_associated_token_account
import pumptx
import time
import requests
from datetime import datetime
import pytz

def example_buy():

    with open("settings.toml", "r") as file:
            config = toml.load(file)

    RPC_HOST = config['NODE']['RPC_HOST']
    print(RPC_HOST)
    global rpc, wallet, positions
    positions = {}
    rpc = Client(RPC_HOST)
    print(rpc)
    pkey = config['WALLET']['PKEY']
    # make_swap()
    wallet = Keypair.from_base58_string(pkey)
    walletpub = wallet.pubkey()
    print(f'walletpub {walletpub}')

    # RPC_HOST = os.getenv("RPC_HOST")
    #[tokenamnt, v] = get_token_balance_from_pubkey(rpc, walletpub, tokenca)
    # #logger.info(f'token_balance {tokenamnt}')

    solbal = rpc.get_balance(walletpub)
    sb = solbal.value/10**9
    print(f'solbal {sb}')

    # tokenca = "Hoghn7ZWdG8iz6GPpQATxw3t1HWfbygVzhwfMWxgpump"
    # bc = "4dDZ6LefZGUyUR1P3Hk2dKrMxh5ZePjbFQyFYuzQztZV"
    # abc = "2bwkeutSuWQgfcG8J6c6TEsfz4cNAmXBUwsc6CY55uBS"

    tokenca = "86DgRcEUM2JiLZ2WXmA3yWunSyj6GvPMfo4zeMhtpump"
    bc = "EpPNc75hvyP8aCjLcuW1ULj8hucCKZjtFSn1aJ5btSZy"
    abc = "DkwYbhZGiMixtNsJhTVrNj4T266nJjA7Z4HsbZqdxFC4"

    # tbal = get_token_balance_from_pubkey(rpc, walletpub, tokenca)
    # print(tbal)

    pumptx.buy_assist(rpc, wallet, tokenca, bc, abc)

    #pumptx.sell_assist(rpc, wallet, tokenca, bc, abc)

    # if sb > 0.01:
    #     #buy(rpc, payer, tokenca, sol_in=0.001)
    #     pumptx.buy_calc(rpc, wallet, )
    # else:
    #     print('not enough balance')

    #sell(rpc, payer, tokenca, tokenamnt)

    #buy(rpc, payer, tokenca, sol_in=0.001)

    # balance of token
    # sell

if __name__ == "__main__":
    example_buy()
