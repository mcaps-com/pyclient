#jito?
#preflight check


import struct
import time
import json
from solana.rpc.core import RPCException
from solana.transaction import AccountMeta
from spl.token.instructions import create_associated_token_account, get_associated_token_address
from solders.pubkey import Pubkey #type: ignore
from solders.instruction import Instruction #type: ignore
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price #type: ignore
from solders.transaction import VersionedTransaction #type: ignore
from solders.message import MessageV0, to_bytes_versioned #type: ignore
from solana.rpc.types import TokenAccountOpts
from solders.transaction import VersionedTransaction #type: ignore
from solders.transaction import SanitizeError, Transaction, TransactionError
from colored import Fore, Back, Style
import traceback
from solana.rpc.types import TxOpts
import requests
#from utils import get_coin_data, get_token_balance, confirm_txn
from util import get_coin_data, confirm_txn
from base64 import b64decode, b64encode
import traceback
from account_helpers import get_token_account, get_token_create
from log_config import get_logger
from util import get_token_balance_from_pubkey
logger = get_logger(__name__)

GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOC_TOKEN_ACC_PROG = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
PUMP_FUN_ACCOUNT = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
SOL = "So11111111111111111111111111111111111111112"
LAMPORTS_PER_SOL = 1_000_000_000
UNIT_PRICE =  2_500_000
UNIT_BUDGET =  390_000

MAGIC_BUY = 16927863322537952870
MAGIC_SELL = 12502976635542562355

def submit_jito(encoded_tx):
    #url = "https://mainnet.block-engine.jito.wtf"
    url = "https://mainnet.block-engine.jito.wtf/api/v1/transactions"
    #TODO

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [
            encoded_tx,
            {
                "encoding": "base64",
                "skipPreflight": True,
                "preflightCommitment": "confirmed"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        logger.info(f"Response JSON: {response.json()}")
        sig = response.json()['result']
        logger.info(f"sig {sig}")

    except requests.exceptions.RequestException as e:
        logger.error("Request failed:", e)
        logger.error("Response status code:", response.status_code if response else "No response")
        logger.error("Response content:", response.content if response else "No content")

def get_poolkeys_buy(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER):
    keys = [
            AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
            AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
            AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
        ]
    return keys

def get_poolkeys_sell(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER):
    keys = [
            AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
            AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True), # Writable
            AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True), # Writable
            AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True), # Writable
            AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True), # Writable
            AccountMeta(pubkey=USER, is_signer=True, is_writable=True), # Writable Signer Fee Payer
            AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=ASSOC_TOKEN_ACC_PROG, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
        ]
    return keys


def sell_instructions(mint, bc, abc, token_account, owner, token_amount, min_sol_output_slip):
    """ make sell tx from parameters """
    MINT = Pubkey.from_string(mint)
    BONDING_CURVE = Pubkey.from_string(bc)
    ASSOCIATED_BONDING_CURVE = Pubkey.from_string(abc)
    ASSOCIATED_USER = token_account
    USER = owner
    poolkeys = get_poolkeys_sell(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER)
    integers = [
        MAGIC_SELL,
        token_amount,
        min_sol_output_slip
    ]
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)
    swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, poolkeys)

    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    instructions.append(swap_instruction)
    return instructions

def make_sell_tx(rpc, mint, bc, abc, token_account, owner, payer_keypair, token_amount, min_sol_output_slip):
    instructions = sell_instructions(mint, bc, abc, token_account, owner, token_amount, min_sol_output_slip)
    hash = rpc.get_latest_blockhash().value.blockhash
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],
        hash,
    )
    tx = VersionedTransaction(compiled_message, [payer_keypair])
    serialized_tx = bytes(tx)
    return serialized_tx

def make_buy_instructions(mint, bc, abc, token_account, owner, token_out, max_sol_cost, token_account_instructions):
    MINT = Pubkey.from_string(mint)
    BONDING_CURVE = Pubkey.from_string(bc)
    ASSOCIATED_BONDING_CURVE = Pubkey.from_string(abc)
    ASSOCIATED_USER = token_account
    USER = owner

    poolkeys = get_poolkeys_buy(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER)
    integers = [
        MAGIC_BUY,
        token_out,
        max_sol_cost
    ]
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)
    swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, poolkeys)

    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    if token_account_instructions:
        instructions.append(token_account_instructions)
    instructions.append(swap_instruction)
    return instructions


