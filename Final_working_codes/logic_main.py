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
global global_investment_checker
global at_10,at_1015,at_1030,at_1,at_115,at_130
at_10,at_1015,at_1030,at_1,at_115,at_130,global_investment_checker=dict(),dict(),dict(),dict(),dict(),dict(),0





# Calculate yesterday's date

# Function to get the upcoming Thursday as expiry date
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



def valid_strike_rate(nifty_price,Instrument):
    print("enter int valid_strike_rate funtion")
    nearest_strike = (nifty_price // 50) * 50
    # Generate a list of 5 backward and 5 forward strike prices
    backward_strikes = [int(nearest_strike - (i * 50)) for i in range(1, 9)][::-1]  # 5 backward strikes as floats
    forward_strikes = [int(nearest_strike + (i * 50)) for i in range(1, 9)]  # 5 forward strikes as floats
    expiry_date= get_expiry_date() # call the function for get_expiry_date
    result = dict()
    if Instrument == 'C':
            print(f"CALL Strike Prices (5 forward): {forward_strikes}")
            for i in forward_strikes:
                temp=get_last_trade_price(i,expiry_date,Instrument)
                # print(temp)
                if temp is not None:
                    if 93.0<=temp<=107.0:
                        print(temp)
                        result= {
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument
                        }
                        print("exit form valid_strike_rate funtion",result)
                        break

                        
                    
    elif Instrument == 'P':
            print(f"PUT Strike Prices (5 backward): {backward_strikes}")
            for i in backward_strikes:
                temp=(get_last_trade_price(i,expiry_date, Instrument))
                if temp is not None:
                     if 93.0<=temp<=107.0:
                        print(temp)
                        result= {
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument
                        }
                        print("exit form valid_strike_rate funtion",result)
                        break
    if len(result==0):
        print("no result found")

    else:
        return result
    




def get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,Instrument):
    global global_investment_checker
    global_investment_checker==1
    
    print("entetr into get_strikes_and_expiry")
    global at_10,at_1015,at_1030,at_1,at_115,at_130
    global at_10,at_1015,at_1030,option_type,total_call_quality,total_put_quality,expiry_date
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130

    current_time_ist = datetime.now(ist_timezone).time()
    formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
    current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()
    print("len of at_10 ",len(at_10))
    if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:05:00", "%H:%M:%S").time()) and len(at_10)==0:     
            print("entered into at 10 condition")
            at_10=valid_strike_rate(nifty_price,Instrument)
            print(at_10)
            if len(at_10)!=0:
                place_order(f"NIFTY{at_10["expiry_date"]}{at_10["Instrument"]}{at_10["strike_rate"]}",600)  # call place_order function
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_10["expiry_date"], option_type=at_10["Instrument"], strike_rate=at_10["strike_rate"], 
                        option_chain_price=at_10["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back ")
            else:
                return 
            

    
    elif current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:20:00", "%H:%M:%S").time()) and len(at_1015)==0:
            print("entered into at 10:15 condition")

            at_1015=valid_strike_rate(nifty_price,Instrument)
            print(at_1015)

            if len(at_1015)!=0:
                place_order(f"NIFTY{at_1015["expiry_date"]}{at_1015["Instrument"]}{at_1015["strike_rate"]}",200) # call place_order function
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_10["expiry_date"], option_type=at_10["Instrument"], strike_rate=at_10["strike_rate"], 
                        option_chain_price=at_10["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back ")
            else:
                return 



    elif current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:35:00", "%H:%M:%S").time()) and len(at_1030)==0:
            print("entered into at 10:30 condition")
            at_1030=valid_strike_rate(nifty_price,Instrument)
            print(at_1030)
            tem=valid_strike_rate(nifty_price,Instrument)
            print(tem)
            Quantity=0
            if len(at_1030)!=0:
                if at_1030["Instrument"]==at_1015["Instrument"]:
                    Quantity=200
                else:
                    Quantity=400
                place_order(f"NIFTY{at_1030["expiry_date"]}{at_1030["Instrument"]}{at_1030["strike_rate"]}",Quantity) # call place_order function
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_10["expiry_date"], option_type=at_10["Instrument"], strike_rate=at_10["strike_rate"], 
                        option_chain_price=at_10["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back ")

            else:
                return 


# check profit all the time 

def profit_loss_tracker():
    global strike_rate, expiry_date,option_type
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global option_chain_price,total_call_quality,total_put_quality
    global at_10,at_1015,at_1030,at_1,at_115,at_130

    temp1=0

    unique_values = list(set(option_type))
    try:
    # check for at 11:30 and 2:30 conditions
        if (current_time >= datetime.strptime("11:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("11:30:59", "%H:%M:%S").time())) or (current_time >= datetime.strptime("14:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("14:30:59", "%H:%M:%S").time())):
            if len(unique_values)==1:
                if unique_values[0]=="C":
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                            
                if unique_values[0]=="P":
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)
                temp1=1
                            

            if len(unique_values)==2: 
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)
                    temp1=1
        

        if len(unique_values)==1:
            new_price=get_last_trade_price(strike_rate,expiry_date,unique_values[0])
            is_increased_by_14 = new_price >= option_chain_price * 1.14
            if is_increased_by_14 is True:
                if unique_values[0]=="C":
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                if unique_values[0]=="P":
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)
                temp1=1
        

        if len(unique_values)==2:
                new_price=get_last_trade_price(strike_rate,expiry_date,unique_values[0])
                is_increased_by_14 = new_price >= option_chain_price * 1.14
                if is_increased_by_14 is True:
                    sell_order(f"NIFTY{expiry_date}C{strike_rate}",total_call_quality)
                    sell_order(f"NIFTY{expiry_date}P{strike_rate}",total_put_quality)
                    temp1=1

        if temp1==1:
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
        return
            
    

