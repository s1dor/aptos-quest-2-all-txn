from aptos_sdk.client import RestClient

from logger import setup_gay_logger
from constant import MAX_SLIPPAGE_PERCENT
from utils import get_apt_price, append_digit_to_integer

SLIPPAGE = (100 - MAX_SLIPPAGE_PERCENT) / 100
Z8 = 10 ** 8
Z6 = 10 ** 6
Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")


def submit_and_log_transaction(account, payload, logger, silence=False):
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
        return True
    except AssertionError as e:
        if not silence:
            logger.error(f"AssertionError caught: {e}")
        return False
    except Exception as e:
        if not silence:
            logger.critical(f"An unexpected error occurred: {e}")
        return False


def swap_zUSDC_to_MOD(account, amount_zUSDC, retries=2):
    logger = setup_gay_logger('swap_zUSDC_to_MOD')

    slippage_dec = 0.01 * (2 - retries)
    normalization = amount_zUSDC / Z6
    MOD_slip = normalization * (SLIPPAGE - slippage_dec)
    MOD_slip_int = int(MOD_slip * Z8)

    payload = {
        "type": "entry_function_payload",
        "function": "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool_scripts::swap_exact_in",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD"
        ],
        "arguments": [
            str(amount_zUSDC),
            str(MOD_slip_int)
        ],
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_zUSDC_to_MOD(account, amount_zUSDC, retries-1)

def swap_APT_to_MOD(account, amount_APT, retries = 2):
    logger = setup_gay_logger('swap_APT_to_MOD')

    slippage_dec = 0.01 * (2 - retries)
    normalization = amount_APT / Z8
    apt_price = get_apt_price()
    MOD_slip = apt_price * normalization * (SLIPPAGE - slippage_dec)
    MOD_slip_int = int(MOD_slip * Z8)

    payload = {
      "function": "0x60955b957956d79bc80b096d3e41bad525dd400d8ce957cdeb05719ed1e4fc26::router::swap_exact_in_2",
      "type_arguments": [
        "0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL",
        "0x1::aptos_coin::AptosCoin",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_50",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_50",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
        "0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_20",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_80",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
        "0x1::aptos_coin::AptosCoin",
        "0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL",
        "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD"
      ],
      "arguments": [
        str(amount_APT),
        str(MOD_slip_int)
      ],
      "type": "entry_function_payload"
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_APT_to_MOD(account, amount_APT, retries-1)


def swap_MOD_to_APT(account, amount_MOD, retries = 2):
    logger = setup_gay_logger('swap_MOD_to_zUSDC')

    slippage_dec = 0.01 * (2 - retries)
    apt_price = get_apt_price()
    normalization = amount_MOD / Z8
    APT_ideal = normalization / apt_price
    APT_slip = APT_ideal * (SLIPPAGE - slippage_dec)
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "type": "entry_function_payload",
        "function": "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool_scripts::swap_exact_in",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
            "0x1::aptos_coin::AptosCoin",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_50",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::weighted_pool::Weight_50",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(amount_MOD),
            str(APT_slip_int)
        ],
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_MOD_to_APT(account, amount_MOD, retries - 1)


def stake_MOD(account, amount_MOD: int):
    logger = setup_gay_logger('deposit_MOD')

    payload = {
        "type": "entry_function_payload",
        "function": "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool_scripts::deposit_mod",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool::Crypto"
        ],
        "arguments": [
            str(amount_MOD)
        ],
    }

    submit_and_log_transaction(account, payload, logger)


def unstake_MOD(account, amount_MOD: int):
    logger = setup_gay_logger('deposit_MOD')

    payload = {
        "type": "entry_function_payload",
        "function": "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool_scripts::withdraw_mod",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool::Crypto"
        ],
        "arguments": [
            str(amount_MOD)
        ],
    }

    submit_and_log_transaction(account, payload, logger)


def register_coin(account, to_register: str):
    logger = setup_gay_logger(f'register_coin:<{to_register}>')

    payload = {
        "type": "entry_function_payload",
        "function": "0x1::managed_coin::register",
        "type_arguments": [
            to_register
        ],
        "arguments": []
    }

    submit_and_log_transaction(account, payload, logger)


def swap_APT_to_zUSDC_via_liquidswap(account, amount, retries = 2):
    logger = setup_gay_logger('swap_APT_to_zUSDC_via_liquidswap')

    slippage_dec = 0.01 * (2 - retries)
    apt_price = get_apt_price()
    normalization = amount / Z8
    zUSDC_ideal = apt_price * normalization
    zUSDC_slip = zUSDC_ideal * (SLIPPAGE - slippage_dec)
    zUSDC_slip_int = int(zUSDC_slip * Z6)

    payload = {
        "type": "entry_function_payload",
        "function": "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12::scripts_v2::swap",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12::curves::Uncorrelated"
        ],
        "arguments": [
            str(amount),
            str(zUSDC_slip_int)
        ],
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_APT_to_zUSDC_via_liquidswap(account, amount, retries-1)


