import pandas as pd
import time as t
import pytz
from decimal import Decimal
from datetime import datetime,timedelta
from pya3 import *
import ssl
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
print("yesterday low",yesterday_low)

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


morning_start = datetime.strptime("09:00:00", "%H:%M:%S").time()
morning_end = datetime.strptime("12:00:00", "%H:%M:%S").time()
afternoon_start = datetime.strptime("12:01:00", "%H:%M:%S").time()
afternoon_end = datetime.strptime("15:31:00", "%H:%M:%S").time()


# Variables for specific LTP times
global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1, LTP_at_130, nifty_low, nifty_high,nifty_open,nifty_price
LTP_at_930 = LTP_at_10 = LTP_at_1015 = LTP_at_1030 = LTP_at_1230 = LTP_at_1 = LTP_at_130 = 0


global invested_amount, total_money_for_investment, investment_count,strike_pices,expiry_date
invested_amount, initial_investment= 0, 100000
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
                ls.append(i)
                break # break the loop after getting the first value

    elif option_type.upper() == 'P':
        print(f"PUT Strike Prices (5 backward): {backward_strikes}")
        for i in forward_strikes:
            temp=(get_last_trade_price(i, expiry_date,option_type))
            if 94<=float(temp)<=104:
                ls.append(temp)
                ls.append(i)
                break # break the loop after getting the first value
        
    else:
        raise ValueError("Option type must be either 'CALL' or 'PUT'")
    
    write_to_csv(LTP=LTP, expiry_date=expiry_date, option_type=option_type,strike_price=ls[1],option_chain_price=ls[0],LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_130=LTP_at_130, nifty_low=nifty_low, nifty_high=nifty_high,nifty_open=nifty_open,nifty_price=nifty_price)
    # trigger order place code 
    print("Order status is :",place_order(f"NIFTY{expiry_date}{option_type}{ls[1]}"))
    return ls, expiry_date,option_type
    



# function to get the last trade price of option_chain


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



