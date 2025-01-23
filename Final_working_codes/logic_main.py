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

#global variable declarations
global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
global total_call_quality,total_put_quality,global_investment_checker,at_10,at_1015,at_1030,at_1,at_115,at_130

#global variable assignment
strike_rate, expiry_date,option_type,option_chain_price,total_call_quality,total_put_quality,global_investment_checker=0,0,0,0,0,0,0
LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130=0,0,0,0,0,0,0,0
option_type=[]
at_10,at_1015,at_1030,at_1,at_115,at_130=dict(),dict(),dict(),dict(),dict(),dict()



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
                print("value of temp",temp)
                if temp is not None:
                    if 93<=temp<=107.0:
                        print(f"Pirce for the strike - {i} is {temp} ")                        
                        result= {
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument
                        }
                        print("exit form valid_strike_rate funtion")
                        return result
                                               
                    
    elif Instrument == 'P':
            print(f"PUT Strike Prices (5 backward): {backward_strikes}")
            for i in backward_strikes:
                temp=(get_last_trade_price(i,expiry_date, Instrument))
                if temp is not None:
                     if 93.0<=temp<=107.0:
                        print(f"Pirce for the strike - {i} is {temp}")
                        result= {
                            "expiry_date":expiry_date,
                            "strike_rate":int(i),
                            "option_chain_price" :temp,
                            "Instrument":Instrument
                        }
                        print("exit form valid_strike_rate funtion")
                        return result
    try:
        if len(result==0):
            print("no result found")
        else:
            return result
    except:
        pass
    