# function to get the last trade price of option_chain


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
    global strike_rate, expiry_date,option_type,global_investment_checker
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global option_chain_price,total_call_quality,total_put_quality
    global nifty_low, nifty_high,nifty_open,nifty_price
    global at_10,at_1015,at_1030,at_1,at_115,at_130

    try:
        if global_investment_checker==1:
            print("INvested some amount")
            profit_loss_tracker()

        else:
            print("not Invested some amount")
    except:
        pass


    try:
        # Fetch data for NIFTY 50
        instrument = alice.get_instrument_by_symbol('NSE', 'NIFTY 50')
        nifty_data = alice.get_scrip_info(instrument)
        # Variables for specific LTP times
        global yesterday_low,yesterday_high
        # print(" Yesterday low in Nifty function ",yesterday_low)
        # yesterday_low=yesterday_lowest_market_value()

         
        # Extract and safely convert values
        nifty_open = float(nifty_data.get('openPrice')) if nifty_data.get('openPrice') is not None else 0.0
        nifty_price = float(nifty_data.get('LTP')) if nifty_data.get('LTP') is not None else 0.0
        nifty_high = float(nifty_data.get('High')) if nifty_data.get('High') is not None else 0.0
        nifty_low = float(nifty_data.get('Low')) if nifty_data.get('Low') is not None else 0.0        
        # Print data
        print(f"NIFTY50 - Open: {nifty_open}, LTP: {nifty_price}, High: {nifty_high}, Low: {nifty_low}")
    
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

        LTP_at_930=23518.90
        LTP_at_10=23669.65
        LTP_at_1015=24000
        LTP_at_1030=24964.75
        nifty_open =23700.65
        nifty_price =23688.95
        nifty_high =23830.85
        nifty_low =23636.15
        
       
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
    

        if current_time >= datetime.strptime("23:01:00", "%H:%M:%S").time() and current_time <= datetime.strptime("23:59:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and len(at_10)==0:  #analyze_csv()) for getting last day low price
                print("H1 call morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')

    
    # condtion check at 10:15 AM CALL 
                    
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time():
            
            if (nifty_high- nifty_open) > 75.0  and (nifty_open- nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) > 0.0 and len(at_1015)==0:
                pass 

            elif (nifty_high- nifty_open) > 75.0  and (nifty_open- nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) < 5.0 and len(at_1015)==0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')   # buy put for safety guard
                # buy put at this conditons


    # condtion check at 10:30 AM CALL 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:34:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open- nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) > 2.0 and len(at_1030)==0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')
            
            elif (nifty_high - nifty_open) > 75.0 and (nifty_open- nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) < 2.0 and len(at_1030)==0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')  # buy put for safety guard
                # buy put at this conditons
        
     


    # conditon check PUT morning time

        #condtion check at 10 AM PUT 

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:04:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0:
                print("H1 put morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 




        #condtion check at 10:15 AM PUT  
        
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) < 0.0 :
                    pass
                  
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) > 5.0 :
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                    # buy put for safety guard

            #condtion check at 10:30 AM PUT  



        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:34:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) < -2.0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
     
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) < 0.0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                # buy put for safety guard


 



    # afternoon conditions 

    # condtion check at 1 PM CALL 
        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:04:00", "%H:%M:%S").time():
            if  (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0:
                print("H1 call morning start-end time varifyed at 1 PM")
                get_strikes_and_expiry(nifty_price,'C',0,nifty_low,nifty_high,nifty_open)# 0 for strike rate 




    #condtion check at 1:15 PM CALl

        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:19:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_1 - LTP_at_115) > 0.0:
                pass # no buing at this stage 
                # print("H1 call morning start-end time varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'C',strike_rate)
            elif (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_1 - LTP_at_115) < -5.0:
                get_strikes_and_expiry(nifty_price,'P',1,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                # buy put for safety guard
                # buy put at this conditons


    #condtion check at 1:30 PM CALL 
                       
        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:34:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) > 2.0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'C',2,nifty_low,nifty_high,nifty_open) # 0 for strike rate 

            elif (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) < -2.0:
                get_strikes_and_expiry(nifty_price,'P',3,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
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
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1- LTP_at_1230) < -2.0 and (LTP_at_115- LTP_at_1) < 0.0 :
                pass # no buing at this point 
                #  print("H2 put afternoon varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'P',strike_rate)       
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1- LTP_at_1230) < -2.0 and (LTP_at_115- LTP_at_1) > 5.0 :
                get_strikes_and_expiry(nifty_price, 'C',1,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                #   buy put for safety guard

        #ondtion check at 1:30 PM PUT 



        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:30:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open- nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) < -2.0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_price,'P',2,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
      
            elif(nifty_high - nifty_open) < 75.0 and (nifty_open- nifty_low) >75.0 and nifty_high < yesterday_high and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) > 2.0:
                get_strikes_and_expiry(nifty_price,'C',3,nifty_low,nifty_high,nifty_open)# 0 for strike rate 
                # buy put for safety guard

           
                   

    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")

# Fetch NIFTY data every 0.5 seconds
while True:
    fetch_nifty_data()
    t.sleep(0.5)

