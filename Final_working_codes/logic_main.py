import pandas as pd
import time as t
from pya3 import Aliceblue
import pytz
from datetime import datetime,timedelta
from pya3 import *
import ssl
import mysql.connector
from mysql.connector import Error
import json
from key_generator import key_genrater  # for key_genrater function
from get_yesterday_low import yesterday_lowest_market_value  # for get_yesterday_low function
from get_yesterday_high import yesterday_highest_market_value
from APIConnect.APIConnect import APIConnect 

nuvama_req_id ="346334f88d8d737f"


api_connect = APIConnect(
    "877nujhgiEqQhg",
    "74BjQ&3cylKWKot(",
    nuvama_req_id,
    True,
    "/Users/mohitkumar/Downloads/Python Project/Final_working_codes/python-settings.ini"
)

# https://www.nuvamawealth.com/api-connect/login?api_key=877nujhgiEqQhg

from constants.exchange import ExchangeEnum
from constants.order_type import OrderTypeEnum
from constants.product_code import ProductCodeENum
from constants.duration import DurationEnum
from constants.action import ActionEnum



# Previous Day Market Data  
yesterday_low, yesterday_high = 0, 0  

# Global Investment Checkers  
global_investment_checker, global_investment_checker_at_30 = 0, 0  

# LTP (Last Traded Price) for Different Time Intervals  
LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030 = 0, 0, 0, 0  
LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130 = 0, 0, 0, 0  

# Trade Data at Different Time Intervals (Stored as Dictionaries)  
at_10, at_1015, at_1030, at_1 = {}, {}, {}, {}  
at_115, at_130 = {}, {}  

# NIFTY Market Data  
nifty_open, nifty_low, nifty_high, nifty_price = 0, 0, 0, 0  




# for key_genrater function
key_genrater()  
# Call the get_yesterday_low function to get the yesterday low 
yesterday_low=yesterday_lowest_market_value()
# Call the get_yesterday_high function to get the yesterday high 
yesterday_high=yesterday_highest_market_value()


ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone).time()
formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()

# print(datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"))

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

Aliceblue(username, api_key).get_contract_master("NFO")

# global variable defining

