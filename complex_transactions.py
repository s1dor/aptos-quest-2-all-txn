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
    deposit_stAPT_on_aries,
    borrow_APT_on_aries,
    repay_APT_on_aries,
    withdraw_stAPT_on_aries
)

from utils import get_coin_value, get_account_balance, check_registration, get_apt_price
from constant import zUSDC_coin, MOD_coin, stAPT_coin, MIN_SLEEP, MAX_SLEEP
from logger import setup_gay_logger
from transactions import Rest_Client

Z8 = 10 ** 8
Z6 = 10 ** 6


def do_gator_ops(account, zUSDC_amount, register=True):
    logger = setup_gay_logger("do_gator_ops")

    APT_price = get_apt_price()
    APT_amount = zUSDC_amount / Z6 / APT_price * Z8

    if register:
        logger.info("Registering gator market account...")
        register_gator_market_account(account)

    logger.info(f"Depositing {zUSDC_amount / Z6} zUSDC to gator...")
    deposit_zUSDC_to_gator(account, zUSDC_amount)
    time.sleep(10)

    logger.info("Swapping zUSDC to APT...")
    swap_zUSDC_to_APT_via_gator(account)
    time.sleep(10)

    logger.info(f"Withdrawing {APT_amount / Z8} APT from gator...")
    withdraw_APT_from_gator(account, int(APT_amount))


def do_MOD_ops(account):
    logger = setup_gay_logger("do_MOD_ops")
    address = account.address()

    MOD_availabe = int(get_coin_value(address, MOD_coin))
    logger.info(f"Wallet has {MOD_availabe / Z8} MOD")

    logger.info(f"Staking {MOD_availabe / Z8} MOD...")
    stake_MOD(account, MOD_availabe)

    logger.info(f"Unstaking {MOD_availabe / Z8} MOD...")
    unstake_MOD(account, MOD_availabe)

    MOD_availabe = int(get_coin_value(address, MOD_coin))
    logger.info(f"Wallet has {MOD_availabe / Z8} MOD")

    logger.info(f"Swapping {MOD_availabe / Z8} MOD to APT...")
    swap_MOD_to_APT(account, MOD_availabe)


def start_gator_ops(account, zUSDC_cap, pos):
    logger = setup_gay_logger("start_gator_ops")
    address = account.address()

    zUSDC_amount = int(get_coin_value(address, zUSDC_coin))
    logger.info(f"Wallet has {zUSDC_amount / Z6} USDC")

    if pos < 2:
        m = random.uniform(0.5, 0.6)
        zUSDC_amount = int(zUSDC_cap * m)

    do_gator_ops(account, zUSDC_amount, False)  # should be False for used account, True for new


def start_MOD_ops(account, zUSDC_cap, pos):
    logger = setup_gay_logger("start_MOD_ops")
    address = account.address()

    zUSDC_amount = int(get_coin_value(address, zUSDC_coin))
    logger.info(f"Wallet has {zUSDC_amount / Z6} zUSDC")

    if pos < 2:
        m = random.uniform(0.15, 0.25)
        zUSDC_amount = int(zUSDC_cap * m)

    logger.info(f"Swapping {zUSDC_amount / Z6} zUSDC to MOD")
    swap_zUSDC_to_MOD(account, zUSDC_amount)

    do_MOD_ops(account)


def start_sushi_ops(account, zUSDC_cap, pos):
    logger = setup_gay_logger("start_sushi_ops")
    address = account.address()

    zUSDC_amount = int(get_coin_value(address, zUSDC_coin))
    logger.info(f"Wallet has {zUSDC_amount / Z6} zUSDC")

    if pos < 2:
        m = random.uniform(0.15, 0.25)
        zUSDC_amount = int(zUSDC_cap * m)

    logger.info(f"Swapping {zUSDC_amount / Z6} zUSDC to APT")
    swap_zUSDC_to_APT_via_sushiswap(account, zUSDC_amount)


def borrow_APT_for_stAPT(account):
    logger = setup_gay_logger("borrow_APT_for_stAPT")
    address = account.address()

    logger.info("Borrowing APT for stAPT...")

    stAPT_value = int(get_coin_value(address, stAPT_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {stAPT_value / Z8} stAPT, {balance_APT / Z8} APT")

    logger.info(f"Depositing {stAPT_value / Z8} stAPT to aries...")
    deposit_stAPT_on_aries(account, stAPT_value)

    logger.info(f"Borrowing {int(stAPT_value * 0.55) / Z8} APT from aries...")
    borrow_APT_on_aries(account, int(stAPT_value * 0.55))

    stAPT_value = int(get_coin_value(address, stAPT_coin))
    balance_APT = get_account_balance(Rest_Client, account)
    logger.info(f"Wallet has {stAPT_value / Z8} stAPT, {balance_APT / Z8} APT")


def repay_APT_get_stAPT(account):
    logger = setup_gay_logger("repay_APT_get_stAPT")

    logger.info(f"Repaying all APT to aries...")
    repay_APT_on_aries(account)

    logger.info(f"Withdrawing all stAPT from aries...")
    withdraw_stAPT_on_aries(account)




#do_random_ops(account):
