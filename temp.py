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
# global strike_rate
# Configure logging
# logging.basicConfig(level=logging.DEBUG)




ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone).time()
formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()

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

#global variable declarations
global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
global total_call_quality,total_put_quality,global_investment_checker,at_10,at_1015,at_1030,at_1,at_115,at_130

#global variable assignment
strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality,global_investment_checker=0,0,0,0,0,0,0
LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130=0,0,0,0,0,0,0,0
option_type=[]
at_10,at_1015,at_1030,at_1,at_115,at_130=dict(),dict(),dict(),dict(),dict(),dict()


def get_last_trade_price(strikes, expiry_date, option_type):
    try:
        # Initialize AliceBlue session
        alice = Aliceblue("1721033", "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas")
        alice.get_session_id()

        # Update the NFO contract file before subscribing
        alice.get_contract_master("NFO")

        ltp = None
        socket_opened = False
        websocket_active = False

        def socket_open():
            nonlocal socket_opened
            socket_opened = True
            print("WebSocket connection opened.")

        def socket_close():
            nonlocal websocket_active
            websocket_active = False
            print("WebSocket connection closed.")

        def socket_error(message):
            print("Socket Error:", message)

        def feed_data(message):
            nonlocal ltp
            try:
                feed_message = json.loads(message)
                if feed_message.get("t") == "tk":
                    ltp = feed_message.get("lp")
            except Exception as e:
                print("Error processing feed data:", str(e))

        # Start the WebSocket
        alice.start_websocket(
            socket_open_callback=socket_open,
            socket_close_callback=socket_close,
            socket_error_callback=socket_error,
            subscription_callback=feed_data,
            run_in_background=True
        )

        # Wait for the WebSocket to open
        timeout = 7  # Maximum wait time
        start_time = t.time()
        while not socket_opened and (t.time() - start_time) < timeout:
            t.sleep(0.6)

        if not socket_opened:
            raise TimeoutError("WebSocket failed to open within the timeout period.")

        websocket_active = True

        # Get the updated instrument data
        instrument = alice.get_instrument_by_symbol("NFO", f"NIFTY{expiry_date}{option_type}{strikes}")

        # Subscribe to the instrument
        alice.subscribe([instrument])

        # Wait for the LTP to be received
        ltp_timeout = 10  # Timeout for LTP
        start_time = t.time()
        while ltp is None and (t.time() - start_time) < ltp_timeout:
            t.sleep(0.5)

        # Unsubscribe and close WebSocket if LTP is fetched
        alice.unsubscribe([instrument])
        if websocket_active:
            alice.stop_websocket()

        if ltp is None:
            raise TimeoutError("Failed to receive LTP within the timeout period.")

        return float(ltp)

    except Exception as e:
        print("Error in get_last_trade_price:", str(e))
        return None



for i in [23400,23450,23500,23200]:
    print(get_last_trade_price(i, "30JAN25", "C"))