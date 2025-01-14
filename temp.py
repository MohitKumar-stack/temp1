import json
import time as t
# from alice_blue import Aliceblue
import pandas as pd
import time as t
import pytz
from decimal import Decimal
from datetime import datetime,timedelta
from pya3 import *
import ssl
import mysql.connector
from mysql.connector import Error
import json

def get_last_trade_price(strikes, expiry_date, option_type):
    try:
        # Initialize AliceBlue session
        alice = Aliceblue("1721033", "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas")
        alice.get_session_id()

        # Update the NFO contract file before subscribing
        alice.get_contract_master("NFO")

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
            print("Socket Error:", message)

        def feed_data(message):
            nonlocal ltp
            feed_message = json.loads(message)
            if feed_message.get("t") == "tk":
                ltp = feed_message.get("lp")

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
            t.sleep(0.4)

        # Get the updated instrument data
        instrument = alice.get_instrument_by_symbol("NFO", f"NIFTY{expiry_date}{option_type}{strikes}")

        # Subscribe to the instrument
        alice.subscribe([instrument])

        # Wait for the LTP to be received
        timeout = 7  # Increased timeout
        start_time = t.time()
        while ltp is None and (t.time() - start_time) < timeout:
            t.sleep(0.4)

        # Unsubscribe after fetching data
        alice.unsubscribe([instrument])

        # Return the Last Trade Price
        if ltp is None:
            raise TimeoutError("Failed to receive LTP within the timeout period.")

        return float(ltp)

    except Exception as e:
        print("Error in get_last_trade_price:", str(e))
        return None

c=get_last_trade_price(23700,"23JAN25","C")
print(c)

