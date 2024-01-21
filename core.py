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
    swap_zUSDC_to_APT_via_sushiswap,
    withdraw_APT_from_gator,
    swap_stAPT_to_APT_via_pancakeswap,
    deposit_stAPT_on_aries,
    borrow_APT_on_aries,
    repay_APT_on_aries,
    withdraw_stAPT_on_aries
)

from complex_transactions import (
    start_gator_ops,
    start_MOD_ops,
    start_sushi_ops,
    borrow_APT_for_stAPT,
    repay_APT_get_stAPT,
)

from utils import get_coin_value, get_account_balance, check_registration, get_apt_price
from constant import zUSDC_coin, MOD_coin, stAPT_coin, MIN_SLEEP, MAX_SLEEP
from logger import setup_gay_logger
from transactions import Rest_Client

Z8 = 10**8
Z6 = 10**6

def process_cheap_key(key):
    # Starting
    account = Account.load_key(key)
    address = account.address()

    logger = setup_gay_logger(f"{address}")
    logger.info(f"Processing wallet {address}...")

    # Checking initial wallet balance
    zUSDC_value = int(get_coin_value(address, zUSDC_coin))
    MOD_value = int(get_coin_value(address, MOD_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    stAPT_value = int(get_coin_value(address, stAPT_coin))
    logger.info(
        f"Initial wallet balance: {balance_APT / Z8} APT, {zUSDC_value / Z6} USDC, {MOD_value / Z8} MOD, {stAPT_value / Z8} stAPT")

    time.sleep(10)

    # [Randomization] Swapping some APT to zUSDC

    # Staking APT
    balance_APT = get_account_balance(Rest_Client, account)
    APT_to_stake = int(random.uniform(0.5, 0.8) * balance_APT)
    logger.info(f"Staking {APT_to_stake / Z8}(out of {balance_APT / Z8}) APT...")
    stake_APT(account, APT_to_stake)

    time.sleep(10)

    # Borrowing APT
    borrow_APT_for_stAPT(account)

    time.sleep(10)

    # Swapping APT to zUSDC via liquidswap
    balance_APT = get_account_balance(Rest_Client, account)
    APT_to_swap = int(balance_APT * 0.95)
    logger.info(f"Swapping {APT_to_swap / Z8}(out of {balance_APT / Z8}) APT to zUSDC...")
    swap_APT_to_zUSDC_via_liquidswap(account, APT_to_swap)

    time.sleep(10)

    # Swapping zUSDC to APT via Gator/Sushiswap/MOD staking
    logger.info("Swapping zUSDC to APT via Gator, Sushi and Mod staking...")
    zUSDC_value = int(get_coin_value(address, zUSDC_coin))
    MOD_value = int(get_coin_value(address, MOD_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {zUSDC_value / Z6} USDC, {balance_APT / Z8} APT, {MOD_value / Z8} MOD")

    start_ops = [start_gator_ops, start_MOD_ops, start_sushi_ops]
    random.shuffle(start_ops)
    for i in range(len(start_ops)):
        start_ops[i](account, zUSDC_value, i)

    zUSDC_value = int(get_coin_value(address, zUSDC_coin))
    MOD_value = int(get_coin_value(address, MOD_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {zUSDC_value / Z6} USDC, {balance_APT / Z8} APT, {MOD_value / Z8} MOD")

    time.sleep(10)

    # Repaying APT
    logger.info("Repaying APT...")
    stAPT_value = int(get_coin_value(address, stAPT_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {stAPT_value / Z8} stAPT, {balance_APT / Z8} APT")

    repay_APT_get_stAPT(account)

    stAPT_value = int(get_coin_value(address, stAPT_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {stAPT_value / Z8} stAPT, {balance_APT / Z8} APT")

    time.sleep(10)

    # Swapping stAPT to APT via Pancake
    logger.info("Swapping stAPT to APT via Pancake")
    stAPT_value = int(get_coin_value(address, stAPT_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {stAPT_value / Z8} stAPT, {balance_APT / Z8} APT")
    swap_stAPT_to_APT_via_pancakeswap(account, stAPT_value)

    time.sleep(10)

    # Checking final wallet balance
    zUSDC_value = int(get_coin_value(address, zUSDC_coin))
    MOD_value = int(get_coin_value(address, MOD_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    stAPT_value = int(get_coin_value(address, stAPT_coin))
    logger.info(f"Final wallet balance: {balance_APT / Z8} APT, {zUSDC_value / Z6} USDC, {MOD_value / Z8} MOD, {stAPT_value / Z8} stAPT")

    #TODO: Add some randomness, add flag to choose if we want to collect everything back to APT | Implement disperser


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
    result = process_cheap_key(pkey)
    if result == 0:
        delete_line_from_file('pkey.txt', pkey)
    time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
