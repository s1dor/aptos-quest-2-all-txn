import random
import time
from aptos_sdk.account import Account

from transactions import (
    swap_zUSDC_to_MOD,
    swap_MOD_to_APT,
    stake_MOD,
    unstake_MOD,
    register_coin,
    swap_APT_to_zUSDC_via_liquidswap,
    open_merkle_order,
    stake_APT,
    register_gator_market_account,
    deposit_zUSDC_to_gator,
    swap_zUSDC_to_APT_via_gator,
    swap_zUSDC_to_APT_via_pancakeswap,
    swap_zUSDC_to_APT_via_sushisvap,
    withdraw_APT_from_gator
)

from utils import get_coin_value, get_account_balance, check_registration
from constant import zUSDC_coin, MOD_coin, MIN_SLEEP, MAX_SLEEP
from logger import setup_gay_logger
from transactions import Rest_Client

Z8 = 10**8
Z6 = 10**6

def process_key(key):
    account = Account.load_key(key)
    address = account.address()

    logger = setup_gay_logger(f"{address}")

    logger.info("Getting APT available balance...")
    APT_balance = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {APT_balance} APT")

    logger.info("Withdtaw APT from gator")
    withdraw_APT_from_gator(account, 10000000)
    time.sleep(5)

    logger.info("Getting APT available balance...")
    APT_balance = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {APT_balance} APT")
    return

    logger.info("Checking registration...")
    if check_registration(address, zUSDC_coin) is False:
        logger.info("Registering coin...")
        register_coin(account, zUSDC_coin)
        logger.info("Coin registered.")

    logger.info("Getting initial wallet balance...")
    initial_balance_APT = get_account_balance(Rest_Client, account)
    fix = initial_balance_APT / Z8
    logger.info(f"Starting wallet balance is {fix} APT")
    if fix < 1:
        logger.critical("Wallet is too broke, add some coin")
        return 1

    half_APT = int(initial_balance_APT * 0.5)
    quarter_APT = int(initial_balance_APT * 0.25)

    logger.info("Swapping APT to zUSDC via liquidswap...")
    swap_APT_to_zUSDC_via_liquidswap(account, half_APT)

    time.sleep(10)

    logger.info("Getting zUSDC coin value...")
    zUSDC_value = int(get_coin_value(address, zUSDC_coin))

    zUSDC_value_third = int(zUSDC_value * 0.3)

    logger.info(f"Wallet has {zUSDC_value / Z6} USDC")
    if zUSDC_value < 4000000:
        logger.critical("Wallet is too broke, add some coin")
        return 1

    logger.info("Opening Merkle order...")
    open_merkle_order(account, 3000000)
    time.sleep(11)

    logger.info("Swapping zUSDC to MOD...")
    swap_zUSDC_to_MOD(account, zUSDC_value_third)
    logger.info("Getting MOD available balance...")
    time.sleep(15)
    MOD_availabe = int(get_coin_value(address, MOD_coin))

    logger.info(f"Wallet has {MOD_availabe / Z8} MOD")
    logger.info("Staking MOD...")
    stake_MOD(account, MOD_availabe)
    time.sleep(12)

    logger.info("Staking APT...")
    stake_APT(account, quarter_APT)
    time.sleep(13)

    logger.info("Registering gator market account...")
    register_gator_market_account(account)
    time.sleep(9)

    logger.info("Depositing zUSDC to gator...")
    deposit_zUSDC_to_gator(account, zUSDC_value_third)
    time.sleep(11)

    logger.info("Swapping zUSDC to APT via gator...")
    swap_zUSDC_to_APT_via_gator(account)
    time.sleep(14)

    logger.info("Calculating zUSDC value for Pancakeswap...")
    time.sleep(5)
    fix2 = int(get_coin_value(address, zUSDC_coin))
    zUSDC_value2 = int(fix2 * 0.5)

    logger.info("Swapping zUSDC to APT via Pancakeswap...")
    swap_zUSDC_to_APT_via_pancakeswap(account, zUSDC_value2)
    time.sleep(10)

    logger.info("Calculating remaining zUSDC value for Sushiswap...")
    time.sleep(5)
    zUSDC_value_left = int(get_coin_value(address, zUSDC_coin))
    time.sleep(11)

    logger.info("Swapping zUSDC to APT via Sushiswap...")
    swap_zUSDC_to_APT_via_sushisvap(account, zUSDC_value_left)

    logger.info("Process completed successfully.")
    return 0

def delete_line_from_file(filename, line_to_delete):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            if line.strip("\n") != line_to_delete:
                file.write(line)

# Main logic
with open('pkey.txt', 'r') as file:
    pkeys = file.readlines()

for pkey in pkeys:
    pkey = pkey.strip()
    result = process_key(pkey)
    if result == 0:
        delete_line_from_file('pkey.txt', pkey)
    time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
