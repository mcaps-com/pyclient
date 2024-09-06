import json
import time
import os
from solana.rpc.api import Client
import account_helpers as account_helpers
from util import get_token_balance_from_pubkey, get_associated_token_account, get_token_balance
from solders.pubkey import Pubkey
from dotenv import load_dotenv
import requests
load_dotenv()

# Function to create the JSON-RPC payload
def create_payload(wallet_address, token_address):
    return {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"mint": token_address},
            {"encoding": "jsonParsed"},
        ],
    }

# Function to make the RPC request
def make_rpc_request(url, payload):
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response

# Function to extract and print the token balance from the response
def extract_token_balance(response):
    try:
        response_json = response.json()
        if "result" in response_json and response_json["result"]["value"]:
            token_info = response_json["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]
            balance = token_info["uiAmount"]
            return balance
        else:
            return 0  # No token accounts found or empty response indicates balance is 0
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response.")
        print(f"Response text: {response.text}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Main function to execute the process
def get_balance(RPC_HOST, wallet_address, token_address):
    # Create the payload
    payload = create_payload(wallet_address, token_address)

    # Make the RPC request
    response = make_rpc_request(RPC_HOST, payload)

    # Extract and print the token balance
    balance = extract_token_balance(response)
    if balance is not None:
        print(f"Token balance: {balance}")
        return balance

