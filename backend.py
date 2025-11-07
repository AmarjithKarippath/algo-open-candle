import json
import time
import logging
import pandas as pd

from fyers_apiv3 import fyersModel
from nsepython import nse_optionchain_scrapper
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT = os.getenv('CLIENT')
SECRET = os.getenv('SECRET')
REDIRECT_URL = os.getenv('REDIRECT_URL')
LOG_PATH = r"{}".format(os.getenv('LOG_PATH'))
SYMBOL = os.getenv('SYMBOL')

# Trade Settings
QTY = 75
LIMIT_OFFSET = 10
SL = 10
PT = SL * 1

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_nse_data(symbol="NIFTY"):
    return nse_optionchain_scrapper(symbol.upper())


def get_atm_strike(data: dict):
    ltp = float(data['records']['underlyingValue'])
    strike_price_list = [x['strikePrice'] for x in data['records']['data']]
    atm = sorted([[round(abs(ltp - i), 2), i] for i in strike_price_list])[0][1]
    return float(atm)


def find_symbol(strike: float):
    instruments = pd.read_csv(r'https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    ism = instruments[instruments[13] == '{}'.format(SYMBOL)]
    return ism[ism[15] == strike][0:2][9].to_list()


class Auth:
    def __init__(self):
        self.auth_token = None
        self.session = fyersModel.SessionModel(
            client_id=CLIENT,
            secret_key=SECRET,
            redirect_uri=REDIRECT_URL,
            response_type="code",
            grant_type="authorization_code")

    def generate_authcode(self):
        return self.session.generate_authcode()

    def set_token(self, auth: str):
        self.session.set_token(auth)

    def generate_access_token(self):
        return self.session.generate_token()['access_token']


class FyersConnect:
    def __init__(self):
        self.__fyers = None

    def connect(self, token: str):
        self.__fyers = fyersModel.FyersModel(
            token=token,
            is_async=False,
            log_path=LOG_PATH,
            client_id=CLIENT)

    def get_connection(self):
        return self.__fyers

def find_atm_symbols():
    payload = get_nse_data()
    atm_strike = get_atm_strike(data=payload)
    logger.info(f"atm -> {atm_strike}")
    symbols = find_symbol(atm_strike)
    logger.info(f"symbols -> {symbols}")
    data = {
        "symbols": f"{symbols[0]},{symbols[1]}",
    }
    return data, symbols


def place_trade(trade_symbol, order_p, trader):

    data = {
        "symbol": trade_symbol,
        "qty": QTY,
        "side": 1,
        "type": 1,
        "productType": "BO",
        "limitPrice": round(order_p),
        "stopPrice": 0,
        "disclosedQty": 0,
        "validity": "DAY",
        "offlineOrder": "False",
        "stopLoss": SL,
        "takeProfit": PT
    }
    logger.info(f"API POST data -> {data}")
    response = trader.place_order(data=data)
    logger.info(f"order placement -> {response}")
    logger.info(f"order data -> {data}")



def prepare_trade(trader):
    t1 = time.time()
    data, symbols = find_atm_symbols()
    quotes = trader.quotes(data=data)
    logger.info(f"quotes -> {json.dumps(quotes, indent=4)}")
    ce_p = quotes['d'][0]['v']['lp']
    pe_p = quotes['d'][1]['v']['lp']
    ce_o = quotes['d'][0]['v']['open_price']
    pe_o = quotes['d'][1]['v']['open_price']
    logger.info(f"ce_p -> {ce_p}")
    logger.info(f"pe_p -> {pe_p}")
    logger.info(f"ce_o -> {ce_o}")
    logger.info(f"pe_o -> {pe_o}")
    trade_symbol = symbols[0] if ce_p < pe_p else symbols[1]
    order_p = (ce_o if ce_p < pe_p else pe_o) - LIMIT_OFFSET
    sl_p = order_p - SL
    logger.info(f"Trade plan -> symbol: {trade_symbol}, order price: {order_p}, sl: {sl_p}")
    place_trade(trade_symbol, order_p, trader)
    # final steps
    t2 = time.time()
    logger.info(f"total time: {round(t2 - t1, 2)} sec.")