def make_tx_buy(rpc, mint, bc, abc, token_account, owner, payer_keypair, token_out, max_sol_cost, token_account_instructions):
    """ make buy tx from parameters """
    instructions = make_buy_instructions(mint, bc, abc, token_account, owner, token_out, max_sol_cost, token_account_instructions)
    address_lookup = []
    hash = rpc.get_latest_blockhash().value.blockhash
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        address_lookup,
        hash,
    )
    tx = VersionedTransaction(compiled_message, [payer_keypair])
    return tx

def calc_slip():
    #TODO
    # Calculate max_sol_cost and amount
    #sol_in_with_slippage = sol_in * (1 + slippage_decimal)
    #sol_in_with_slippage = sol_in * 5
    #sol_in_with_slippage =100_000
    #max_sol_cost = int(sol_in_with_slippage * LAMPORTS_PER_SOL)
    max_sol_cost = 100_000

# def buy_calc(rpc, wallet, tokenca, bc, abc, price, token_amnt):
#     #TODO token decimals

#     #TODO as intial

#     token_decimals = 6
#     sol_decimals = 9
#     #sol_amnt = 0.005

#     logger.info(f'price {price}')
#     logger.info(f'token_amnt {token_amnt}')
#     #logger.info(f'sol_amnt {sol_amnt}')

#     #3x from initial price
#     base_sol_amnt = token_amnt * price
#     slip_sol_amnt = base_sol_amnt * 3.0

#     logger.info(f'max_sol_cost {base_sol_amnt}')
#     logger.info(f'max_sol_cost {slip_sol_amnt}')


#     token_out = int(token_amnt * 10**token_decimals)
#     max_sol_cost = int(slip_sol_amnt * 10**sol_decimals)
#     logger.info(f'token_out {token_out}')
#     logger.info(f'max_sol_cost {max_sol_cost}')

#     result = buy(rpc, wallet, tokenca, bc, abc, token_out, max_sol_cost)
#     return [result, token_amnt]


def buy_assist(rpc, wallet, tokenca, bc, abc, create_ata, token_amnt, price):

    #logger.info(f'walletpub {wallet.pubkey()}')

    logger.warn(f'!!BUY. token: {tokenca} token_amnt {token_amnt} price {price}')
    logger.info(f"bc {bc} abc {abc}")    

    token_decimals = 6
    sol_decimals = 9
    SLIP = 0.05
    slippage = SLIP * price
    max_price_with_slippage = price + slippage
    logger.info(f"Price with slippage: {max_price_with_slippage}")

    # Calculate the maximum SOL cost including slippage
    max_sol_cost = int(token_amnt * max_price_with_slippage * 10**sol_decimals)
    token_out = int(token_amnt * 10**token_decimals)

    logger.info(f"token_out {token_out} \t max_sol_cost {max_sol_cost}")

    result = buy(rpc, wallet, tokenca, bc, abc, token_out, max_sol_cost, create_ata)
    logger.info(f"trade result {result}")
    return result

