import logging
import json
import requests
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import BackgroundTasks, FastAPI, Depends

from backend import Auth, FyersConnect

from prepare_trade import opening_candle_trade

app = FastAPI()

logger = logging.getLogger(__name__)

obj = Auth()

fyers_obj = FyersConnect()

# To place order
@app.get("/home", response_class=HTMLResponse)
def home():
    res = obj.generate_authcode()
    logger.info(f"res -> {res}")
    return RedirectResponse(res)


@app.get("/orders", response_class=HTMLResponse)
def all_order():
    trader = fyers_obj.get_connection()
    orders = trader.orderbook() if trader else {}
    logger.info(f"orders -> {orders}")
    return JSONResponse(orders)


@app.get("/positions", response_class=HTMLResponse)
def get_positions():
    trader = fyers_obj.get_connection()
    positions = trader.positions() if trader else {}
    logger.info(f"positions -> {positions}")
    return JSONResponse(positions)


@app.get("/trades", response_class=HTMLResponse)
def get_trade_book():
    trader = fyers_obj.get_connection()
    trades = trader.tradebook() if trader else {}
    logger.info(f"trades -> {trades}")
    return JSONResponse(trades)


@app.get("/profile", response_class=HTMLResponse)
def current_profile():
    trader = fyers_obj.get_connection()
    profile = trader.get_profile() if trader else {}
    logger.info(f"profile -> {profile}")
    return JSONResponse(profile)


@app.get("/", response_class=HTMLResponse)
async def read_root(auth_code: str, background_tasks: BackgroundTasks):
    if not auth_code:
        return """
            <span style="color: red">
                Error while generating request token.
            </span>
            <a href='/'>Try again.<a>"""

    obj.set_token(auth=auth_code)
    access_token = obj.generate_access_token()
    logger.info(f"access_token -> {access_token}")
    fyers_obj.connect(token=access_token)
    trader = fyers_obj.get_connection()
    background_tasks.add_task(opening_candle_trade, trader)
    return "Request received successfully."
