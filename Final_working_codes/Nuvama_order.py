from APIConnect.APIConnect import APIConnect 
api_connect = APIConnect(
    "877nujhgiEqQhg",
    "74BjQ&3cylKWKot(",
    "613231fb2a539670",
    "python-settings.ini"
)
# https://www.nuvamawealth.com/api-connect/login?api_key=877nujhgiEqQhg
from constants.exchange import ExchangeEnum
from constants.order_type import OrderTypeEnum
from constants.product_code import ProductCodeENum
from constants.duration import DurationEnum
from constants.action import ActionEnum
# OPTIDX	NFO
response = api_connect.PlaceTrade(Trading_Symbol = "NIFTY25FEB21750CE", Exchange = ExchangeEnum.NFO, Action = ActionEnum.SELL, Duration = DurationEnum.DAY, Order_Type = OrderTypeEnum.MARKET, Quantity = 75, Streaming_Symbol = "NFO", Limit_Price = "0", Disclosed_Quantity="0", TriggerPrice="0", ProductCode = ProductCodeENum.MIS)
print(response) 

