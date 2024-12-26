import pandas as pd

from datetime import datetime, timedelta
from pya3 import Aliceblue
import ssl
import os


# Ensure SSL is available
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

    # Set date range for fetching data (use datetime objects)
    from_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = (datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    exchange = "NSE"
    spot_symbol = "NIFTY 50"

    # Check if data for yesterday already exists in the CSV file
    yesterday_date_str = to_date.strftime('%Y-%m-%d')
    # Fetch historical data
    try:
        token = alice.get_instrument_by_symbol(exchange, spot_symbol)
        data = alice.get_historical(token, from_date, to_date, interval='1', indices=True)
        print("low values is ",min(data['low']))
        update_csv_with_yesterday_data(min(data['low']))
        # return (min(data['low']))
    
    except Exception as e:
        return 0
        


# check if the data is exist in the CSV file or not 
def analyze_csv():
    try:
        # Read the CSV file
        df = pd.read_csv("/Users/mohitkumar/Downloads/Php Project/yesterday_data.csv")
        yesterday = datetime.now() - timedelta(days=1)
    # Format the date if needed (e.g., for printing or API calls)
        yesterday_formatted = yesterday.strftime('%Y-%m-%d')
        
        # Check if yesterday was Saturday or Sunday
        if yesterday.strftime('%a') in ['Sat', 'Sun']:
            # If yes, move back to the last Friday
            days_to_subtract = (yesterday.weekday() - 4) % 7
            yesterday = yesterday - timedelta(days=days_to_subtract)

        # Format the date if needed
        yesterday_formatted = yesterday.strftime('%Y-%m-%d')
        # Check unique values and types for each column
        for col in df.columns:
            if col == "date":
    # Filter rows where the 'date' matches yesterday's formatted date
                yesterday_rows = df[df[col] == yesterday_formatted]
                if not yesterday_rows.empty:
                    # Find the minimum value in the 'low' column for the matching rows
                    float_value = yesterday_rows['low'].min()
                    print("Yesterday's lowest value is:", float_value)
                    return float_value

                else:
                    get_yesterday_low() # all the function to get the value of yesterday low

    except FileNotFoundError:
        pass


def update_csv_with_yesterday_data(yesterday_low_value):
    """
    Update the CSV file with yesterday's date and low value, replacing any existing data for that date.
    """
    try:
        # File path
        file_path = "/Users/mohitkumar/Downloads/Php Project/yesterday_data.csv"

        # Check if the file exists
        if os.path.exists(file_path):
            # Read the CSV file
            df = pd.read_csv(file_path)
        else:
            # Create an empty DataFrame if the file does not exist
            df = pd.DataFrame(columns=["date", "low"])

        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_formatted = yesterday.strftime('%Y-%m-%d')

        # Remove any existing rows with yesterday's date
        df = df[df["date"] != yesterday_formatted]

        # Add new row with yesterday's date and low value
        new_row = pd.DataFrame({"date": [yesterday_formatted], "low": [yesterday_low_value]})
        df = pd.concat([df, new_row], ignore_index=True)

        # Save the updated DataFrame back to the CSV
        df.to_csv(file_path, index=False)
        print(f"Replaced/Updated CSV with yesterday's data: {new_row.to_dict(orient='records')[0]}")
        analyze_csv()

    except Exception as e:
        return 0





# Call the function
# if __name__ == "__main__":
print(analyze_csv())
    
