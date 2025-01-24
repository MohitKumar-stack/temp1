# from alice_blue import  TransactionType, OrderType, ProductType
import pandas as pd
from pya3 import *
import ssl
import time as t


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


def place_order(symbol,Quantity):
                order_check=(alice.place_order(transaction_type = TransactionType.Buy, 
                    instrument = alice.get_instrument_by_symbol("NFO", symbol), 
                    quantity = Quantity,
                    order_type = OrderType.Market, 
                    product_type = ProductType.Intraday))
                print(order_check)
                return "Success"



def sell_order(symbol,Quantity):
    order_check =alice.place_order(transaction_type = TransactionType.Sell, 
                            instrument = alice.get_instrument_by_symbol("NFO", symbol), 
                            quantity = Quantity,
                            order_type = OrderType.Market, 
                            product_type = ProductType.Intraday)
    print(order_check)
    return "Success"
    
    



# print(place_order("NIFTY30JAN25C24150",600))





