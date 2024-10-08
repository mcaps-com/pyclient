#https://github.com/7xck/raydium-executor/blob/ede3a248ad117bdf41ec334d6460c516cd666d50/utils/account_helpers.py#L78

from solders.pubkey import Pubkey as PublicKey
from solana.rpc.types import TokenAccountOpts
from solana.rpc.api import Client
from spl.token.client import Token
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.keypair import Keypair
from typing import Optional
import asyncio
from spl.token.instructions import create_associated_token_account, get_associated_token_address, close_account
import logging

logger = logging.getLogger(__name__)

def wallet_keypair(private_key: str):
    pair = Keypair.from_base58_string(
        private_key
    )
    return pair

async def get_token_account_retry(rpc, owner, tokenca, max_retries=5, delay=0.2):
    tokenpub = Pubkey.from_string(tokenca)
    owner_pubkey = owner.pubkey()
    token_account = None
    token_account_instructions = None

    for attempt in range(max_retries):
        try:
            account_data = await rpc.get_token_accounts_by_owner(owner_pubkey, TokenAccountOpts(tokenpub))
            if len(account_data['result']['value']) > 0:
                token_account = Pubkey.from_string(account_data['result']['value'][0]['pubkey'])
                token_account_instructions = None
                break
            else:
                # Create account
                token_account_instructions = create_associated_token_account(owner_pubkey, owner_pubkey, tokenpub)
                token_account = get_associated_token_address(owner_pubkey, tokenpub)
                break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                raise e

    if token_account is None:
        raise ValueError("Unable to find or create the token account.")

    return token_account, token_account_instructions

def get_token_create(owner, tokenca):
    mint = Pubkey.from_string(tokenca)
    token_account = get_associated_token_address(owner, mint)
    token_account_instructions = create_associated_token_account(owner, owner, mint)
    return token_account, token_account_instructions

def get_token_account(rpc, owner, tokenca):
    mint = Pubkey.from_string(tokenca)
    try:
        #account_data = rpc.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        account_data = rpc.get_token_accounts_by_owner(owner, TokenAccountOpts(mint), commitment='processed')
        token_account = account_data.value[0].pubkey
        token_account_instructions = None
        logger.info(f"account exists {token_account}")
    except Exception as e:
        token_account = get_associated_token_address(owner, mint)
        token_account_instructions = create_associated_token_account(owner, owner, mint)
        logger.info(f"account not exists need to create \ntoken_account_instructions: {token_account_instructions}")
    return token_account, token_account_instructions



def get_token_accountold(client, owner: PublicKey, mint: PublicKey):
    account_data = client.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
    logger.info(f"mint {account_data.value[0].pubkey}")
    return account_data.value[0].pubkey


def set_solana_client(development_url):
    solana_client = Client(development_url, timeout=30)
    return solana_client


def set_source_main_wallet_keypair(source_main_wallet_private_key: str):
    source_main_wallet_keypair = Keypair.from_base58_string(
        source_main_wallet_private_key
    )
    return source_main_wallet_keypair


def set_main_wallet_publickey(main_wallet_address: str):
    main_wallet_public_key = Pubkey.from_string(main_wallet_address)
    return main_wallet_public_key


def set_program_id_publickey(program_id: str):
    program_id_publickey = Pubkey.from_string(program_id)
    return program_id_publickey


def set_token_address_publickey(token_address: str):
    token_address_publickey = Pubkey.from_string(token_address)
    return token_address_publickey


def set_spl_client(
        solana_client: Client,
        token_address_publickey: Pubkey,
        program_id_publickey: Pubkey,
        source_main_wallet_keypair: Keypair,
):
    spl_client = Token(
        conn=solana_client,
        pubkey=token_address_publickey,
        program_id=program_id_publickey,
        payer=source_main_wallet_keypair,
    )
    return spl_client


def get_token_wallet_address_from_main_wallet_address(
        spl_client: Token, main_wallet_address: Pubkey
):
    try:
        token_wallet_address_public_key = (
            spl_client.get_accounts_by_owner(
                owner=main_wallet_address, encoding="base64"
            )
            .value[0]
            .pubkey
        )
        logger.info("Got the token account for the coin")
    except:
        token_wallet_address_public_key = (
            spl_client.create_associated_token_account(
                owner=main_wallet_address,
            )
        )
        logger.error("WARNING: had to create a token account for the coin")
    return token_wallet_address_public_key


def create_account(sol_client, private_key, wallet_address, program_id, mint):
    main_wallet = wallet_address
    source_main_wallet_keypair = set_source_main_wallet_keypair(private_key)
    sender_pubkey = set_main_wallet_publickey(wallet_address)
    program_pubkey = set_program_id_publickey(program_id)
    token_address_pubkey = set_token_address_publickey(mint)

    # set clients
    spl_client = set_spl_client(
        sol_client,
        token_address_pubkey, program_pubkey, source_main_wallet_keypair
    )

    # set and check sender token account
    sender_token_pubkey = (
        get_token_wallet_address_from_main_wallet_address(
            spl_client,
            sender_pubkey
        )
    )

    return sender_token_pubkey
