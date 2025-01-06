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
import logging
from order_trigger import place_order,sell_order
from key_generator import key_genrater  # for key_genrater function
from get_yesterday_low import yesterday_lowest_market_value  # for get_yesterday_low function


# Configure logging
# logging.basicConfig(level=logging.DEBUG)

# Call the key_genrater function to get the each_code
key_genrater()  # for key_genrater function
# Call the get_yesterday_low function to get the yesterday low

global yesterday_low
yesterday_low=yesterday_lowest_market_value()

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


# Time intervals for logic implementation


morning_start = datetime.strptime("09:00:00", "%H:%M:%S").time()
morning_end = datetime.strptime("12:00:00", "%H:%M:%S").time()
afternoon_start = datetime.strptime("12:01:00", "%H:%M:%S").time()
afternoon_end = datetime.strptime("15:31:00", "%H:%M:%S").time()


# Variables for specific LTP times
# global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1, LTP_at_115 ,LTP_at_130, nifty_low, nifty_high,nifty_open,nifty_price
# global strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality
strike_rate, expiry_date,option_type,option_chain_price=0,0,0,0
total_call_quality,total_put_quality=0,0
option_type =[]
LTP_at_930 = LTP_at_10 = LTP_at_1015 = LTP_at_1030 = LTP_at_1230 = LTP_at_1 = LTP_at_115 = LTP_at_130 = 0

# strike_rate,expiry_date,option_type,option_chain_price=0,0,0,0
nifty_low=0





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
    print("formatted_date",str(formatted_date))
    return formatted_date

# importenee function

def get_strikes_and_expiry(nifty_price, Instrument,order_value_checker,nifty_low,nifty_high,nifty_open): 
    print("get_strikes_and_expiry entered  ")

    global strike_rate,expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality
    # global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1, LTP_at_115 ,LTP_at_130
   
    if order_value_checker==0: #check for first time investement for the day (H1 or H2)
        ls=[]
        temp=0

        if option_chain_price==0 and strike_rate==0 and expiry_date==0:
            print("varied first if in get_strikes_and_expiry entered  ")
             # check expiry_date is blank or have values
            expiry_date = get_next_to_next_thursday()  # Calculate the next-to-next expiry date (Thursday)

            # Find the nearest strike price multiple of 50
            nearest_strike = (nifty_price // 50) * 50

            # Generate a list of 5 backward and 5 forward strike prices
            backward_strikes = [int(nearest_strike - (i * 50)) for i in range(1, 6)][::-1]  # 5 backward strikes as floats
            forward_strikes = [int(nearest_strike + (i * 50)) for i in range(1, 6)]  # 5 forward strikes as floats
            print("backward_strikes",backward_strikes)
            print("forward_strikes",forward_strikes)

            if Instrument == 'C':
                print(f"CALL Strike Prices (5 forward): {forward_strikes}")
                for i in forward_strikes:
                    temp=get_last_trade_price(i, expiry_date,Instrument)
                    # print(temp)
                    if 94<=temp<=104:
                        ls.append(temp)
                        option_chain_price=temp
                        option_type.append(Instrument)
                        if strike_rate==0:
                            strike_rate=i
                        break # break the loop after getting the first value
                    
            elif Instrument == 'P':
                print("varied first if in get_strikes_and_expiry entered  ")

                print(f"PUT Strike Prices (5 backward): {backward_strikes}")
                for i in forward_strikes:
                    temp=(get_last_trade_price(i, expiry_date,Instrument))
                    if 94<=float(temp)<=104:
                        ls.append(temp)
                        option_chain_price=temp
                        option_type.append(Instrument)
                        if strike_rate==0:
                            strike_rate=i
                        break # break the loop after getting the first value
    
        
            if len(ls)==0:
                if Instrument == 'C':
                    print(f"CALL Strike Prices (5 forward): {forward_strikes}")
                    for i in forward_strikes:
                        temp=get_last_trade_price(i, expiry_date,Instrument)
                        # print(temp)
                        if 91<=temp<=109:
                            ls.append(temp)
                            option_chain_price=temp
                            option_type.append(Instrument)
                            if strike_rate==0:
                                strike_rate=i
                            break # break the loop after getting the first value
                    
                elif Instrument == 'P':
                    print(f"PUT Strike Prices (5 backward): {backward_strikes}")
                    for i in forward_strikes:
                        temp=(get_last_trade_price(i, expiry_date,Instrument))
                        if 91<=float(temp)<=109:
                            ls.append(temp)
                            option_chain_price=temp
                            option_type.append(Instrument)
                            if strike_rate==0:
                                strike_rate=i
                            break # break the loop after getting the first value


            if len(ls)!=0:
                # trigger order place code
                if Instrument== 'C':
                    total_call_quality=600
                elif Instrument== 'P':
                    total_put_quality=600

                Quantity=600
                place_order(f"NIFTY{expiry_date}{Instrument}{strike_rate}",Quantity)  # call place_order function
                print("ALLL Success Full")
                save_trigger_data(
                    nifty_price=nifty_price, expiry_date=expiry_date, option_type=Instrument, strike_rate=strike_rate, 
                    option_chain_price=ls[0], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                    LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                    LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                    yesterday_low=yesterday_low
                )
                print("retun to nifty function back ")
                return None 
            

    if order_value_checker>0:
       # this function can be run on 15 min or 30 min condtions
        if option_chain_price!=0 and strike_rate!=0 and expiry_date!=0 and order_value_checker>0:
            Quantity=300
            print("enbtered in else condions of ")
            if Instrument== 'C':
                total_call_quality=total_call_quality+300
            elif Instrument== 'P':
                total_put_quality=total_put_quality+300

            place_order(f"NIFTY{expiry_date}{Instrument}{strike_rate}",Quantity)  # call place_order function
            print("ALLL Success Full")
            save_trigger_data(
                        nifty_price=nifty_price, expiry_date=expiry_date, option_type=Instrument, strike_rate=strike_rate, 
                        option_chain_price="0000", LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low
                    )
            return None


strike_rate=24000
expiry_date="16JAN25"
option_type=["C","P","C"]
total_call_quality=800
total_put_quality=300

# check profit all the time 

def profit_loss_tracker():
    global strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality

    if len(option_type)==1:    # for ideal condition 
        new_price=get_last_trade_price(strike_rate, expiry_date,option_type[0])
        if abs(new_price-option_chain_price)>=15:
                if option_type[0]=="C":
                    sell_order(f"NIFTY{expiry_date}{option_type[0]}{strike_rate}",total_call_quality)
                if option_type[0]=="P":
                   sell_order(f"NIFTY{expiry_date}{option_type[0]}{strike_rate}",total_put_quality)
    
    elif len(option_type)>1:
        if (current_time >= datetime.strptime("11:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("11:30:59", "%H:%M:%S").time())) or (current_time >= datetime.strptime("14:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("14:30:59", "%H:%M:%S").time())):
            unique_values = list(set(option_type))
            if len(unique_values)==1 and unique_values[0]=="C":
                sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
            elif len(unique_values)==1 and unique_values[0]=="P":
                sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)

            elif len(unique_values)==2:
                sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)
                return None

    return None
    


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
        t.sleep(0.2)

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

profit_loss_tracker()