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
from account_helpers import get_token_account
from log_config import get_logger
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
        print("Response JSON:", response.json())
        sig = response.json()['result']
        print("sig ", sig)

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


def make_sell_tx(rpc, mint, bc, abc, token_account, owner, payer_keypair, token_amount, min_sol_output_slip):
    """ make sell tx from parameters """
    MINT = mint
    BONDING_CURVE = Pubkey.from_string(bc)
    ASSOCIATED_BONDING_CURVE = Pubkey.from_string(abc)
    ASSOCIATED_USER = token_account
    USER = owner
    poolkeys = get_poolkeys_sell(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER)
    sell = MAGIC_SELL
    integers = [
        sell,
        token_amount,
        min_sol_output_slip
    ]
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)
    swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, poolkeys)
    hash = rpc.get_latest_blockhash().value.blockhash
    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    instructions.append(swap_instruction)
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],
        hash,
    )
    tx = VersionedTransaction(compiled_message, [payer_keypair])
    serialized_tx = bytes(tx)
    return serialized_tx

def make_tx_buy(rpc, mint, bc, abc, token_account, token_account_instructions, owner, payer_keypair, token_out, max_sol_cost):
    """ make buy tx from parameters """
    MINT = Pubkey.from_string(mint)
    BONDING_CURVE = Pubkey.from_string(bc)
    ASSOCIATED_BONDING_CURVE = Pubkey.from_string(abc)
    ASSOCIATED_USER = token_account
    USER = owner

    poolkeys = get_poolkeys_buy(MINT, BONDING_CURVE, ASSOCIATED_BONDING_CURVE, ASSOCIATED_USER, USER)
    buy = MAGIC_BUY
    integers = [
        buy,
        token_out,
        max_sol_cost
    ]
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)
    swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, poolkeys)
    hash = rpc.get_latest_blockhash().value.blockhash
    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    if token_account_instructions:
        instructions.append(token_account_instructions)
    instructions.append(swap_instruction)
    address_lookup = []
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

def buy_calc(rpc, wallet, tokenca, bc, abc, price, token_amnt):
    #TODO token decimals

    #TODO as intial
    tdec = 6
    sdec = 9
    #sol_amnt = 0.005

    logger.info(f'price {price}')
    logger.info(f'token_amnt {token_amnt}')
    #logger.info(f'sol_amnt {sol_amnt}')

    #3x from initial price
    base_sol_amnt = token_amnt * price
    #TODO! adjust slippage
    factor = 3.0
    slip_sol_amnt = base_sol_amnt * factor

    logger.info(f'max_sol_cost {base_sol_amnt}')
    logger.info(f'max_sol_cost {slip_sol_amnt}')


    token_out = int(token_amnt * 10**tdec)
    max_sol_cost = int(slip_sol_amnt * 10**sdec)
    logger.info(f'token_out {token_out}')
    logger.info(f'max_sol_cost {max_sol_cost}')

    result = buy(rpc, wallet, tokenca, bc, abc, token_out, max_sol_cost)
    return [result, token_amnt]

def get_data_retry(tokenca):
    coin_data = None
    for _ in range(5):
        coin_data = get_coin_data(tokenca)
        if coin_data is None:
            print('coin_data is None')
            time.sleep(0.1)
        else:
            print('Valid coin_data found, exiting loop')
            break
    if coin_data is None:
        print('Failed to get valid coin data after 5 attempts')
        return None
    return coin_data

def buy_assist(rpc, wallet, tokenca, bc, abc):
    try:
        logger.info(f'walletpub {wallet.pubkey()}')
        logger.info(f'buy.....  token: {tokenca}\nbc {bc}\nabc: {abc}')

        # Set token and SOL amounts
        tdec = 6
        sdec = 9
        token_amnt = 1_000
        sol_amnt = 0.0001
        token_out = int(token_amnt * 10**tdec)
        max_sol_cost = int(sol_amnt * 10**sdec)
        logger.info(f'token_out.....  {token_out}\nmax_sol_cost {max_sol_cost}')

        # Execute buy
        buy_result = buy(rpc, wallet, tokenca, bc, abc, token_out, max_sol_cost)

        # Log buy result
        logger.info(f'buy_result: {buy_result}')
        
        return buy_result
    except Exception as e:
        logger.error(f"Error in buy_assist: {e}")
        logger.error(traceback.format_exc())
        return {'success': False, 'amount': 0}
    