def get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,Instrument):
   
    global global_investment_checker
            
    print("entetr into get_strikes_and_expiry")
    global at_10,at_1015,at_1030,at_1,at_115,at_130
    global at_10,at_1015,at_1030,option_type,total_call_quality,total_put_quality,expiry_date
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130

    current_time_ist = datetime.now(ist_timezone).time()
    formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
    current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()


    
   # at 10 AM conditions check and controller 
    if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:14:00", "%H:%M:%S").time()) and len(at_10)==0:     
            print("entered into at 10 condition")
            at_10=valid_strike_rate(nifty_price,Instrument)
            print("values which at_10 stored",at_10)
            if len(at_10)!=0:
                place_order(f"NIFTY{at_10['expiry_date']}{at_10['Instrument']}{at_10['strike_rate']}", 600)
                global_investment_checker=1
                at_10["Quantity"] = 600
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_10["expiry_date"], option_type=at_10["Instrument"], strike_rate=at_10["strike_rate"], 
                        option_chain_price=at_10["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back at 10")
                return
            else:
                return 
            



    # at 10:15 AM conditions check and controller 
    elif current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:19:00", "%H:%M:%S").time()) and len(at_1015)==0:
            print("entered into at 10:15 condition")

            at_1015=valid_strike_rate(nifty_price,Instrument)
            print("values which at_10:15 stored",at_1015)

            if len(at_1015)!=0:
                place_order(f"NIFTY{at_1015['expiry_date']}{at_1015['Instrument']}{at_1015['strike_rate']}", 200)  # call place_order function
                print("ALLL Success Full")
                at_1015["Quantity"] = 200
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_1015["expiry_date"], option_type=at_1015["Instrument"], strike_rate=at_1015["strike_rate"], 
                        option_chain_price=at_1015["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back at 10:15 ")
                return
            else:
                return 
            


    # at 10:30 AM conditions check and controller 
    elif current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("10:35:00", "%H:%M:%S").time()) and len(at_1030)==0:
            print("entered into at 10:30 condition ")
            if len(at_1015)!=0 and (at_1015["Instrument"]==Instrument): # put trigger at 15 and 30 and both are same
                Quantity=200
                at_1015["Quantity"] = at_1015["Quantity"] + 200 
                place_order(f"NIFTY{at_1015['expiry_date']}{at_1015['Instrument']}{at_1015['strike_rate']}", Quantity)  # call place_order function
                save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_1015["expiry_date"], option_type=at_1015["Instrument"], strike_rate=at_1015["strike_rate"], 
                            option_chain_price=at_1015["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                print("retun to nifty function back st 10:30")
                return

            elif len(at_1015)==0:
                if (at_10["Instrument"]==Instrument): # no trigger at 15 but call at 30 same at 10
                    print("values which at_10:30 stored same as 10 quantity increassed")
                    Quantity=200
                    at_10["Quantity"] = at_10["Quantity"] + 200 
                    place_order(f"NIFTY{at_10['expiry_date']}{at_10['Instrument']}{at_10['strike_rate']}", Quantity)  # call place_order function
                    print("ALLL Success Full")
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_10["expiry_date"], option_type=at_10["Instrument"], strike_rate=at_10["strike_rate"], 
                            option_chain_price=at_10["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    print("retun to nifty function back ")
                    return
                
                elif (at_10["Instrument"]!=Instrument):  # no trigger at 15 but put at 30 not same at 10
                    print("entered into  at_1030 condition")
                    at_1030=valid_strike_rate(nifty_price,Instrument)
                    at_1030["Quantity"] + 400 
                    print("values which aat_1030 stored",at_1030)
                    place_order(f"NIFTY{at_1030['expiry_date']}{at_1030['Instrument']}{at_1030['strike_rate']}", Quantity)  # call place_order function
                    print("ALLL Success Full")
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_1030["expiry_date"], option_type=at_1030["Instrument"], strike_rate=at_1030["strike_rate"], 
                            option_chain_price=at_1030["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    print("retun to nifty function back ")
                    return




   # at 1 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:05:00", "%H:%M:%S").time()) and len(at_1)==0:     
            print("entered into at 1 PM condition")
            at_1=valid_strike_rate(nifty_price,Instrument)
            print(at_1)
            if len(at_1)!=0:
                place_order(f"NIFTY{at_1['expiry_date']}{at_1['Instrument']}{at_1['strike_rate']}", 600)  # call place_order function
                global_investment_checker=1
                at_1["Quantity"] = 600 
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_1["expiry_date"], option_type=at_1["Instrument"], strike_rate=at_1["strike_rate"], 
                        option_chain_price=at_1["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back at 1 PM")
                return
            else:
                return 
            



    # at 1:15 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:20:00", "%H:%M:%S").time()) and len(at_115)==0:
            print("entered into at 1:15 condition")

            at_115=valid_strike_rate(nifty_price,Instrument)
            print(at_115)

            if len(at_115)!=0:
                place_order(f"NIFTY{at_115['expiry_date']}{at_115['Instrument']}{at_115['strike_rate']}", 200)  # call place_order function
                at_115["Quantity"] = 200 
                print("ALLL Success Full")
                save_trigger_data(
                        nifty_price=nifty_price, expiry_date=at_115["expiry_date"], option_type=at_115["Instrument"], strike_rate=at_115["strike_rate"], 
                        option_chain_price=at_115["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                        LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                        LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                        yesterday_low=yesterday_low)
                print("retun to nifty function back at 1:15 ")
                return
            else:
                return 




    # at 1:30 PM conditions check and controller 
    elif current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("13:35:00", "%H:%M:%S").time()) and len(at_130)==0:
            print("entered into at 1:30 condition ")
            if len(at_115)!=0 and (at_115["Instrument"]==Instrument): # put trigger at 15 and 30 and both are same
                Quantity=200
                at_115["Quantity"] = at_115["Quantity"] + 200 
                place_order(f"NIFTY{at_115['expiry_date']}{at_115['Instrument']}{at_115['strike_rate']}", Quantity)  # call place_order function
                save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_115["expiry_date"], option_type=at_115["Instrument"], strike_rate=at_115["strike_rate"], 
                            option_chain_price=at_115["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                print("retun to nifty function back at_115")
                return

            elif len(at_115)==0:
                if (at_1["Instrument"]==Instrument): # no trigger at 15 but call at 30 same at 1
                    print("values which at_1:30 stored same as 10 quantity increassed")
                    Quantity=200
                    at_1["Quantity"] = at_1["Quantity"] + 200 
                    place_order(f"NIFTY{at_1['expiry_date']}{at_1['Instrument']}{at_1['strike_rate']}", Quantity)  # call place_order function
                    print("ALLL Success Full")
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_1["expiry_date"], option_type=at_1["Instrument"], strike_rate=at_1["strike_rate"], 
                            option_chain_price=at_1["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    print("retun to nifty function back ")
                    return
                
                elif (at_1["Instrument"]!=Instrument):  # no trigger at 15 but put at 30 not same at 10
                    print("entered into  at_1030 condition")
                    at_130=valid_strike_rate(nifty_price,Instrument)
                    at_130["Quantity"] + 400 
                    print("values which aat_1030 stored",at_130)
                    place_order(f"NIFTY{at_130['expiry_date']}{at_130['Instrument']}{at_130['strike_rate']}", Quantity)  # call place_order function
                    print("ALLL Success Full")
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=at_130["expiry_date"], option_type=at_130["Instrument"], strike_rate=at_130["strike_rate"], 
                            option_chain_price=at_130["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    print("retun to nifty function back ")
                    return


# check profit all the time 

def profit_loss_tracker():
    print("entered profit_loss_tracker function")
    global LTP_at_930, LTP_at_10, LTP_at_1015, LTP_at_1030, LTP_at_1230, LTP_at_1,LTP_at_115, LTP_at_130
    global total_call_quality,total_put_quality,expiry_date
    global at_10,at_1015,at_1030,at_1,at_115,at_130

    current_time = datetime.strptime(datetime.now(ist_timezone).time().strftime("%H:%M:%S"), "%H:%M:%S").time()
    
    temp=[]
    unique_Instrument=[]
    # result= {
    #                         "expiry_date":expiry_date,
    #                         "strike_rate":int(i),
    #                         "option_chain_price" :temp,
    #                         "Quantity":Quantity,
    #                         "Instrument":Instrument
    
    #                     }
    
    # check what tiggers are done
    for i in [at_10,at_1015,at_1030,at_1,at_115,at_130]:
        if len(i)!=0:
            temp.append(i)
            unique_Instrument.append(i["Instrument"])
            if i["Instrument"]=="C":
                total_call_quality=total_call_quality+i["Quantity"]
            elif i["Instrument"]=="P":
                total_put_quality=total_put_quality+i["Quantity"]

    unique_Instrument=list(set(unique_Instrument))
    # sell conditon 1 check when target increase 14% and at 10 or 1 and at 1 and 1:30 same instityment hit:
    if len(unique_Instrument)==1:
            print("check for 14 percentage conditions")
            new_price=get_last_trade_price(temp[0]["strike_rate"],temp[0]["expiry_date"], temp[0]["Instrument"])
            if (new_price >= temp[0]["option_chain_price"] * 1.14):
                if unique_Instrument[0]=="C":
                    sell_order(f"NIFTY{temp[0]['expiry_date']}C{temp[0]['strike_rate']}",total_call_quality)
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=temp[0]["expiry_date"], option_type=temp[0]["Instrument"], strike_rate=temp[0]["strike_rate"], 
                            option_chain_price=temp[0]["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    at_10 = at_1015 = at_1030 = at_1 = at_115 = at_130 = {}
                    return
                elif unique_Instrument[0]=="P":
                    sell_order(f"NIFTY{temp[0]['expiry_date']}P{temp[0]['strike_rate']}",total_put_quality)
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=temp[0]["expiry_date"], option_type=temp[0]["Instrument"], strike_rate=temp[0]["strike_rate"], 
                            option_chain_price=temp[0]["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    at_10 = at_1015 = at_1030 = at_1 = at_115 = at_130 = {}
                    return

    elif (current_time >= datetime.strptime("11:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("11:31:59", "%H:%M:%S").time())) or (current_time >= datetime.strptime("14:30:00", "%H:%M:%S").time() and current_time <= (datetime.strptime("14:31:59", "%H:%M:%S").time())):
            for i in [at_10,at_1015,at_1030,at_1,at_115,at_130]:
                if len(i)!=0 and i["Instrument"]=="C":
                    sell_order(f"NIFTY{i[0]['expiry_date']}{i[0]['Instrument']}{i[0]['strike_rate']}",i[0]['Quantity'])
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=temp[0]["expiry_date"], option_type=temp[0]["Instrument"], strike_rate=temp[0]["strike_rate"], 
                            option_chain_price=temp[0]["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    at_10 = at_1015 = at_1030 = at_1 = at_115 = at_130 = {}
                    return
                
                elif len(i)!=0 and i["Instrument"]=="P":
                    sell_order(f"NIFTY{i[0]['expiry_date']}{i[0]['Instrument']}{i[0]['strike_rate']}",i[0]['Quantity'])
                    save_trigger_data(
                            nifty_price=nifty_price, expiry_date=temp[0]["expiry_date"], option_type=temp[0]["Instrument"], strike_rate=temp[0]["strike_rate"], 
                            option_chain_price=temp[0]["option_chain_price"], LTP_at_930=LTP_at_930, LTP_at_10=LTP_at_10, LTP_at_1015=LTP_at_1015, 
                            LTP_at_1030=LTP_at_1030, LTP_at_1230=LTP_at_1230, LTP_at_1=LTP_at_1, LTP_at_115=LTP_at_115, 
                            LTP_at_130=LTP_at_130, nifty_low = nifty_low, nifty_high=nifty_high, nifty_open=nifty_open, 
                            yesterday_low=yesterday_low)
                    at_10 = at_1015 = at_1030 = at_1 = at_115 = at_130 = {}
                    return

                      

# function to get the last trade price of option_chain


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
    global yesterday_low,yesterday_high

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
                print("No Investment As of Now")
        except:
            pass

        # LTP_at_930=23207.90
        # LTP_at_10=23312.25
        # LTP_at_1015=23660.65
        # LTP_at_1030=24964.75
        # nifty_open =23700.65
        # nifty_price =23688.95
        # nifty_high =23830.85
        # nifty_low =23636.15
        # LTP_at_1230=23012.25
        
       
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
    

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:14:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and len(at_10)==0:  #analyze_csv()) for getting last day low price
                print("H1 call morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')

    
    # condtion check at 10:15 AM CALL 
                    
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time():
            
            if (nifty_high- nifty_open) > 75.0  and (nifty_open- nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) > 0.0 and len(at_1015)==0 and len(at_10)!=0:
                pass 

            elif (nifty_high- nifty_open) > 75.0  and (nifty_open- nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1015 - LTP_at_10) < 5.0 and len(at_1015)==0 and len(at_10)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')   # buy put for safety guard
                # buy put at this conditons


    # condtion check at 10:30 AM CALL 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:34:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) > 75.0 and (nifty_open- nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) > 2.0 and len(at_1030)==0 and len(at_10)!=0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')
            
            elif (nifty_high - nifty_open) > 75.0 and (nifty_open- nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_10 - LTP_at_930) > 2.0 and (LTP_at_1030 - LTP_at_10) < 2.0 and len(at_1030)==0 and len(at_10)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')  # buy put for safety guard
                # buy put at this conditons
        
     


    # conditon check PUT morning time

        #condtion check at 10 AM PUT 

        if current_time >= datetime.strptime("10:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:14:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and len(at_10)==0:
                print("H1 put morning start-end time varifyed at 10 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 




        #condtion check at 10:15 AM PUT  
        
        if current_time >= datetime.strptime("10:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:19:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) < 0.0 and len(at_1015)==0 and len(at_10)!=0:
                    pass
                  
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1015 - LTP_at_10) > 5.0 and len(at_1015)==0 and len(at_10)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                    # buy put for safety guard

            #condtion check at 10:30 AM PUT  

       #condtion check at 10:30 AM PUT 

        if current_time >= datetime.strptime("10:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("10:34:00", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) < -2.0 and len(at_1030)==0 and len(at_10)!=0:
                print("H1 put morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
     
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_10 - LTP_at_930) < -2.0 and (LTP_at_1030 - LTP_at_10) < 0.0 and len(at_1030)==0 and len(at_10)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                # buy put for safety guard


 



    # afternoon conditions 

    # condtion check at 1 PM CALL 
        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:04:00", "%H:%M:%S").time():
            if  (nifty_high - nifty_open)> 75.0 and (nifty_open - nifty_low)< 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and len(at_1)==0:
                print("H1 call morning start-end time varifyed at 1 PM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 




    #condtion check at 1:15 PM CALl

        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:19:00", "%H:%M:%S").time() :
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_1 - LTP_at_115) > 0.0 and len(at_115)==0 and len(at_1)!=0:
                pass # no buing at this stage 
                # print("H1 call morning start-end time varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'C',strike_rate)
            elif (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1- LTP_at_1230) > 2.0 and (LTP_at_1 - LTP_at_115) < -5.0 and len(at_115)==0 and len(at_1)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
                # buy put for safety guard
                # buy put at this conditons


    #condtion check at 1:30 PM CALL 
                       
        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:34:00", "%H:%M:%S").time() :
            if (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) > 2.0 and len(at_130)==0 and len(at_1)!=0:
                print("H1 call morning start-end time varifyed at 10:30 AM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C') # 0 for strike rate 

            elif (nifty_high - nifty_open) > 75.0  and (nifty_open - nifty_low) < 75.0 and nifty_low > yesterday_low and (LTP_at_1 - LTP_at_1230) > 2.0 and (LTP_at_130- LTP_at_1) < -2.0 and len(at_130)==0 and len(at_1)!=0:
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
 #               buy put for safety guard
                # buy put at this conditons




    # conditions for put


        #condtion check at 1 PM PUT 

        if current_time >= datetime.strptime("13:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:05:01", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and len(at_1)==0:
                print("H2 put afternoon varifyed at 1 PM")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 




        #condtion check at 1:15 PM PUT 
        
        if current_time >= datetime.strptime("13:15:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:19:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0  and (LTP_at_1- LTP_at_1230) < -2.0 and (LTP_at_115- LTP_at_1) < 0.0 and len(at_115)==0 and len(at_1)!=0:
                pass # no buing at this point 
                #  print("H2 put afternoon varifyed at 1:15 PM")
                # get_strikes_and_expiry(nifty_price, 'P',strike_rate)       
            elif (nifty_high - nifty_open) < 75.0 and (nifty_open - nifty_low) >75.0 and (LTP_at_1- LTP_at_1230) < -2.0 and (LTP_at_115- LTP_at_1) > 5.0 and len(at_115)==0 and len(at_1)!=0:
                print("H1 put morning start-end time varifyed at 1:15 PM ")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                #   buy put for safety guard

        #ondtion check at 1:30 PM PUT 



        if current_time >= datetime.strptime("13:30:00", "%H:%M:%S").time() and current_time <= datetime.strptime("13:35:05", "%H:%M:%S").time():
            if (nifty_high - nifty_open) < 75.0 and (nifty_open- nifty_low) >75.0 and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) < -2.0 and len(at_130)==0 and len(at_1)!=0:
                print("H1 put morning start-end time varifyed at 1:30 PM level 1")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'P')# 0 for strike rate 
      
            elif(nifty_high - nifty_open) < 75.0 and (nifty_open- nifty_low) >75.0  and (LTP_at_1 - LTP_at_1230) < -2.0 and (LTP_at_130 - LTP_at_1) > 2.0 and len(at_130)==0 and len(at_1)!=0:
                print("H1 put morning start-end time varifyed at 1:30 PM level 2")
                get_strikes_and_expiry(nifty_open,nifty_price,nifty_low,nifty_high,'C')# 0 for strike rate 
                # buy put for safety guard

           
                   

    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")

# Fetch NIFTY data every 0.5 seconds
while True:
    fetch_nifty_data()
    t.sleep(0.5)