def sell_assist(rpc, payer_keypair, tokenca, bc, abc, token_amnt, check_balance, max_retries=3, retry_delay=2):
    #TODO skip for speedup
    if check_balance:
        tokenbal = get_token_balance_from_pubkey(rpc, payer_keypair.pubkey(), tokenca)
        logger.info(f"token balance {tokenbal}")
        if tokenbal == 0:
            logger.error("nothing to sell")
            return

    #TODO calc input
    #TODO calc slippage
    token_decimals = 6
    sol_decimals = 9

    #TODO
    #for 10k tokens
    #target_price = 0.00000003
    #sol_amnt = target_price * 10_000

    token_amount_dec = int(token_amnt * 10**token_decimals)
    #min_sol_output_slip = int(sol_amnt * 10**sol_decimals)
    min_sol_output_slip = 0

    owner = payer_keypair.pubkey()
    token_account, token_instructions = get_token_account(rpc, owner, tokenca)
    logger.info("rpc, tokenca, bc, abc, token_account, owner, payer_keypair, token_amnt, min_sol_output_slip")
    info = [rpc, tokenca, bc, abc, token_account, owner, payer_keypair, token_amount_dec, min_sol_output_slip]
    logger.info(f"{info}")
    serialized_tx = make_sell_tx(rpc, tokenca, bc, abc, token_account, owner, payer_keypair, token_amount_dec, min_sol_output_slip)
    logger.info(f"SELL AMOUNT {token_amount_dec}")
    logger.info(f"serialized_tx {serialized_tx}")

    doSim = False
    if doSim:
        #TODO
        pass

    attempt = 0
    txsig = None

    while attempt < max_retries:
        attempt += 1
        try:
            logger.info('send tx')
            response = rpc.send_raw_transaction(serialized_tx)
            txsig = response.value
            logger.info(f"response {response}")
            logger.info(f"txsig {txsig}")
            break
        except RPCException as e:
            logger.error(f"error with tx {str(e)}")
            logs = json.loads(e.args[0].data.to_json())['logs']
            incorrect_prog = "Error processing Instruction 2: incorrect program id for instruction"
            overflow = "panicked at programs/pump/src/lib.rs:615:48:\nattempt to subtract with overflow"
            missing_account = "Error Message: The program expected this account to be already initialized"

            #Instruction #3 Failed - Provided owner is not allowed"

            if any(overflow in log for log in logs):
                logger.error('overflow')
                logger.error(logs)
            elif any(incorrect_prog in log for log in logs):
                logger.error('incorrect program')
            elif any(missing_account in log for log in logs):
                logger.error(f"selling error. don't have balance {str(e)}")
            else:
                logger.error(f"selling error. unknown  {str(e)}")

            if attempt < max_retries:
                logger.info(f"Retrying... ({attempt}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting.")
                return {'success': False, 'amount': 0}

    if txsig is None:
        logger.error("no txsig")
        return {'success': False, 'amount': 0}

    try:
        logger.info("try confirm")
        confirm = confirm_txn(rpc, txsig)
        if confirm["success"]:
            logger.warn(f'Successfully sold {tokenca} \n{str(txsig)}')
            return {'success': True, 'amount': 0}
        else:
            logger.info(f"{Fore.red}[!] not confirmed {confirm["error"]}")
            return {'success': False, 'amount': 0}
    except Exception as e:
        logger.error(f"error confirm {str(e)}")
        return {'success': False, 'amount': 0}