def sell_assist(rpc, wallet, tokenca, bc, abc):
    #TODO calc input
    #TODO calc slippage
    tdec = 6
    sdec = 9
    poolkeys = {
        'mint': tokenca,
        'associated_bonding_curve': abc,\
        #'bonding_curve': coin_data['bondingCurveKey'],
        'bonding_curve': bc,
        #'virtual_sol_reserves': coin_data['virtual_sol_reserves'],
        #'virtual_token_reserves': coin_data['virtual_token_reserves']
    }
    token_amnt = 10_000
    sol_amnt = 0.005
    token_amount_dec = int(token_amnt * 10**tdec)
    min_sol_output_slip = int(sol_amnt * 10**sdec)
    #TODO! fix this
    #total_supply = coin_data['total_supply']
    #market_cap = coin_data['market_cap']
    return sell(rpc, wallet, tokenca, bc, abc, token_amount_dec, min_sol_output_slip)

def buy(rpc, payer_keypair, mint, bc, abc, token_out, max_sol_cost):
    try:
        logger.info(f'try buy.... {mint}')

        #coin_data = get_data_retry(mint)
        #if coin_data == None: return

        logger.info('owner')
        owner = payer_keypair.pubkey()
        logger.info(f'mint {mint}')
        logger.info(f'payer_keypair {payer_keypair}')

        balance = rpc.get_balance(owner).value
        logger.info(f'your balance {balance}')
        print(f'your balance {balance}')
        required_balance = max_sol_cost + 5000  # Add some buffer for fees

        if balance < required_balance:
            logger.error(f'Insufficient SOL. Balance: {balance}, Required: {required_balance}')
            return {'success': False, 'amount': 0}

        #mint = Pubkey.from_string(poolkeys['mint'])
        token_account, token_account_instructions = get_token_account(rpc, owner, mint)
        logger.info(f'token_account {token_account}')
        try:
            buytx = make_tx_buy(rpc, mint, bc, abc, token_account, token_account_instructions, owner, payer_keypair, token_out, max_sol_cost)
        except Exception as e:
            logger.error(f'error make buy tx {e}')

        logger.info(f"buy tx {buytx}")
        simulation_result = rpc.simulate_transaction(buytx, sig_verify=True)
        js = json.loads(simulation_result.to_json())
        print(js)
        verr = js['result']['value']['err']

        # Check the simulation result
        # TODO =
        if verr:
            if 'InstructionError' in verr.keys():
                elogs= js['result']['value']['logs']
                import pdb; pdb.set_trace()

                print("Simulation failed:", js['result']['value']['err'])
                #'Transfer: insufficient lamports 2492079, need 2851242'
                if any('insufficient lamports' in log for log in elogs):
                    print("not enough SOL")
                    return {'success': False, 'amount': 0}
                elif any('incorrect program id' in log for log in elogs):
                    print('issue with bc')

                return {'success': False, 'amount': 0}
        else:
            print("Simulation succeeded")

        txsig = None
        try:
            logger.info('send tx')
            serialized_tx = bytes(buytx)
            response = rpc.send_raw_transaction(serialized_tx)
            txsig = response.value
            logger.info(f'response {response}')
            logger.info(f'txsig {txsig}')
            #print('json ', response.to_json())
        except RPCException as e:
            import pdb; pdb.set_trace()
            emsg = e.args[0].message
            if '0x1772' in emsg:
                #'Transaction simulation failed: Error processing Instruction 3: custom program error: 0x1772'
                #slippage?
                print('??')
            elif 'incorrect program id' in emsg:
                #sourceAccount hasn't been created on mainnet yet.
                print('wrong program')
                #"Transaction simulation failed: Error processing Instruction 2: incorrect program id for instruction"
            else:
                logs = json.loads(e.args[0].data.to_json())['logs']
                #print(logs)
                incorrect_prog = 'Error processing Instruction 2: incorrect program id for instruction'
                overflow = 'panicked at programs/pump/src/lib.rs:615:48:\nattempt to subtract with overflow'
                if any(overflow in log for log in logs):
                    logger.error('overflow')
                    logger.error(logs)
                elif any(incorrect_prog in log for log in logs):
                    logger.error('incorrect porgra')
                else:
                    logger.error(f'error {e}')
            return {'success': False, 'amount': 0}

        if txsig != None:
            try:
                logger.info("try confirm")
                # Confirm transaction
                confirm = confirm_txn(rpc, txsig)
                #TODO get tx result
                if confirm == True:
                    logger.info(f'Succesfully bought {mint} \n{str(txsig)}')
                    #TODO return position size
                    return {'success': True, 'amount': 0}
                else:
                    logger.info(f"{Fore.red}[!] not confirmed")
                    return {'success': False, 'amount': 0}
                return confirm
            except Exception as e:
                print(f'exception trying confirm {e}')
        else:
            return {'success': False, 'amount': 0}

    except Exception as e:
        logger.info(f'{traceback.format_exc()}')
        return {'success': False, 'amount': 0}

