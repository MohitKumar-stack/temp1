# import threading
import time as t
import pandas as pd
import time as t
import threading
import pytz
from decimal import Decimal
from datetime import datetime,timedelta
from pya3 import *
import ssl
import mysql.connector
from mysql.connector import Error
import json






ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone).time()
formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
current_time = datetime.strptime(formatted_time_ist, "%H:%M:%S").time()



# # Global variables
# x = 10
# run_fun2 = False  # Flag to control when `fun2()` starts running

# def fun1():
#     global x, run_fun2
#     if x > 1:
#         run_fun2 = True  # Start `fun2()` when the condition is met
#     # Other codes here
#     print("Running fun1")
#     time.sleep(1)  # Simulate processing time
#     return

# def fun2():
#     global x
#     while True:
#         if x < 2:
#             print("x is less than 2")
#         else:
#             print("Running fun2")
#         time.sleep(1)  # Simulate processing time

# # Start the main loop
# if __name__ == "__main__":
#     # Run `fun2` in a separate thread
#     threading.Thread(target=fun2, daemon=True).start()

#     while True:
#         fun1()
#      # `fun2()` runs in the background


dic={}
if dic:
    print("dic is not empty")
