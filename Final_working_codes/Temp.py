import mysql.connector
from mysql.connector import Error

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
                LTP_at_1230, LTP_at_1, LTP_at_115, LTP_at_130, nifty_open, yesterday_low)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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


# Example usage
save_trigger_data(
    nifty_price=19645.25, expiry_date="2023-01-05", option_type="CE", strike_rate=19700, 
    option_chain_price=210.50, LTP_at_930=205.00, LTP_at_10=208.00, LTP_at_1015=212.00, 
    LTP_at_1030=215.00, LTP_at_1230=220.00, LTP_at_1=225.00, LTP_at_115=230.00, 
    LTP_at_130=235.00, nifty_low=19595.75, nifty_high=19685.50, nifty_open=19650.00, 
    yesterday_low=19550.00
)
