import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import pandas as pd
from pya3 import Aliceblue
import ssl



def save_yesterday_low(date, low):
    connection = None  # Initialize connection as None
    cursor = None  # Initialize cursor as None
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
            # print("Successfully connected to the database")
            
            # Prepare the SQL query
            query = "INSERT INTO yesterday_low (date, low) VALUES (%s, %s)"
            data = (date, low)

            # Execute the query
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()  # Commit the transaction
            
            # print(f"Data inserted: Date={date}, Low={low}")

    except Error as e:
        pass
        # print(f"Error while connecting to MySQL: {e}")

    finally:
        # Close cursor and connection if they were initialized
        if cursor is not None:
            cursor.close()
            # print("Cursor closed.")
        if connection is not None and connection.is_connected():
            connection.close()
            get_low_for_yesterday_or_friday()
            # print("MySQL connection closed.")

# Example usage
# save_yesterday_low("2025-01-02", 3443.4)  # Replace with your actual date and low value






def get_low_for_yesterday_or_friday():
    connection = None  # Initialize connection as None
    cursor = None  # Initialize cursor as None
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
            # print("Successfully connected to the database")
            cursor = connection.cursor()

            # Get yesterday's date
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_date = yesterday.strftime('%Y-%m-%d')

            # Check if yesterday is a weekend (Saturday or Sunday)
            if yesterday.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
                # Get the previous Friday's date
                days_to_friday = yesterday.weekday() - 4
                friday_date = (yesterday - timedelta(days=days_to_friday)).strftime('%Y-%m-%d')
            else:
                friday_date = None  # Not a weekend, no need to check Friday

            # print("yesterday date",yesterday_date)

            # Prepare and execute the query for yesterday
            query = "SELECT low FROM yesterday_low WHERE date = %s"
            cursor.execute(query, (yesterday_date,))
            result = cursor.fetchone()

            # If yesterday's low is found, return it
            if result:
                # print(f"Low value found for {yesterday_date}: {result[0]}")
                return result[0]

            # If yesterday's low is not found, check Friday (if applicable)
            if friday_date:
                cursor.execute(query, (friday_date,))
                result = cursor.fetchone()
                if result:
                    # print(f"Low value found for {friday_date}: {result[0]}")
                    return result[0]

            # If neither date has a low value
            # print("get_yesterday_low trigger ")
            return get_yesterday_low()

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

    finally:
        # Close cursor and connection if they were initialized
        if cursor is not None:
            cursor.close()
            # print("Cursor closed.")
        if connection is not None and connection.is_connected():
            connection.close()
            # print("MySQL connection closed.")







# def get_yesterday_low():
#     # Verify SSL availability
#     try:
#         ssl.PROTOCOL_TLS
#     except AttributeError:
#         raise ImportError("SSL module is not available. Please ensure your Python environment supports SSL.")

#     # Credentials
#     username = "1721033"
#     api_key = "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas"

#     # Initialize Aliceblue session
#     try:
#         alice = Aliceblue(username, api_key)
#         session_id = alice.get_session_id().get('sessionID', None)
#     except Exception as e:
#         raise ConnectionError(f"Error initializing Aliceblue session: {e}")

#     # Set date range for fetching data (use datetime objects)
#     from_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#     to_date = (datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    

#     exchange = "NSE"
#     spot_symbol = "NIFTY 50"

#     # Check if data for yesterday already exists in the CSV file
#     yesterday_date_str = to_date.strftime('%Y-%m-%d')
#     # Fetch historical data
#     try:
#         token = alice.get_instrument_by_symbol(exchange, spot_symbol)
#         data = alice.get_historical(token, from_date, to_date, interval='1', indices=True)
#         # print("low values is ",min(data['low']))
#         # print("Go to update_csv_with_yesterday_data function  ")
#         yesterday_date = (datetime.now() - timedelta(days=1)).date()
#         # print(yesterday_date,min(data['low']))

#         # print("save_yesterday_low trigger ")

#         save_yesterday_low(yesterday_date,min(data['low']))
#         # return (min(data['low']))
    

#     except Exception as e:
#         return 0
    




from datetime import datetime, timedelta
import ssl


def get_yesterday_low():
    # Verify SSL availability
    try:
        ssl.PROTOCOL_TLS
    except AttributeError:
        raise ImportError("SSL module is not available. Please ensure your Python environment supports SSL.")

    # Credentials
    username = "1721033"
    api_key = "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas"

    # Initialize Aliceblue session
    try:
        alice = Aliceblue(username, api_key)
        session_id = alice.get_session_id().get('sessionID', None)
    except Exception as e:
        raise ConnectionError(f"Error initializing Aliceblue session: {e}")

    # Determine the correct date for fetching data
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    if yesterday.weekday() == 5:  # Saturday
        from_date = (yesterday - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = (yesterday - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif yesterday.weekday() == 6:  # Sunday
        from_date = (yesterday - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = (yesterday - timedelta(days=2)).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        from_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    exchange = "NSE"
    spot_symbol = "NIFTY 50"
    
    try:
        token = alice.get_instrument_by_symbol(exchange, spot_symbol)
        data = alice.get_historical(token, from_date, to_date, interval='1', indices=True)
        
        # Determine the correct date to save
        save_date = from_date.date()
        
        save_yesterday_low(save_date, min(data['low']))
    except Exception as e:
        return 0




def yesterday_lowest_market_value():
    t=get_low_for_yesterday_or_friday()
    temp=get_low_for_yesterday_or_friday()
    if temp is not None:
        return(temp)
    
# print(yesterday_lowest_market_value())