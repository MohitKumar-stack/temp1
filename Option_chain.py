import pandas as pd
from pya3 import *
import ssl
import json
import pandas as pd
import time as t
import pytz
from decimal import Decimal
from datetime import timedelta
from pya3 import *
import ssl


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

# Time intervals for logic implementation

strike_price,expiry_date=0,0

# investment_count = 0 this variable means how many times we have invested in the market on that day

# Calculate yesterday's date
# Function to get the upcoming Thursday as expiry date
def get_next_to_next_thursday():
    today = datetime.now().date()
    # Find the next Thursday (weekday 3 represents Thursday)
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead)
    # Add another 7 days to get the next-to-next Thursday
    next_to_next_thursday = next_thursday + timedelta(days=7)
    # Format the date as 'DDMMMYY'
    formatted_date = next_to_next_thursday.strftime('%d%b%y').upper()
    print("formatted_date",formatted_date)
    return formatted_date

# Function to get strike prices (multiples of 50)
def get_strikes_and_expiry(LTP, option_type):  
    ls=[]
    temp=0
    """
    Calculate 5 backward and 5 forward strike prices based on NIFTY price (LTP) 
    and return strike prices based on the option type.
    """
    expiry_date = get_next_to_next_thursday()  # Calculate the next-to-next expiry date (Thursday)

    # Find the nearest strike price multiple of 50
    nearest_strike = (LTP // 50) * 50

    # Generate a list of 5 backward and 5 forward strike prices
    backward_strikes = [nearest_strike - (i * 50) for i in range(1, 6)][::-1]  # 5 backward strikes
    forward_strikes = [nearest_strike + (i * 50) for i in range(1, 6)]  # 5 forward strikes

    if option_type.upper() == 'C':
        print(f"CALL Strike Prices (5 forward): {forward_strikes}")
        for i in forward_strikes:
            temp=get_last_trade_price(i, expiry_date,option_type)
            if 94<=float(temp)<=104:
                ls.append(temp)

    elif option_type.upper() == 'P':
        print(f"PUT Strike Prices (5 backward): {backward_strikes}")
        for i in forward_strikes:
            temp=(get_last_trade_price(i, expiry_date,option_type))
            if 94<=float(temp)<=104:
                ls.append(temp)
        
    else:
        raise ValueError("Option type must be either 'CALL' or 'PUT'")
    
    return ls, expiry_date,option_type
    





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
        t.sleep(0.1)

    # Subscribe to the instrument
    instrument = alice.get_instrument_by_symbol("NFO", f"NIFTY{expiry_date}{option_type}{strikes}")
    alice.subscribe([instrument])

    # Wait for the LTP to be received
    timeout = 0.1  # seconds
    start_time = t.time()
    while ltp is None and (t.time() - start_time) < timeout:
        t.sleep(0.1)

    # Unsubscribe and close the WebSocket

    if ltp is None:
        raise TimeoutError("Failed to receive LTP within the timeout period.")

    return ltp



