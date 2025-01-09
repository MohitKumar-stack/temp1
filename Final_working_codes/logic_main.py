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
from get_yesterday_high import yesterday_highest_market_value
# global strike_rate
# Configure logging
# logging.basicConfig(level=logging.DEBUG)

# Call the key_genrater function to get the each_code
key_genrater()  # for key_genrater function

# Call the get_yesterday_low function to get the yesterday low 
# Call the get_yesterday_high function to get the yesterday high 
global yesterday_low,yesterday_high
yesterday_low=yesterday_lowest_market_value()
yesterday_high=yesterday_highest_market_value()

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

global strike_rate, expiry_date,option_type
global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
global option_chain_price,total_call_quality,total_put_quality


strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality=0,0,0,0,0,0
LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130=0,0,0,0,0,0,0,0
option_type=[]
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
    # global strike_rate, expiry_date,option_type
    global strike_rate, expiry_date,option_type
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global option_chain_price,total_call_quality,total_put_quality
   
    ls=[]
    temp=0

    if order_value_checker==0: #check for first time investement for the day (H1 or H2)
        
        if len(option_type)==0 and strike_rate==0 and expiry_date==0:
            print("varied first if in get_strikes_and_expiry entered  ")
             # check expiry_date is blank or have values
            expiry_date = get_next_to_next_thursday()  # Calculate the next-to-next expiry date (Thursday)
            # expiry_date="16JAN25"
            # Find the nearest strike price multiple of 50
            nearest_strike = (nifty_price // 50) * 50

            # Generate a list of 5 backward and 5 forward strike prices
            backward_strikes = [int(nearest_strike - (i * 50)) for i in range(1, 6)][::-1]  # 5 backward strikes as floats
            forward_strikes = [int(nearest_strike + (i * 50)) for i in range(1, 6)]  # 5 forward strikes as floats
           

            if Instrument == 'C':
                print(f"CALL Strike Prices (5 forward): {forward_strikes}")
                for i in forward_strikes:
                    temp=get_last_trade_price(i,expiry_date,Instrument)
                    # print(temp)
                    if temp is not None:
                        if 94.0<=temp<=104.0:
                            ls.append(temp)
                            option_chain_price=temp
                            option_type.append(Instrument)
                            strike_rate=int(i)
                            break # break the loop after getting the first value
                    
            elif Instrument == 'P':
                print(f"PUT Strike Prices (5 backward): {backward_strikes}")
                for i in forward_strikes:
                    temp=(get_last_trade_price(i, expiry_date,Instrument))
                    if temp is not None:
                        if 94.0<=temp<=104.0:
                            ls.append(temp)
                            option_chain_price=temp
                            option_type.append(Instrument)
                            strike_rate=int(i)
                            break # break the loop after getting the first value
        
        
            if len(ls)==0:
                if Instrument == 'C':
                    print(f"CALL Strike Prices (5 forward): {forward_strikes}")
                    for i in forward_strikes:
                        temp=get_last_trade_price(i, expiry_date,Instrument)
                        if temp is not None:
                            if 91.0<=temp<=109.0:
                                ls.append(temp)
                                option_chain_price=temp
                                option_type.append(Instrument)
                                strike_rate=int(i)
                                break # break the loop after getting the first value
                    
                elif Instrument == 'P':
                    print(f"PUT Strike Prices (5 backward): {backward_strikes}")
                    for i in forward_strikes:
                        temp=(get_last_trade_price(i, expiry_date,Instrument))
                        if temp is not None:
                            if 91.0<=temp<=109.0:
                                ls.append(temp)
                                option_chain_price=temp
                                option_type.append(Instrument)
                                strike_rate=int(i)
                                break # break the loop after getting the first value

            if len(ls)==0:
                print("No Strike founc in that price range ")
            
            if len(ls)!=0:
                print(" Stike rate is " ,strike_rate)
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
                # global strike_rate,expiry_date,option_type
                # print(strike_rate)
                # print(expiry_date)
                # print(option_type)
                # print(len(option_type))
                print("retun to nifty function back ")
                return 
            

    if order_value_checker>0:
       # this function can be run on 15 min or 30 min condtions
        print("checking condiotn 2 time invest")
        print(strike_rate)
        print(len(option_type))

        if len(option_type)>=1 and strike_rate>0:
            Quantity=300
            print("enbtered in else condions of ")
            if Instrument=='C':
                total_call_quality=total_call_quality+300
            elif Instrument=='P':
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





# check profit all the time 

def profit_loss_tracker():
    global strike_rate, expiry_date,option_type
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global option_chain_price,total_call_quality,total_put_quality

    if len(option_type)==1: 
        try: # for ideal condition 
            new_price=get_last_trade_price(strike_rate,expiry_date,option_type[0])
            if abs(new_price-option_chain_price)>=15:
                    if option_type[0]=="C":
                        sell_order(f"NIFTY{expiry_date}{option_type[0]}{strike_rate}",total_call_quality)
                    if option_type[0]=="P":
                        sell_order(f"NIFTY{expiry_date}{option_type[0]}{strike_rate}",total_put_quality)

                    save_trigger_data(
                        nifty_price=nifty_price, expiry_date=expiry_date, option_type=Instrument, strike_rate=strike_rate, 
                        option_chain_price="0000", LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low
                    )
                    strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality=0,0,0,0,0,0
        except:
            return             
    
    elif len(option_type)>1:
        try:
            print("Enter into KHshcdi condions ")
            if (current_time >= datetime.strptime("11:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("11:30:59", "%H:%M:%S").time())) or (current_time >= datetime.strptime("14:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("14:30:59", "%H:%M:%S").time())):
                print("Enter into KHshcdi condions time also varied")
                unique_values = list(set(option_type))
                if len(unique_values)==1 and unique_values[0]=="C":
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                elif len(unique_values)==1 and unique_values[0]=="P":
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)

                elif len(unique_values)==2:
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality) 
                save_trigger_data(
                            nifty_price=nifty_price, expiry_date=expiry_date, option_type=Instrument, strike_rate=strike_rate, 
                            option_chain_price="0000", LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low
                        )
                strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality=0,0,0,0,0,0
                return
        except:
            pass    

    return
    






