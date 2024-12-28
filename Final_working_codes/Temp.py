import pandas as pd
import time as t
import pytz
from decimal import Decimal
from datetime import datetime,timedelta
from pya3 import *
import ssl
import json
import csv
from alice_blue import  TransactionType, OrderType, ProductType
import os
from key_generator import key_genrater  # for key_genrater function
from get_yesterday_low import analyze_csv  # for get_yesterday_low function
import logging
from order_trigger import place_order,sell_order

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Call the key_genrater function to get the each_code
key_genrater()  # for key_genrater function
# Call the get_yesterday_low function to get the yesterday low

global yesterday_low
yesterday_low=analyze_csv()
# print("yesterday low",yesterday_low)

# yesterday_low= 23685.15

# get_yesterday_low()  # for get_yesterday_low function
# print("yesterday low",yesterday_low)
current_time = datetime.strptime(datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S").time()


# Ensure SSL is available
try:
    ssl.PROTOCOL_TLS
except AttributeError:
    raise ImportError("SSL module is not available. Please ensure your Python environment supports SSL.")
contract = pd.read_csv('NFO.csv')

# Credentials
username = "1721033"
api_key = "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas"

# Initialize Aliceblue session
alice = Aliceblue(username, api_key)
session_id = alice.get_session_id()['sessionID']

# IST timezone
ist_timezone = pytz.timezone('Asia/Kolkata')


def get_last_trade_price(strikes, expiry_date,option_type):
    alice = Aliceblue("1721033", "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas")
    alice.get_session_id()

    ltp = None
    socket_opened = False

    def socket_open():
        nonlocal socket_opened
        socket_opened = True

    def socket_close():
        nonlocal ltp
        ltp = None

    def socket_error(message):
        nonlocal ltp
        ltp = None
        # print("Socket Error:", message)

    def feed_data(message):
        nonlocal ltp
        feed_message = json.loads(message)
        if feed_message["t"] == "tk":
            ltp = int(feed_message.get("lp"))

    # Start the WebSocket
    alice.start_websocket(
        socket_open_callback=socket_open,
        socket_close_callback=socket_close,
        socket_error_callback=socket_error,
        subscription_callback=feed_data,
        run_in_background=True
    )

    # Wait for the WebSocket to open
    while not socket_opened:
        t.sleep(0.2)

    # Subscribe to the instrument
    instrument = alice.get_instrument_by_symbol("NFO", f"NIFTY{expiry_date}{option_type}{strikes}")
    alice.subscribe([instrument])

    # Wait for the LTP to be received
    timeout = 5  # seconds
    start_time = t.time()
    while ltp is None and (t.time() - start_time) < timeout:
        t.sleep(0.2)

    # Unsubscribe and close the WebSocket

    if ltp is None:
        raise TimeoutError("Failed to receive LTP within the timeout period.")

    return(int(ltp))
    

# strikes=24000
# expiry_date="09JAN25"
# option_type="C"
# get_last_trade_price(strikes, expiry_date,option_type)