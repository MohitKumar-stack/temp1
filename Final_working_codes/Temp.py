from APIConnect.APIConnect import APIConnect
import json
nuvama_req_id ="326334c7d23caaaa"


api_connect = APIConnect(
    "877nujhgiEqQhg",
    "74BjQ&3cylKWKot(",
    nuvama_req_id,
    True,
    "/Users/mohitkumar/Downloads/Python Project/Final_working_codes/python-settings.ini"
)


# Extracting the "cshAvl" value from each JSON object
def quantity_calc():
    for json_obj in api_connect.Limits().strip().split("\n"):
        data = json.loads(json_obj)
        csh_avl = data["eq"]["data"]["cshAvl"]
        print(csh_avl)
        csh_avl=99960.00
        lot_size = 75.0  # Lot size
        lots = int(csh_avl // lot_size)
        lots_60 = int(lots * 0.6)
        lots_20 = int(lots * 0.2)
        lots_40 = int(lots * 0.4)  # Calculate number of lots
        print(f"Total Lots: {lots}")
        print(f"60% Lots: {lots_60}")
        print(f"20% Lots: {lots_20}")
        print(f"40% Lots: {lots_40}")

quantity_calc()