#def sell(rpc, payer_keypair, coin_data, tokenca, bc, abc, token_amount, min_sol_output_slip, total_supply, market_cap):
def sell(rpc, payer_keypair, tokenca, bc, abc, token_amount, min_sol_output_slip):
    #TODO remove coindata
    print(f'try sell.... {tokenca}')
    try:
        owner = payer_keypair.pubkey()
        mint = Pubkey.from_string(tokenca)

        decimal = 6

        #price_per_token = market_cap * (10**decimal) / total_supply
        price_per_token = 0.0000003
        #TODO revist slippage calc
        min_sol_output_n = float(token_amount) * float(price_per_token)
        slippage_decimal = .3
        slippage = 1 - slippage_decimal
        min_sol_output_slip = int(min_sol_output_n * slippage)

        #token_account = get_associated_token_address(owner, mint)
        token_account, token_instructions = get_token_account(rpc, owner, tokenca)
        serialized_tx = make_sell_tx(rpc, mint, bc, abc, token_account, owner, payer_keypair, token_amount, min_sol_output_slip)
        txsig = None
        try:
            print('send tx')
            response = rpc.send_raw_transaction(serialized_tx)
            txsig = response.value
            print('response ', response)
            print('txsig ', txsig)
            #print('json ', response.to_json())
        except RPCException as e:
            logs = json.loads(e.args[0].data.to_json())['logs']
            #print(logs)
            incorrect_prog = 'Error processing Instruction 2: incorrect program id for instruction'
            overflow = 'panicked at programs/pump/src/lib.rs:615:48:\nattempt to subtract with overflow'
            if any(overflow in log for log in logs):
                print('overflow')
                print(logs)
            elif any(incorrect_prog in log for log in logs):
                print('incorrect porgra')
            else:
                print('error ', e)

        if txsig != None:
            try:
                print("try confirm")
                # Confirm transaction
                confirm = confirm_txn(rpc, txsig)
                #TODO get tx result
                if confirm == True:
                    logger.info(f'Succesfully sold {mint}\n{str(txsig)}')
                else:
                    logger.info('not confirmed')
                return confirm
            except Exception as e:
                logger.error(f'execption trying confirm {e}')

    except Exception as e:
        print(f'{traceback.format_exc()}')
        return False



# def get_token_acc(rpc, owner, tokenca):
#     tokenpub = Pubkey.from_string(tokenca)
#     owner_pubkey = owner.pubkey()
#     token_account = None
#     try:
#         account_data = rpc.get_token_accounts_by_owner(owner_pubkey, TokenAccountOpts(tokenpub))
#         try:
#             if len(account_data.value) > 0:
#                 token_account = account_data.value[0].pubkey
#                 token_account_instructions = None
#             else:
#                 #create account
#                 token_account_instructions = create_associated_token_account(owner_pubkey, owner_pubkey, tokenpub)
#                 token_account = get_associated_token_address(owner, tokenpub)
#         except Exception as e:
#                 token_account_instructions = create_associated_token_account(owner_pubkey, owner_pubkey, tokenpub)
#                 token_account = get_associated_token_address(owner, tokenpub)
#     #except InvalidParamsMessage
#     except Exception as e:
#         import traceback
#         import pdb; pdb.set_trace()
#         print(traceback.format_exc())
#         logger.error('error get tokenacc {e}')
#         print('cant find')

#     return token_account, token_account_instructions
