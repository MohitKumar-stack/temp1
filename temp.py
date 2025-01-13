
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

def get_last_trade_price(strikes,expiry_date,option_type):
    try :
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
            t.sleep(0.3)

        # Subscribe to the instrument
        instrument = alice.get_instrument_by_symbol("NFO", f"NIFTY{expiry_date}{option_type}{strikes}")
        alice.subscribe([instrument])

        # Wait for the LTP to be received
        timeout = 5  # seconds
        start_time = t.time()
        while ltp is None and (t.time() - start_time) < timeout:
            t.sleep(0.3)

        # Unsubscribe and close the WebSocket

        if ltp is None:
            raise TimeoutError("Failed to receive LTP within the timeout period.")

        return float(ltp)
    
    except:
        return 
    
print(get_last_trade_price(23600,"16JAN25","P"))

def get_expiry_date():
    today = datetime.now().date()  # Get today's date
    print("Today's Date:", today.strftime('%A, %d %b %Y'))  # Print today's date with the day
    print("Weekday Number:", today.weekday())  # Print the numeric representation of the weekday (Monday = 0, Sunday = 6)

    # Calculate how many days to add to reach next week's Thursday
    days_until_next_thursday = (3 - today.weekday()) % 7 + 7  # Always move to the Thursday of the next week

    next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday

    # Format the date as 'DDMMMYY'
    formatted_date = next_week_thursday.strftime('%d%b%y').upper()
    print("Next Week's Thursday Date:", formatted_date)

    return formatted_date

print(get_expiry_date())