def open_merkle_order(account, amount_zUSDC: int):
    # Fake tx, no actual position will be open

    logger = setup_gay_logger('open_merkle_order')

    leverage = 130
    position_size = leverage * amount_zUSDC
    if position_size <= 300000000:
        return None

    apt = int(get_apt_price() * Z8)
    margin_requirement = 1 / leverage
    liquidation_price = int(apt * (1 - margin_requirement))
    stop_loss_price = int(apt * (1 - 0.10 / leverage))
    take_profit_price = int(apt * (1 + 0.20 / leverage))

    payload = {
        "function": "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06::managed_trading::place_order_with_referrer",
        "type_arguments": [
            "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06::pair_types::APT_USD",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            str(position_size),
            str(amount_zUSDC),
            str(append_digit_to_integer(liquidation_price, 10)),
            True,
            True,
            True,
            str(append_digit_to_integer(stop_loss_price, 59)),
            str(append_digit_to_integer(take_profit_price, 60)),
            False,
            "0x0"
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def stake_APT(account, amount: int):
    logger = setup_gay_logger('stake_APT')

    if amount < 20000000:
        logger.error(f"Amount ({amount / Z8} ATP) less than required (0.2 APT)")
        return

    payload = {
        "function": "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a::router::deposit_and_stake_entry",
        "type_arguments": [],
        "arguments": [
            str(amount),
            str(account.address())
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def register_gator_market_account(account):
    logger = setup_gay_logger('register_gator_market_account')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::user::register_market_account",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0"
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def deposit_zUSDC_to_gator(account, zUSDC_amount: int):
    logger = setup_gay_logger('deposit_zUSDC_to_gator')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::user::deposit_from_coinstore",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0",
            str(zUSDC_amount)
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def withdraw_APT_from_gator(account, APT_amount: int, retries=10):
    logger = setup_gay_logger('withdraw_APT_from_gator')

    logger.info(f"Trying to withdraw {APT_amount} from gator...")

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::user::withdraw_to_coinstore",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            "7",
            str(APT_amount)
        ],
        "type": "entry_function_payload"
    }
    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        withdraw_APT_from_gator(account, int(APT_amount * 0.999), retries - 1)


def swap_zUSDC_to_APT_via_gator(account):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_gator')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::market::place_market_order_user_entry",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0x63e39817ec41fad2e8d0713cc906a5f792e4cd2cf704f8b5fab6b2961281fa11",
            False,
            "100000000",
            3
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def swap_zUSDC_to_APT_via_pancakeswap(account, zUSDC_amount, retries = 2):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_pancakeswap')

    slippage_dec = 0.01 * (2 - retries)
    apt_price = get_apt_price()
    normalization = zUSDC_amount / Z6
    APT_ideal = normalization / apt_price
    APT_slip = APT_ideal * (SLIPPAGE - slippage_dec)
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "function": "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfe19850fa::router::swap_exact_input",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(zUSDC_amount),
            str(APT_slip_int)
        ],
        "type": "entry_function_payload"
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_zUSDC_to_APT_via_pancakeswap(account, zUSDC_amount, retries-1)


def swap_stAPT_to_APT_via_pancakeswap(account, stAPT_amount, retries = 2):
    logger = setup_gay_logger('swap_stAPT_to_APT_via_pancakeswap')

    slippage_dec = 0.01 * (2 - retries)
    normalization = stAPT_amount / Z8
    APT_slip = normalization * (SLIPPAGE - slippage_dec)
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "function": "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfe19850fa::router::swap_exact_input",
        "type_arguments": [
            "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a::stapt_token::StakedApt",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(stAPT_amount),
            str(APT_slip_int)
        ],
        "type": "entry_function_payload"
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_stAPT_to_APT_via_pancakeswap(account, stAPT_amount, retries-1)


def swap_zUSDC_to_APT_via_sushiswap(account, zUSDC_amount, retries = 2):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_sushiswap')

    slippage_dec = 0.01 * (2 - retries)
    apt_price = get_apt_price()
    normalization = zUSDC_amount / Z6
    APT_ideal = normalization / apt_price
    APT_slip = APT_ideal * (SLIPPAGE - slippage_dec)
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "function": "0x31a6675cbe84365bf2b0cbce617ece6c47023ef70826533bde5203d32171dc3c::router::swap_exact_input",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(zUSDC_amount),
            str(APT_slip_int)
        ],
        "type": "entry_function_payload"
    }

    if not submit_and_log_transaction(account, payload, logger, retries > 0) and retries > 0:
        swap_zUSDC_to_APT_via_sushiswap(account, zUSDC_amount, retries-1)

def deposit_stAPT_on_aries(account, stAPT_amount):
    logger = setup_gay_logger('deposit_stAPT_on_aries')

    payload = {
        "function": "0x9770fa9c725cbd97eb50b2be5f7416efdfd1f1554beb0750d4dae4c64e860da3::controller::deposit",
        "type_arguments": [
            "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a::stapt_token::StakedApt"
        ],
        "arguments": [
            "0x4d61696e204163636f756e74",
            str(stAPT_amount),
            False
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def borrow_APT_on_aries(account, APT_amount):
    logger = setup_gay_logger('borrow_APT_on_aries')

    payload = {
        "function": "0x9770fa9c725cbd97eb50b2be5f7416efdfd1f1554beb0750d4dae4c64e860da3::controller::withdraw",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            "0x4d61696e204163636f756e74",
            str(APT_amount),
            True
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def repay_APT_on_aries(account):
    logger = setup_gay_logger('repay_APT_on_aries')

    payload = {
        "function": "0x9770fa9c725cbd97eb50b2be5f7416efdfd1f1554beb0750d4dae4c64e860da3::controller::deposit",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            "0x4d61696e204163636f756e74",
            "18446744073709551615",  # INF
            True
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)


def withdraw_stAPT_on_aries(account):
    logger = setup_gay_logger('withdraw_stAPT_on_aries')

    payload = {
        "function": "0x9770fa9c725cbd97eb50b2be5f7416efdfd1f1554beb0750d4dae4c64e860da3::controller::withdraw",
        "type_arguments": [
            "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a::stapt_token::StakedApt"
        ],
        "arguments": [
            "0x4d61696e204163636f756e74",
            "18446744073709551615",  # INF
            False
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)
