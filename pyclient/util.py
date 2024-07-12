from solders.pubkey import Pubkey
from spl.token.instructions import (
    create_associated_token_account,
    get_associated_token_address,
    close_account,
    CloseAccountParams,
)
import json
import time
import base58
import requests
#from config import RPC, PUB_KEY, client
from solana.transaction import Signature


import logging
logger = logging.getLogger('util')

def get_token_balance(rpc, token_account_pubkey):
    response = rpc.get_token_account_balance(token_account_pubkey)
    #print('response ', response)
    dec = int(response.value.decimals)
    amnt = response.value.amount
    v = int(amnt) / 10**dec
    return v


def get_associated_token_account(wallet_address, token_mint_address):
    associated_token_account = get_associated_token_address(
        wallet_address,
        token_mint_address,
    )
    return associated_token_account


def get_token_balance_from_pubkey(rpc, walletpub, tokenca):
    tokenpub = Pubkey.from_string(tokenca)
    # TODO check if no account
    # self.base_token_account = utils.account_helpers.create_account(
    #         self.wallet_secret,
    #         self.wallet_address,
    #         self.pool_keys["program_id"],
    #         self.pool_keys["base_mint"],
    #     )
    try:
        token_account_pubkey = get_associated_token_account(walletpub, tokenpub)
        logger.info(f"Token account public key: {token_account_pubkey}")
        v = get_token_balance(rpc, token_account_pubkey)
        #print(response)
        #amnt, v = response.result['value']['amount'], response.result['value']
        #amnt = int(amnt)
        #v = get_token_balance(rpc, token_account_pubkey)
        return v
    except Exception as e:
        logger.error(f"Error: {e}")



def find_data(data, field):
    if isinstance(data, dict):
        if field in data:
            return data[field]
        else:
            for value in data.values():
                result = find_data(value, field)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_data(item, field)
            if result is not None:
                return result
    return None

def get_coin_data(mint_str):
    url = f"https://client-api-2-74b1891ee9f9.herokuapp.com/coins/{mint_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.pump.fun/",
        "Origin": "https://www.pump.fun",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "If-None-Match": 'W/"43a-tWaCcS4XujSi30IFlxDCJYxkMKg"'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def confirm_txn(rpc, txsig):
    max_retries=10
    retry_interval=3
    retries = 0
    print('confirm ', txsig)
    if isinstance(txsig, str):
        txsig = Signature.from_string(txsig)
    while retries < max_retries:
        try:
            txn_res = rpc.get_transaction(txsig, encoding="json", commitment="confirmed", max_supported_transaction_version=0)
            txn_json = json.loads(txn_res.value.transaction.meta.to_json())
            if txn_json['err'] is None:
                print("Transaction confirmed... try count:", retries+1)
                #TODO token amount, sol amount
                return True
            print("Error: Transaction not confirmed. Retrying...")
            if txn_json['err']:
                print("Transaction failed.")
                return False
        except Exception as e:
            print("Awaiting confirmation... try count:", retries+1)
            retries += 1
            time.sleep(retry_interval)
    print("Max retries reached. Transaction confirmation failed.")
    return None