# function to get the last trade price of option_chain


def get_last_trade_price(strikes, expiry_date,option_type):
    try :
        # alice = Aliceblue("1721033", "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas")
        # alice.get_session_id()

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
        timeout = 3  # seconds
        start_time = t.time()
        while ltp is None and (t.time() - start_time) < timeout:
            t.sleep(0.1)

        # Unsubscribe and close the WebSocket

        if ltp is None:
            raise TimeoutError("Failed to receive LTP within the timeout period.")

        return float(ltp)
    
    except:
        return 



# Function to write key-value pairs to a database file
def save_trigger_data(
    nifty_price=0, expiry_date=0, option_type=0, strike_rate=0, 
    option_chain_price=0, LTP_at_930=0, LTP_at_10=0, LTP_at_1015=0, 
    LTP_at_1030=0, LTP_at_1230=0, LTP_at_1=0, LTP_at_115=0, 
    LTP_at_130=0, nifty_low=0, nifty_high=0, nifty_open=0, 
    yesterday_low=0, timestamp=None
):
    """
    Save the provided data into the 'trigger_data' table.

    Args:
        Provide arguments in the format of column names. Default values are 0.
    """
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(
            host='82.197.82.130',       # Access host
            port=3306,                  # Default MySQL port
            user='u791720918_mohit3',   # Replace with your database username
            password='sofwaq-fyctes-8gYvze',  # Replace with your database password
            database='u791720918_temp_stock'  # Replace with your database name
        )

        if connection.is_connected():
            # Default timestamp to the current time if not provided
            if timestamp is None:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Prepare the SQL query
            query = """
                INSERT INTO Triggers_data (timestamp, nifty_price, nifty_high, nifty_low, strike_rate,
                option_type, option_chain_price, LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030,
                LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130, nifty_open, yesterday_low,expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Collect the data in order
            data = (
                timestamp, nifty_price, nifty_high, nifty_low, strike_rate, 
                option_type, option_chain_price, LTP_at_930, LTP_at_10, LTP_at_1015, 
                LTP_at_1030, LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130, 
                nifty_open, yesterday_low,expiry_date
            )

            # Execute the query
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()  # Commit the transaction
            
            print(f"Data inserted successfully:")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

    finally:
        # Ensure the cursor and connection are closed
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()






# Fetch real-time data for NIFTY50 and implement logic
def fetch_nifty_data():
   # defining global variables  
    global strike_rate, expiry_date,option_type
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global option_chain_price,total_call_quality,total_put_quality
    global nifty_low, nifty_high,nifty_open,nifty_price
    
    # global strike_rate, expiry_date,option_type
    

  

    print("strike rate again fetch in fetch nifty funciton",strike_rate)
    if strike_rate>0:   #check for if any Buying happend or not and profit/Loss trakcer
        profit_loss_tracker()




    try:
        # Fetch data for NIFTY 50
        instrument = alice.get_instrument_by_symbol('NSE', 'NIFTY 50')
        nifty_data = alice.get_scrip_info(instrument)
        # Variables for specific LTP times
        global yesterday_low
        # print(" Yesterday low in Nifty function ",yesterday_low)
        # yesterday_low=yesterday_lowest_market_value()

         
        # Extract and safely convert values
        nifty_open = float(nifty_data.get('openPrice')) if nifty_data.get('openPrice') is not None else 0.0
        nifty_price = float(nifty_data.get('LTP')) if nifty_data.get('LTP') is not None else 0.0
        nifty_high = float(nifty_data.get('High')) if nifty_data.get('High') is not None else 0.0
        nifty_low = float(nifty_data.get('Low')) if nifty_data.get('Low') is not None else 0.0

      
        
        # Print data
        print(f"NIFTY50 - Open: {nifty_open}, LTP: {nifty_price}, High: {nifty_high}, Low: {nifty_low}")
        # print(type(nifty_price))
        # print(type(nifty_high))
        # print(type(nifty_low))
        # print(type(nifty_open))

        # current_time = datetime.now().time()

        current_time_ist = datetime.now(ist_timezone).time()
        formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
        current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()

        print(f"Current time: {current_time}")
        # print(type(current_time))

#  chcking price at specific time and showing it
        try:
            if current_time >= datetime.strptime("09:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("09:30:01", "%H:%M:%S").time()) and LTP_at_930 == 0:
                LTP_at_930 = nifty_price
            elif current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:00:01", "%H:%M:%S").time())   and LTP_at_10 == 0:  
                LTP_at_10 = nifty_price
            elif current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:15:01", "%H:%M:%S").time()) and LTP_at_1015 == 0:
                LTP_at_1015 = nifty_price
            elif current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:30:01", "%H:%M:%S").time()) and LTP_at_1030 == 0:
                LTP_at_1030 = nifty_price
            elif current_time >= datetime.strptime("12:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("12:30:01", "%H:%M:%S").time()) and LTP_at_1230 == 0:
                LTP_at_1230 = nifty_price
            elif current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <=(datetime.strptime("13:00:01", "%H:%M:%S").time()) and LTP_at_1 == 0:
                LTP_at_1 = nifty_price
            elif current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:15:01", "%H:%M:%S").time()) and LTP_at_115 == 0:
                LTP_at_115 = nifty_price    
            elif current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:30:01", "%H:%M:%S").time()) and LTP_at_130 == 0:
                LTP_at_130 = nifty_price

        except Exception as e:
            print(f"Error storing LTP values: {e}")

        # LTP_at_930=23638.45
        # LTP_at_10=23670.15
        # LTP_at_1015=22000
        # LTP_at_1030=23964.75
        # LTP_at_1230=23550.70
        # LTP_at_1=23536.70
        # nifty_open =23746.65
        # nifty_price =23688.95
        # nifty_high =23830.85
        # nifty_low =23736.15
        
        # print("strike rate",strike_rate)
        # print("option rate",option_type)
        print("at 9:30", LTP_at_930)
        print("at 10:00", LTP_at_10)
        print("at 10:15", LTP_at_1015)
        print("at 10:30", LTP_at_1030)
        print("at 12:30", LTP_at_1230)
        print("at 1:00", LTP_at_1)
        print("at 1:15", LTP_at_115)
        print("at 1:30", LTP_at_130)


    # morning conditions 

    # condtion check at 10 AM CALL 
    

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:00:01", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0:  #analyze_csv()) for getting last day low price
                print("H1 call morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_price,'C',0,nifty_low,nifty_high,nifty_open)

    
    # condtion check at 10:15 AM CALL 
                    
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:15:05", "%H:%M:%S").time():
            if (nifty_high- nifty_open) > 75.0  and (nifty_open- nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) > 0.0:
                pass # no action at this stage only buy put for safety
                # print("H1 call morning start-end time varifyed at 10:15 AM")
                # get_strikes_and_expiry(nifty_price, 'C',strike_rate)
            else:

                get_strikes_and_expiry(nifty_price,'P',1,nifty_low,nifty_high,nifty_open)   # buy put for safety guard
                # buy put at this conditons


    # condtion check at 10:30 AM CALL 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:30:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open- nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) > 2.0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'C',2,nifty_low,nifty_high,nifty_open)
            
            else:
                get_strikes_and_expiry(nifty_price,'P',2,nifty_low,nifty_high,nifty_open)  # buy put for safety guard
                # buy put at this conditons
        
     


    # conditon check PUT morning time

        #condtion check at 10 AM PUT 

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:00:01", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0:
                print("H1 put morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_price,'P',0,nifty_low,nifty_high,nifty_open)# 0 for strike rate 




        #condtion check at 10:15 AM PUT  
        
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:15:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) < -2.0 :
                    pass #no nuing at this point for now 
                    # print("H1 put morning start-end time varifyed at 10:15 AM")
                    # get_strikes_and_expiry(nifty_price, 'P',strike_rate)       
            else:
                get_strikes_and_expiry(nifty_price,'C',1,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                    # buy put for safety guard

            #condtion check at 10:30 AM PUT  



        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:30:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) < -2.0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'P',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
     
            else:
                get_strikes_and_expiry(nifty_price, 'C',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                # buy put for safety guard


 



    # afternoon conditions 

    # condtion check at 1 PM CALL 
        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:00:01", "%H:%M:%S").time():
            if  (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0:
                print("H1 call morning start-end time varifyed at 1 PM")
                get_strikes_and_expiry(nifty_price,'C',0,nifty_low,nifty_high,nifty_open)# 0 for strike rate 




    #condtion check at 1:15 PM CALl

        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:15:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_1 - LTP_at_115) > 0.0:
                pass # no buing at this stage 
                # print("H1 call morning start-end time varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'C',strike_rate)
            else:
                get_strikes_and_expiry(nifty_price,'P',1,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                # buy put for safety guard
                # buy put at this conditons


    #condtion check at 1:30 PM CALL 
                       
        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:30:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) > 2.0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'C',2,nifty_low,nifty_high,nifty_open) # 0 for strike rate 

            

            else:
                get_strikes_and_expiry(nifty_price,'P',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
 #               buy put for safety guard
                # buy put at this conditons




    # conditions for put


        #condtion check at 1 PM PUT 

        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:00:01", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1 - LTP_at_1230) < -2.0:
                print("H2 put afternoon varifyed at 1 PM")
                get_strikes_and_expiry(nifty_price, 'P',0,nifty_low,nifty_high,nifty_open)# 0 for strike rate 




        #condtion check at 1:15 PM PUT 
        
        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:15:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1- LTP_at_1230) < -2.0 and (LTP_at_115- LTP_at_1) < -2.0 :
                pass # no buing at this point 
                #  print("H2 put afternoon varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'P',strike_rate)       
            else:
                get_strikes_and_expiry(nifty_price, 'C',1,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                #   buy put for safety guard

        #ondtion check at 1:30 PM PUT 



        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:30:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open- nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) < -2.0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'P',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
      
            else:
                get_strikes_and_expiry(nifty_price,'C',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                # buy put for safety guard

           
                   

    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")

# Fetch NIFTY data every 5 seconds
while True:
    fetch_nifty_data()
    # t.sleep(0.5)

# for i in ["24000","23400","23500","24000","23400","23500"]:

#     print(get_last_trade_price(i, "16JAN25","C"))


# option_type=["C","C","P"]
# strike_rate=24000
# expiry_date="16JAN25"
# total_call_quality=600
# total_put_quality=600
# print(profit_loss_tracker())