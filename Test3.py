import pandas as pd
import time as t
import pytz
from decimal import Decimal
from datetime import datetime,timedelta
from pya3 import *
import ssl


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
    return formatted_date

# Function to get strike prices (multiples of 50)
def get_strikes_and_expiry(LTP, option_type):  
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

    if option_type.upper() == 'CALL':
        print(f"CALL Strike Prices (5 forward): {forward_strikes}")
        return forward_strikes, expiry_date

    elif option_type.upper() == 'PUT':
        # print(f"PUT Strike Prices (5 backward): {backward_strikes}")
        return backward_strikes, expiry_date

    else:
        raise ValueError("Option type must be either 'CALL' or 'PUT'")
    


print(get_strikes_and_expiry(23700, 'CALL'))
