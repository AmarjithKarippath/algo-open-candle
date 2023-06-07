import time
import datetime
import logging
import sys

from backend import prepare_trade

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

trade_placed = False

start = datetime.time(9, 15, 0)
end = datetime.time(15, 10, 0)


def time_in_range(start, end, current):
    return start <= current <= end


def opening_candle_trade(trader):
    while True:
        try:
            current = datetime.datetime.now().time()
            logger.info(f"current ->{current}")
            is_trade_window = time_in_range(start, end, current)
            if is_trade_window:
                prepare_trade(trader)
                logger.info("Order placed.")
                break

        except KeyboardInterrupt:
            sys.exit(0)

        else:
            time.sleep(1)