def get_expiry_date():
    today = datetime.now().date()  # Get today's date
    print("Today's Date:", today.strftime('%A, %d %b %Y'))  # Print today's date with the day
    print("Weekday Number:", today.weekday())  # Print the numeric representation of the weekday (Monday = 0, Sunday = 6)

    # Calculate how many days to add to reach next week's Thursday
    # Thursday is weekday number 3
    if today.weekday() <= 3:  # If today is before or on Thursday
        days_until_next_thursday = (10 - today.weekday())  # Skip to next week's Thursday
    else:  # If today is after Thursday
        days_until_next_thursday = (3 - today.weekday() + 7)

    next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday

    # Format the date as 'DDMMMYY'
    formatted_date = next_week_thursday.strftime('%d%b%y').upper()
    print("Next Week's Thursday Date:", formatted_date)

    # Check if the calculated Thursday is the last Thursday of the month
    last_day_of_month = (next_week_thursday.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    last_thursday = last_day_of_month
    while last_thursday.weekday() != 3:  # Find the last Thursday of the month
        last_thursday -= timedelta(days=1)

    # If the next week's Thursday is the last Thursday of the month, format differently
    if next_week_thursday == last_thursday:
        Nuvama_date = next_week_thursday.strftime("%d%b").upper()  # Format as DDMMM
    else:
        dt = datetime.strptime(formatted_date, "%d%b%y")
        from calendar import monthrange

        last_day = monthrange(next_week_thursday.year, next_week_thursday.month)[1]  # Get the last day of the month
        last_thursday = max(
            [day for day in range(last_day - 6, last_day + 1) if datetime(next_week_thursday.year, next_week_thursday.month, day).weekday() == 3]
        )  # Find the last Thursday of the month

        Nuvama_date = "25" + next_week_thursday.strftime("%b").upper() if next_week_thursday.day == last_thursday else dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")
        
        # Nuvama_date = "25" + next_week_thursday.strftime("%b").upper() if next_week_thursday == last_thursday else dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")

        # Nuvama_date = dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")

    Nuvama_date="25FEB"
    print("Nuvama Date:", Nuvama_date)
    return formatted_date, Nuvama_date


def valid_strike_rate(nifty_price,Instrument):
    nearest_strike = (nifty_price // 50) * 50
    backward_strikes = [int(nearest_strike - (i * 50)) for i in range(1, 20)][::-1]  # 5 backward strikes as floats
    forward_strikes = [int(nearest_strike + (i * 50)) for i in range(1, 20)]  # 5 forward strikes as floats
    expiry_date,Nuvama_date= get_expiry_date() # call the function for get_expiry_date

    result = dict()
    if Instrument == 'C':
            print(f"CALL Strike Prices (5 forward): {forward_strikes}")
            for i in forward_strikes:
                temp=get_last_trade_price(i,expiry_date,Instrument)
                print("value of temp",temp)
                if temp is not None:
                    if 93.0<=temp<=107.0:
                        print(f"Pirce for the strike - {i} is {temp} ")                        
                        result= {
                            "trade_type":"Buy",
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument,
                            "Nuvama_date":Nuvama_date
                        }
                        # print("exit form valid_strike_rate funtion")
                        return result
                                               
                    
    elif Instrument == 'P':
            print(f"PUT Strike Prices (5 backward): {backward_strikes}")
            for i in backward_strikes:
                temp=(get_last_trade_price(i,expiry_date, Instrument))
                if temp is not None:
                     if 93.0<=temp<=107.0:
                        print(f"Pirce for the strike - {i} is {temp}")
                        result= {
                            "trade_type":"Buy",
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument,
                            "Nuvama_date":Nuvama_date
                        }
                        return result
    

def get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,Instrument):
   
    global global_investment_checker, global_investment_checker_at_30  

    # LTP (Last Traded Price) for Different Time Intervals  
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030  
    global LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130  

    # Trade Data at Different Time Intervals (Stored as Dictionaries)  
    global at_10, at_1015, at_1030, at_1  
    global at_115, at_130  

    # Previous Day Market Data  
    global yesterday_low, yesterday_high 

    current_time_ist = datetime.now(ist_timezone).time()
    formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
    current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()


    
   # at 10 AM conditions check and controller 
    if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:14:00", "%H:%M:%S").time()) and len(at_10)==0:     
            at_10=valid_strike_rate(nifty_price,Instrument)
            print(" values of at_10 dictonery after valid_strike_rate function",at_10)
            if at_10:
                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_10['Nuvama_date']}{at_10['strike_rate']}{at_10['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 600, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                at_10['Quantity'] = 600                
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_10["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_10["strike_rate"], instrument=at_10["Instrument"], option_chain_price=at_10["option_chain_price"], expiry_date=at_10["expiry_date"],Quantity=at_10["Quantity"])
                print("order place at 10'O clock values are",at_10)
                global_investment_checker=1
                return
            else:
                return


    # at 10:15 AM conditions check and controller 
    elif current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:19:00", "%H:%M:%S").time()) and len(at_1015)==0 and at_10["Instrument"]!=Instrument:
            at_1015=valid_strike_rate(nifty_price,Instrument)
            if at_1015:
                at_1015["Quantity"] = 200
                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_1015['Nuvama_date']}{at_1015['strike_rate']}{at_1015['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS)  
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_1015["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_1015["strike_rate"], instrument=at_1015["Instrument"], option_chain_price=at_1015["option_chain_price"], expiry_date=at_1015["expiry_date"],Quantity=200)
                print("order place at 10:15'O clock values are",at_1015)
                return
            else:
                return
            


    # at 10:30 AM conditions check and controller 
    elif current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:34:00", "%H:%M:%S").time()) and len(at_1030) == 0 and global_investment_checker_at_30==0 and len(at_10)!=0:
        if at_1015 and (at_1015["Instrument"]==Instrument): # put trigger at 15 and 30 and both are same
            at_1015["Quantity"] = at_1015["Quantity"] + 200 
            api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_1015['Nuvama_date']}{at_1015['strike_rate']}{at_1015['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
            save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_1015["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_1015["strike_rate"], instrument=at_1015["Instrument"], option_chain_price=at_1015["option_chain_price"], expiry_date=at_1015["expiry_date"],Quantity=200)
            global_investment_checker_at_30=1
            print("order place at 10:30'O clock level 1 values are",at_1015)
            return

        elif len(at_1015)==0:
            if at_10 and (at_10["Instrument"]==Instrument): # no trigger at 15 but call at 30 same at 10
                at_10["Quantity"] = at_10["Quantity"] + 200 
                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_10['Nuvama_date']}{at_10['strike_rate']}{at_10['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_10["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_10["strike_rate"], instrument=at_10["Instrument"], option_chain_price=at_10["option_chain_price"], expiry_date=at_10["expiry_date"],Quantity=200)
                global_investment_checker_at_30=1
                print("order place at 10:30'O clock level 2 values are",at_10)
                return
            
            elif len(at_10)!=0 and at_10["Instrument"]!=Instrument:   # no trigger at 15 but put at 30 not same at 10
                at_1030=valid_strike_rate(nifty_price,Instrument)
                if at_1030:
                    at_1030["Quantity"] = 400 
                    api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_1030['Nuvama_date']}{at_1030['strike_rate']}{at_1030['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 400, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                    save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_1030["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_1030["strike_rate"], instrument=at_1030["Instrument"], option_chain_price=at_1030["option_chain_price"], expiry_date=at_1030["expiry_date"],Quantity=400)
                    print("order place at 10:30'O clock level 3 values are",at_1030)
                    return
                else:
                    return





   # at 1 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:14:00", "%H:%M:%S").time()) and len(at_1)==0:     
            at_1=valid_strike_rate(nifty_price,Instrument)
            print("at 1 is",at_1)
            if at_1:
                at_1["Quantity"] = 600 
                print(api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_1['Nuvama_date']}{at_1['strike_rate']}{at_1['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 600, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS))
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_1["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_1["strike_rate"], instrument=at_1["Instrument"], option_chain_price=at_1["option_chain_price"], expiry_date=at_1["expiry_date"],Quantity=600)
                global_investment_checker=1
                return
            else:
                return 
            



    # at 1:15 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:20:00", "%H:%M:%S").time()) and len(at_115)==0 and at_1["Instrument"]!=Instrument:
            at_115=valid_strike_rate(nifty_price,Instrument)
            if at_115:
                at_115["Quantity"] = 200 
                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_115['Nuvama_date']}{at_115['strike_rate']}{at_115['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_115["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_115["strike_rate"], instrument=at_115["Instrument"], option_chain_price=at_115["option_chain_price"], expiry_date=at_115["expiry_date"],Quantity=200)
                return
            else:
                return 




    # at 1:30 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:35:00", "%H:%M:%S").time()) and len(at_130) == 0 and global_investment_checker_at_30==0 and len(at_1)!=0:
            if at_115 and (at_115["Instrument"]==Instrument): # put trigger at 15 and 30 and both are same
                at_115["Quantity"] = at_115["Quantity"] + 200 
                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_115['Nuvama_date']}{at_115['strike_rate']}{at_115['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_115["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_115["strike_rate"], instrument=at_115["Instrument"], option_chain_price=at_115["option_chain_price"], expiry_date=at_115["expiry_date"],Quantity=200)
                global_investment_checker_at_30=1
                return

            elif len(at_115)==0:
                if at_1 and (at_1["Instrument"]==Instrument): # no trigger at 15 but call at 30 same at 10                    
                    at_1["Quantity"] = at_1["Quantity"] + 200 
                    api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_1['Nuvama_date']}{at_1['strike_rate']}{at_1['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 200, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                    save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_1["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_1["strike_rate"], instrument=at_1["Instrument"], option_chain_price=at_1["option_chain_price"], expiry_date=at_1["expiry_date"],Quantity=200)
                    global_investment_checker_at_30=1
                    return
                
                elif at_1 and at_1["Instrument"]!=Instrument:   # no trigger at 15 but put at 30 not same at 10
                    at_130=valid_strike_rate(nifty_price,Instrument)
                    if at_130:
                        at_130["Quantity"] = 400 
                        api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{at_130['Nuvama_date']}{at_130['strike_rate']}{at_130['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.BUY, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 400, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                        save_market_data(Timestamp =datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type=at_130["trade_type"], nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=at_115["strike_rate"], instrument=at_130["Instrument"], option_chain_price=at_130["option_chain_price"], expiry_date=at_130["expiry_date"],Quantity=400)
                        global_investment_checker_at_30=1
                        return
                    else:
                        return



# check profit all the time 

def profit_loss_tracker():
    # print("entered profit_loss_tracker function")
    global global_investment_checker, global_investment_checker_at_30  

    # LTP (Last Traded Price) for Different Time Intervals  
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030  
    global LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130  

    # NIFTY Market Data  
    global nifty_open, nifty_low, nifty_high, nifty_price  

    # Trade Data at Different Time Intervals (Stored as Dictionaries)  
    global at_10, at_1015, at_1030, at_1  
    global at_115, at_130  

    # Previous Day Market Data  
    global yesterday_low, yesterday_high 

    current_time = datetime.strptime(datetime.now(ist_timezone).time().strftime("%H:%M:%S"), "%H:%M:%S").time()

    if ( 
        (
            current_time >= datetime.strptime("11:34:01", "%H:%M:%S").time() and current_time <= (datetime.strptime("11:40:01", "%H:%M:%S").time())

        ) or (
            current_time >= datetime.strptime("14:34:01", "%H:%M:%S").time() and current_time <= (datetime.strptime("14:40:01", "%H:%M:%S").time())
        )
    ):
            print("check for second selling type when 14 percentage conditions not meet ")
            # Iterate through the global dictionaries
            for i in [at_10,at_1015,at_1030,at_1,at_115,at_130]:
                # Check if dictionary is not empty and is a Call option
                if i and i["Instrument"] == "C":
                    api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{i['Nuvama_date']}{i['strike_rate']}{i['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = i["Quantity"], Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                    new_price=get_last_trade_price(i["strike_rate"],i["expiry_date"], i["Instrument"])
                    save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type="Sell", nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=i["strike_rate"], instrument=i["Instrument"], option_chain_price=i["option_chain_price"], expiry_date=i["expiry_date"],Quantity=i["Quantity"])
                
                # Check if dictionary is not empty and is a Put option
                elif i and i["Instrument"] == "P":
                    api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{i['Nuvama_date']}{i['strike_rate']}{i['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = i["Quantity"], Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                    new_price=get_last_trade_price(i["strike_rate"],i["expiry_date"], i["Instrument"])
                    save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type="Sell", nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=i["strike_rate"], instrument=i["Instrument"], option_chain_price=i["option_chain_price"], expiry_date=i["expiry_date"],Quantity=i["Quantity"])


            # Global Investment Cleaner  
            global_investment_checker, global_investment_checker_at_30 = 0, 0  

            # LTP (Last Traded Price) for Different Time Intervals  
            LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030 = 0, 0, 0, 0  
            LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130 = 0, 0, 0, 0  

            # Trade Data at Different Time Intervals (Stored as Dictionaries)  
            at_10, at_1015, at_1030, at_1 = {}, {}, {}, {}  
            at_115, at_130 = {}, {}  

                    

    else:
            temp_count = 0
            for i in [at_10,at_1]:
                if i:
                    new_price=get_last_trade_price(i["strike_rate"],i["expiry_date"], i["Instrument"])
                    if (new_price >= i["option_chain_price"] * 1.14):
                        api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{i['Nuvama_date']}{i['strike_rate']}{i['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = i["Quantity"], Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                        save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type="Sell", nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=i["strike_rate"], instrument=i["Instrument"], option_chain_price=i["option_chain_price"], expiry_date=i["expiry_date"],Quantity=i["Quantity"])
                        for j in [at_1015, at_1030, at_115, at_130]:
                            if j and j["Instrument"] == "C":
                                new_price=get_last_trade_price(j["strike_rate"],j["expiry_date"], j["Instrument"])
                                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{j['Nuvama_date']}{j['strike_rate']}{j['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = j["Quantity"], Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type="Sell", nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=j["strike_rate"], instrument=j["Instrument"], option_chain_price=j["option_chain_price"], expiry_date=j["expiry_date"],Quantity=j["Quantity"])
                               
                            # Check if dictionary is not empty and is a Put option
                            elif j and j["Instrument"] == "P":
                                new_price=get_last_trade_price(j["strike_rate"],j["expiry_date"], j["Instrument"])
                                api_connect.PlaceTrade(Trading_Symbol = f"NIFTY{j['Nuvama_date']}{j['strike_rate']}{j['Instrument']}E", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = j["Quantity"], Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS) 
                                save_market_data(Timestamp = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S"),trade_type="Sell", nifty_open=nifty_open, nifty_low=nifty_low, nifty_high=nifty_high, nifty_current=nifty_price, yesterday_low=yesterday_low, yesterday_high=yesterday_high, at_9_30=LTP_at_930,at_10_00=LTP_at_10, at_10_15=LTP_at_1015, at_10_30=LTP_at_1030, at_12_30=LTP_at_1230, at_1_00=LTP_at_1, at_1_15=LTP_at_115, at_1_30=LTP_at_130, strike=j["strike_rate"], instrument=j["Instrument"], option_chain_price=j["option_chain_price"], expiry_date=j["expiry_date"],Quantity=j["Quantity"])
                        
                        temp_count =temp_count+1
            if temp_count!=0:
                # Global Investment Cleaner  
                global_investment_checker, global_investment_checker_at_30 = 0, 0  

                # LTP (Last Traded Price) for Different Time Intervals  
                LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030 = 0, 0, 0, 0  
                LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130 = 0, 0, 0, 0  

                # Trade Data at Different Time Intervals (Stored as Dictionaries)  
                at_10, at_1015, at_1030, at_1 = {}, {}, {}, {}  
                at_115, at_130 = {}, {} 
                



# function to get the last trade price of option_chain
def get_last_trade_price(strikes, expiry_date, option_type):
    try:
        # Initialize AliceBlue session
        alice = Aliceblue("1721033", "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas")
        alice.get_session_id()

        ltp = None
        socket_opened = False
        websocket_active = False

        def socket_open():
            nonlocal socket_opened
            socket_opened = True
            # print("WebSocket connection opened.")

        def socket_close():
            nonlocal websocket_active
            websocket_active = False
            # print("WebSocket connection closed.")

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
        timeout = 1  # Maximum wait time
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
        ltp_timeout = 1 # Timeout for LTP
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
    
# Function to write key-value pairs to a database file
def save_market_data(
    Timestamp, trade_type, nifty_open, nifty_low, nifty_high, nifty_current,
    yesterday_low, yesterday_high, at_9_30, at_10_00, at_10_15, at_10_30,
    at_12_30, at_1_00, at_1_15, at_1_30, strike,
    instrument, option_chain_price, expiry_date,Quantity
):
    """
    Save the provided data into the 'market_data' table.

    Args:
        Provide all required values. Fields should be passed explicitly.
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
            # Prepare the SQL query
            query = """
                INSERT INTO market_data (
                   Timestamp, trade_type, nifty_open, nifty_low, nifty_high, nifty_current,
                    yesterday_low, yesterday_high, at_9_30, at_10_00, at_10_15, at_10_30,
                    at_12_30, at_1_00, at_1_15, at_1_30, strike,
                    instrument, option_chain_price, expiry_date ,Quantity
                ) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Collect the data in order
            data = (
                Timestamp, trade_type, nifty_open, nifty_low, nifty_high, nifty_current,
                yesterday_low, yesterday_high, at_9_30, at_10_00, at_10_15, at_10_30,
                at_12_30, at_1_00, at_1_15, at_1_30, strike,
                instrument, option_chain_price, expiry_date, Quantity
            )

            # Execute the query
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()  # Commit the transaction
            
            print("Data inserted successfully!")

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
    global global_investment_checker, global_investment_checker_at_30  

    # LTP (Last Traded Price) for Different Time Intervals  
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030  
    global LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130  

    # NIFTY Market Data  
    global nifty_open, nifty_low, nifty_high, nifty_price  

    # Trade Data at Different Time Intervals (Stored as Dictionaries)  
    global at_10, at_1015, at_1030, at_1  
    global at_115, at_130  

    # Previous Day Market Data  
    global yesterday_low, yesterday_high 

    try:
        # Fetch data for NIFTY 50
        instrument = alice.get_instrument_by_symbol('NSE', 'NIFTY 50')
        nifty_data = alice.get_scrip_info(instrument)  
        # Extract and safely convert values
        nifty_open = float(nifty_data.get('openPrice')) if nifty_data.get('openPrice') is not None else 0.0
        nifty_price = float(nifty_data.get('LTP')) if nifty_data.get('LTP') is not None else 0.0
        nifty_high = float(nifty_data.get('High')) if nifty_data.get('High') is not None else 0.0
        nifty_low = float(nifty_data.get('Low')) if nifty_data.get('Low') is not None else 0.0        
        # Print data
        print(f"NIFTY50 - Open: {nifty_open}, LTP: {nifty_price}, High: {nifty_high}, Low: {nifty_low}")
        current_time = datetime.strptime(datetime.now(ist_timezone).time().strftime("%H:%M:%S"), "%H:%M:%S").time()
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
        
        #investment checker
        try:
            if global_investment_checker==1:
                print("Investment Some Amount")
                profit_loss_tracker()
            else:
                t.sleep(0.3)
                print("No Investment As of Now")
        except:
            pass

        # LTP_at_930=22852.5
        # LTP_at_10=22955
        # LTP_at_1015=23260.65
        # LTP_at_1030=24964.75
        # nifty_open =23700.65
        # nifty_price =23688.95
        # nifty_high =23830.85
        # nifty_low =23656.15
        # # LTP_at_1230=22807.80
        # # LTP_at_1=22788.40
        # yesterday_high=23169.6
        # yesterday_low=22900.0
       
        print("at 9:30", LTP_at_930)
        print("at 10:00", LTP_at_10)
        print("at 10:15", LTP_at_1015)
        print("at 10:30", LTP_at_1030)
        print("at 12:30", LTP_at_1230)
        print("at 1:00", LTP_at_1)
        print("at 1:15", LTP_at_115)
        print("at 1:30", LTP_at_130)
        print("yesterday low", yesterday_low)
        print("yesterday high", yesterday_high)
       

    # morning conditions 

    # condtion check at 10 AM CALL 
        print(" values of at_10 dictonery IN NIFTY FUNCTION ",at_10)

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:14:00", "%H:%M:%S").time() and len(at_10)==0:
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0: 
                print("H1 call morning start-end time varifyed at 10 AM CALL")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')

    
    # condtion check at 10:15 AM CALL 
                    
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time() and len(at_1015)==0 and len(at_10)!=0:
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) > 0.0:
                pass 
            elif (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) <(-5.0):
                print("H1 call morning start-end time varifyed at 10:15 AM PUT")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')   # buy put for safety guard
                # buy put at this conditons


    # condtion check at 10:30 AM CALL 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:35:00", "%H:%M:%S").time() and len(at_10)!=0 and len(at_1030)==0 and global_investment_checker_at_30==0:
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) > 2.0:
                print("H1 call morning start-end time varifyed at 10:30 AM CALL")
                print("global_investment_checker_at_30 inside nifty function 1 is ",global_investment_checker_at_30)
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')
            
            elif (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) < 0.0:
                print("H1 call morning start-end time varifyed at 10:30 AM PUT")
                print("global_investment_checker_at_30 inside nifty function 2 is ",global_investment_checker_at_30)
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')  # buy put for safety guard
                # buy put at this conditons
        
     


    # conditon check PUT morning time

        #condtion check at 10 AM PUT 

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:14:00", "%H:%M:%S").time() and len(at_10)==0:
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 :
                print("H1 put morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 




        #condtion check at 10:15 AM PUT  
        
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time() and len(at_1015)==0 and len(at_10)!=0:
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) < 0.0 :
                    pass
                  
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) > 5.0 :
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                    # buy put for safety guard

            #condtion check at 10:30 AM PUT  

       #condtion check at 10:30 AM PUT 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:35:00", "%H:%M:%S").time() and global_investment_checker_at_30==0 and len(at_1030)==0 and len(at_10)!=0:
            if  (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and  (LTP_at_1030 - LTP_at_10) < -2.0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
     
            elif  (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) > 0.0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                # buy put for safety guard


 



    # afternoon conditions 

    # condtion check at 1 PM CALL 
        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:14:00", "%H:%M:%S").time() and len(at_1)==0:
            if  (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 :
                print("H1 call morning start-end time varifyed at 1 PM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 




    #condtion check at 1:15 PM CALl

        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:19:00", "%H:%M:%S").time() and len(at_115)==0 and len(at_1)!=0:
            if (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_115 - LTP_at_1) > 0.0:
                pass 
            elif (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_115 - LTP_at_1)< -5.0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
                # buy put for safety guard
                # buy put at this conditons



    #condtion check at 1:30 PM CALL 
                       
        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:34:00", "%H:%M:%S").time() and len(at_130)==0 and len(at_1)!=0 and global_investment_checker_at_30==0:
            if (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) > 2.0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C') # 0 for strike rate 

            elif (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) < 0.0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
 #               buy put for safety guard
                # buy put at this conditons




    # conditions for put


        #condtion check at 1 PM PUT 

        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:10:01", "%H:%M:%S").time() and len(at_1)==0:
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 :
                print("H2 put afternoon varifyed at 1 PM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 




        #condtion check at 1:15 PM PUT 
        
        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:19:05", "%H:%M:%S").time() and len(at_115)==0 and len(at_1)!=0:
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and  (LTP_at_115- LTP_at_1) < 0.0:
                pass       
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and  (LTP_at_115- LTP_at_1) > 5.0:
                print("H1 put morning start-end time varifyed at 1:15 PM ")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                #   buy put for safety guard

        #ondtion check at 1:30 PM PUT 



        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:35:05", "%H:%M:%S").time() and len(at_130)==0 and len(at_1)!=0 and global_investment_checker_at_30==0:
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) < -2.0:
                print("H1 put morning start-end time varifyed at 1:30 PM level 1")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
      
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) > 0.0:
                print("H1 put morning start-end time varifyed at 1:30 PM level 2")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                # buy put for safety guard


                    

    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")


if __name__ == "__main__":
    while True:
        fetch_nifty_data()