def buy(rpc, payer_keypair, tokenca, bc, abc, token_out, max_sol_cost, create_ata):
    try:
        logger.info(f'try buy....\ntoken {tokenca}\nBC: {bc}\nABC: {abc}')

        #not enough balance leads to this
        #pumptx - ERROR - uncategorized error SendTransactionPreflightFailureMessage { message: "Transaction simulation failed: Error processing Instruction 2: custom program error: 0x1"

        owner = payer_keypair.pubkey()
        logger.info(f"owner {owner}")
        #logger.info(f'payer_keypair {payer_keypair}')

        #need to wait for token creation?

        #TODO flag for skip check if available
        if create_ata:
            token_account, token_instructions = get_token_create(owner, tokenca)
        else:
            token_account, token_instructions = get_token_account(rpc, owner, tokenca)

        logger.info(f"token_account {token_account}")
        try:
            logger.info("tokenca, bc, abc, token_account, owner, payer_keypair, max_sol_cost")
            info = [tokenca, bc, abc, token_account, owner, payer_keypair, max_sol_cost]
            logger.info(f"trigger buy: {info}")
            buytx = make_tx_buy(rpc, tokenca, bc, abc, token_account, owner, payer_keypair, token_out, max_sol_cost, token_instructions)
        except Exception as e:
            logger.error(f'error make buy tx {e}')

        doSim = False

        if doSim:
            simulation_result = rpc.simulate_transaction(buytx, sig_verify=True)
            js = json.loads(simulation_result.to_json())
            verr = js['result']['value']['err']

            # Check the simulation result
            # TODO =
            if verr:
                if 'InstructionError' in verr.keys():
                    elogs= js['result']['value']['logs']

                    logger.error(f"Simulation failed: {js['result']['value']['err']}")
                    #'Transfer: insufficient lamports 2492079, need 2851242'
                    if any('insufficient lamports' in log for log in elogs):
                        logger.error("not enough SOL")
                        return {'success': False, 'amount': 0}
                    elif any('incorrect program id' in log for log in elogs):
                        logger.error('issue with bc')

                    return {'success': False, 'amount': 0}
            else:
                logger.info("Simulation succeeded")

        txsig = None

        try:
            logger.info("send tx")
            serialized_tx = bytes(buytx)
            #response = rpc.send_raw_transaction(serialized_tx)
            response = rpc.send_raw_transaction(serialized_tx, opts=TxOpts(skip_preflight=True))

            txsig = response.value
            logger.info(f"response {response}")
            logger.info(f"txsig {txsig}")
        except RPCException as e:
            logger.error(f"error with tx {str(e)}")
            emsg = e.args[0].message
            #Instruction #3 Failed - Provided owner is not allowed"

            if '0x1772' in emsg:
                #'Transaction simulation failed: Error processing Instruction 3: custom program error: 0x1772'
                #slippage?
                logger.error(f"??? {emsg}")
            elif 'incorrect program id' in emsg:
                #sourceAccount hasn't been created on mainnet yet.
                logger.error(f"wrong program. emsg: {emsg}")
                #"Transaction simulation failed: Error processing Instruction 2: incorrect program id for instruction"
            elif "custom program error: 0xbc4" in emsg:
                logger.error(f"??: {emsg}")
                #error  SendTransactionPreflightFailureMessage { message: "Transaction simulation failed: Error processing Instruction 2: custom program error: 0xbc4", data: RpcSimulateTransactionResult(RpcSimulateTransactionResult { err: Some(InstructionError(2, Custom(3012))), logs: Some(["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke [1]", "Program log: Instruction: Sell", "Program log: AnchorError caused by account: associated_user. Error Code: AccountNotInitialized. Error Number: 3012. Error Message: The program expected this account to be already initialized.", "Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P consumed 9237 of 389700 compute units", "Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P failed: custom program error: 0xbc4"]), accounts: None, units_consumed: Some(9537), return_data: None, inner_instructions: None }) }
            elif "#custom program error: 0x1" in emsg:
                logger.error("error related to ATA?")
            else:
                logs = json.loads(e.args[0].data.to_json())['logs']
                incorrect_prog = 'Error processing Instruction 2: incorrect program id for instruction'
                overflow = 'panicked at programs/pump/src/lib.rs:615:48:\nattempt to subtract with overflow'
                if any(overflow in log for log in logs):
                    logger.error('overflow')
                    logger.error(logs)
                elif any(incorrect_prog in log for log in logs):
                    logger.error('incorrect program')
                else:

                    logger.error(f'uncategorized error {e}')
            return {'success': False, 'amount': 0}

        if txsig != None:
            tries = 0
            while tries < 10:
                #Program Error: "Instruction #4 Failed - slippage: Too much SOL required to buy the given amount of tokens"
                try:
                    logger.info("try confirm")
                    # Confirm transaction
                    confirm = confirm_txn(rpc, txsig)
                    #TODO get tx result
                    if confirm["success"] == True:
                        logger.warn(f'Succesfully bought {tokenca} \n{str(txsig)}')
                        #TODO return position size
                        return {'success': True, 'amount': 0}
                    else:
                        logger.info(f"{Fore.red}[!] not confirmed {confirm["error"]}")
                        #return {'success': False, 'amount': 0}
                    #return confirm
                    tries+=1
                    return {'success': False, 'amount': 0}
                except Exception as e:
                    logger.error(f'exception trying confirm {e}')
        else:
            return {'success': False, 'amount': 0}

    except Exception as e:
        logger.info(f'{traceback.format_exc()}')
        return {'success': False, 'amount': 0}
