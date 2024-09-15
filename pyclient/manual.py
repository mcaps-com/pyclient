import os
from dotenv import load_dotenv
from solana.rpc.api import Client, Keypair
from util import get_token_balance_from_pubkey
from util import get_coin_data, confirm_txn, get_associated_token_account
import pumptx
import time
import requests
from dotenv import load_dotenv
import account_helpers
from check_balance import get_balance
import logging
logger = logging.getLogger(__name__)

load_dotenv()
RPC_HOST = os.getenv("RPC_HOST")
pkey = os.getenv('PRIVKEY')
sol_client = Client(RPC_HOST)
keypair = account_helpers.wallet_keypair(pkey)
pubkey = keypair.pubkey()
import requests

def get_token_info(token):
    url = f"https://mcaps.com/api/v0/pump/poolinfo/{token}"
    result = requests.get(url)
    data = result.json()
    return data

def example_buy():


    token = "3wBSxcAXjtK4gEvobciYZPyMFsz5rn4tdWPrL9DBpump"
    bc = "HwEH8X8ow2GF8TC6vxh7pt1xL8rHTNvxgVmqntJUWP2i"
    abc = "7PiFhJu61j4ZtE9sNrE1XxtVvhq5KWMSAiYQF2d9fqe"


    # RPC_HOST = os.getenv("RPC_HOST")
    #[tokenamnt, v] = get_token_balance_from_pubkey(rpc, walletpub, tokenca)
    # #logger.info(f'token_balance {tokenamnt}')
    logger.info(f"pubkey {pubkey}")
    solbal = sol_client.get_balance(pubkey)
    sb = solbal.value/10**9
    print(f'SOL balalance {sb}')

    # tokenbal = get_token_balance_from_pubkey(sol_client, pubkey, token)
    # logger.info(f"token balance {tokenbal}")

    token_amnt = 1000
    price = 0.0001
    pumptx.buy_assist(sol_client, keypair, token, bc, abc, False, token_amnt, price)

    # token_amnt = 1_000
    # pumptx.sell_assist(sol_client, keypair, token, bc, abc, token_amnt, False)

    # if sb > 0.01:
    #     #buy(rpc, payer, tokenca, sol_in=0.001)
    #     pumptx.buy_calc(rpc, wallet, )
    # else:
    #     print('not enough balance')

    #sell(rpc, payer, tokenca, tokenamnt)

    # balance of token
    # sell



def sell():

    #token = "BSdGR2HpQBLf9S5bZsKMCyQFPS8S7Z8zPJZZrYLRpump"
    token = "3wBSxcAXjtK4gEvobciYZPyMFsz5rn4tdWPrL9DBpump"
    bc = "HwEH8X8ow2GF8TC6vxh7pt1xL8rHTNvxgVmqntJUWP2i"
    abc = "7PiFhJu61j4ZtE9sNrE1XxtVvhq5KWMSAiYQF2d9fqe"
    # info = get_token_info(token)
    # print("token info ", info)
    # bc = info["bondingcurve"]
    # abc = info["ascbondingcurve"]

    # RPC_HOST = os.getenv("RPC_HOST")
    #[tokenamnt, v] = get_token_balance_from_pubkey(rpc, walletpub, tokenca)
    # #logger.info(f'token_balance {tokenamnt}')
    print(f"pubkey {pubkey}")
    solbal = sol_client.get_balance(pubkey)
    sb = solbal.value/10**9
    logger.info(f'solbal {sb}')

    #wpubkey = "C1pc11aUxegHUVzEpaSiUm56z9sHZk9gcjawyoaRwmuN"

    #tokenbal = get_balance(RPC_HOST, pubkey, token)
    tokenbal = get_token_balance_from_pubkey(sol_client, pubkey, token)
    print(f"token balance {tokenbal}")
    if tokenbal > 0:
        token_amnt = tokenbal
        pumptx.sell_assist(sol_client, keypair, token, bc, abc, token_amnt, False)
        token_amnt = 1000
        #price = 0.0001
        #pumptx.buy_assist(sol_client, keypair, token, bc, abc, False, token_amnt, price)


    # if sb > 0.01:
    #     #buy(rpc, payer, tokenca, sol_in=0.001)
    #     pumptx.buy_calc(rpc, wallet, )
    # else:
    #     print('not enough balance')


if __name__ == "__main__":
    #example_buy()
    sell()