# Function to write key-value pairs to a CSV file
def write_to_csv(**kwargs):
    """
    Write key-value pairs to a CSV file. Keys become headers, and values become the row data.
    """
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{today_date}.csv"

    # Convert kwargs to lists for headers and values
    headers = list(kwargs.keys())
    values = list(kwargs.values())

    # Check if the file exists
    file_exists = os.path.exists(file_name)

    # Open the file in append or write mode as needed
    with open(file_name, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        
        # If the file doesn't exist, write the headers first
        if not file_exists:
            writer.writerow(headers)
        
        # Write the values as a new row
        writer.writerow(values)
    print(f"Data written to {file_name}: {kwargs}")
    return





# Fetch real-time data for NIFTY50 and implement logic
def fetch_nifty_data(checking_time):
    try:
        # Fetch data for NIFTY 50
        instrument = alice.get_instrument_by_symbol('NSE', 'NIFTY 50')
        nifty_data = alice.get_scrip_info(instrument)
        # Variables for specific LTP times
        global nifty_low, nifty_high,nifty_open,nifty_price
        # Extract and safely convert values
        nifty_open = Decimal(nifty_data.get('openPrice')) if nifty_data.get('openPrice') is not None else Decimal(0)
        nifty_price = Decimal(nifty_data.get('LTP')) if nifty_data.get('LTP') is not None else Decimal(0)
        nifty_high = Decimal(nifty_data.get('High')) if nifty_data.get('High') is not None else Decimal(0)
        nifty_low = Decimal(nifty_data.get('Low')) if nifty_data.get('Low') is not None else Decimal(0)
      
        
        # Print data
        print(f"NIFTY50 - Open: {nifty_open}, LTP: {nifty_price}, High: {nifty_high}, Low: {nifty_low}")

        # current_time = datetime.now().time()
        current_time = datetime.now().time()
        # Format the time as HH:MM:SS
        formatted_time = datetime.now().time().strftime("%H:%M:%S")
        # Convert formatted_time back to `datetime.time` for comparison
        current_time = datetime.strptime(datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S").time()
        # current_time = datetime.now().time()
        # current_time = datetime.now(ist_timezone).strftime("%H:%M")
        print(f"Current time: {current_time}")
        # print(type(current_time))
        global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1, LTP_at_130

#  chcking price at specific time and showing it
        try:
            if current_time >= datetime.strptime("09:30:00", "%H:%M:%S").time() and current_time < (datetime.strptime("09:30:01", "%H:%M:%S").time()) and LTP_at_930 == 0:
                LTP_at_930 = nifty_price
            elif current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time < (datetime.strptime("10:00:01", "%H:%M:%S").time())   and LTP_at_10 == 0:  
                LTP_at_10 = nifty_price
            elif current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time < (datetime.strptime("10:15:01", "%H:%M:%S").time()) and LTP_at_1015 == 0:
                LTP_at_1015 = nifty_price
            elif current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time < (datetime.strptime("10:30:01", "%H:%M:%S").time()) and LTP_at_1030 == 0:
                LTP_at_1030 = nifty_price
            elif current_time >= datetime.strptime("12:30:00", "%H:%M:%S").time() and current_time < (datetime.strptime("12:30:01", "%H:%M:%S").time()) and LTP_at_1230 == 0:
                LTP_at_1230 = nifty_price
            elif current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time < (datetime.strptime("13:00:01", "%H:%M:%S").time()) and LTP_at_1 == 0:
                LTP_at_1 = nifty_price
            elif current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time < (datetime.strptime("13:30:01", "%H:%M:%S").time()) and LTP_at_130 == 0:
                LTP_at_130 = nifty_price

        except Exception as e:
            print(f"Error storing LTP values: {e}")
        
        print("at 9:30", LTP_at_930)
        print("at 10:00", LTP_at_10)
        print("at 10:15", LTP_at_1015)
        print("at 10:30", LTP_at_1030)
        print("at 12:30", LTP_at_1230)
        print("at 1:00", LTP_at_1)
        print("at 1:30", LTP_at_130)


        if checking_time==0: # 0 for morning time first level checking
            #  check H1 Condtions 
            if morning_start <= current_time <= morning_end:
                print("morning H1 Conditions  start analysing")
                print("yesterday low",yesterday_low)
                #  check for H1 call conditions
    
                if (Decimal(nifty_high) - Decimal(nifty_open) > 75) and (Decimal(nifty_open) - Decimal(nifty_low)) < 75 and Decimal(nifty_low) > Decimal(yesterday_low) and (LTP_at_10 - LTP_at_930) > 5:
                    print("H1 call morning start-end time varifyed at 10 AM")
                    get_strikes_and_expiry(nifty_price, 'C', investment_count=1)

                    
                    # check for 10:15 AM condtion if true then Buy more call else but PUT
                    if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time():
                        if (Decimal(nifty_high) - Decimal(nifty_open) > 75) and (Decimal(nifty_open) - Decimal(nifty_low)) < 75 and Decimal(nifty_low) > Decimal(yesterday_low) and (LTP_at_10 - LTP_at_930) > 5 and (LTP_at_1015 - LTP_at_10) > 0:
                            print("H1 call morning start-end time varifyed at 10:15 AM")
                            get_strikes_and_expiry(nifty_price, 'C', investment_count=1)
                        else:
                            print("H1 call morning start-end time not varifyed at 10:15 AM")
                            # buy put at this conditons

                    # check for 10:30 AM condtion if true then Buy more call else but PUT
        
                    if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time():
                            if (Decimal(nifty_high) - Decimal(nifty_open) > 75) and (Decimal(nifty_open) - Decimal(nifty_low)) < 75 and Decimal(nifty_low) > Decimal(yesterday_low) and (LTP_at_10 - LTP_at_930) > 5 and (LTP_at_1015 - LTP_at_10) > 0 and (LTP_at_1030 - LTP_at_10) > 3:
                                print("H1 call morning start-end time varifyed at 10:30 AM")
                                get_strikes_and_expiry(nifty_price, 'C', investment_count=1)

                            else:
                                print("H1 call morning start-end time not varifyed at 10:30 AM")    
                                # buy put at this conditons



                       

                # check for H1 put conditions

                elif (Decimal(nifty_high) - Decimal(nifty_open) < 75) and (Decimal(nifty_open) - Decimal(nifty_low)) >75 and (LTP_at_10 - LTP_at_930) < 5:
                        print("H1 put morning start-end time varifyed at 10 AM")
                        get_strikes_and_expiry(nifty_price, 'C', investment_count=1)
   
                        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and (Decimal(nifty_high) - Decimal(nifty_open) < 75) and (Decimal(nifty_open) - Decimal(nifty_low)) >75 and (LTP_at_10 - LTP_at_930) < 5 and (LTP_at_1030 - LTP_at_10) > 3:
                            print("H1 put morning start-end time varifyed at 10:30 AM")
                            get_strikes_and_expiry(nifty_price, 'C', investment_count=2)

                        else:
                            print("H1 put morning start-end time not varifyed at 10:30 AM")
                            # buy call at this conditons    






            #  check H2 Condtions afternoon  
            elif afternoon_start <= current_time <= afternoon_end:
                print("H2  afternoon Conditions  start analysing")
                print("yesterday low",yesterday_low)
                #  check for H2 call conditions
                if (Decimal(nifty_high) - Decimal(nifty_open) > 75) and (Decimal(nifty_open) - Decimal(nifty_low)) < 75 and (LTP_at_1 - LTP_at_1230) > 5:
                    print("H2 Call condition satisfy at 1 PM")
                    get_strikes_and_expiry(nifty_price, 'C', investment_count=1)

                    # check for 1:30 PM condtion if true then Buy more call else but PUT
                    if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and (Decimal(nifty_high) - Decimal(nifty_open) > 75) and (Decimal(nifty_open) - Decimal(nifty_low)) < 75 and (LTP_at_1 - LTP_at_1230) > 5 and (LTP_at_130 - LTP_at_1) < 0:
                        print("H2 Call condition satisfy at 1:30 PM")
                        get_strikes_and_expiry(nifty_price, 'C', investment_count=2)

                    else:
                        print("H2 Call condition not satisfy at 1:30 PM")
                        # buy put at this conditons    



                #  check for H2 PUT conditions
                elif (Decimal(nifty_open) - Decimal(nifty_low) < 75) and (Decimal(nifty_open) - Decimal(nifty_high)) > 75 and (LTP_at_1 - LTP_at_1230) < -5:
                    print("H2 PUT condition satisfy at 1 PM")
                    get_strikes_and_expiry(nifty_price, 'C', investment_count=1)
                    if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and (Decimal(nifty_open) - Decimal(nifty_low) < 75) and (Decimal(nifty_open) - Decimal(nifty_high)) > 75 and (LTP_at_1 - LTP_at_1230) < -5 and (LTP_at_130 - LTP_at_1) < -3:
                        print("H2 PUT condition satisfy at 1:30 PM")
                        get_strikes_and_expiry(nifty_price, 'C', investment_count=2)

                    else:
                        print("H2 PUT condition not satisfy at 1:30 PM")
                        # buy call at this conditons    
                   

    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")

# Fetch NIFTY data every 5 seconds
while True:
    fetch_nifty_data(checking_time=0) # checking_type=0 means first level of algo checking
    t.sleep(0.5)



# Final_working_codes/logic_main.py