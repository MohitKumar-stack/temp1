

from datetime import datetime,timedelta


# def get_expiry_date():
#     today = datetime.now().date()  # Get today's date
#     # print("Today's Date:", today.strftime('%A, %d %b %Y'))  # Print today's date with the day
#     # print("Weekday Number:", today.weekday())  # Print the numeric representation of the weekday (Monday = 0, Sunday = 6)

#     # Calculate how many days to add to reach next week's Thursday
#     # Thursday is weekday number 3
#     if today.weekday() <= 3:  # If today is before or on Thursday
#         days_until_next_thursday = (10 - today.weekday())  # Skip to next week's Thursday
#     else:  # If today is after Thursday
#         days_until_next_thursday = (3 - today.weekday() + 7)

#     next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday

#     # Format the date as 'DDMMMYY'
#     formatted_date = next_week_thursday.strftime('%d%b%y').upper()
#     print("Next Week's Thursday Date:", formatted_date)

#     # Check if the calculated Thursday is the last Thursday of the month
#     last_day_of_month = (next_week_thursday.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
#     last_thursday = last_day_of_month
#     while last_thursday.weekday() != 3:  # Find the last Thursday of the month
#         last_thursday -= timedelta(days=1)

#     # If the next week's Thursday is the last Thursday of the month, format differently
#     if next_week_thursday == last_thursday:
#         Nuvama_date = next_week_thursday.strftime("%d%b").upper()  # Format as DDMMM
#     else:
#         dt = datetime.strptime(formatted_date, "%d%b%y")
#         from calendar import monthrange

#         last_day = monthrange(next_week_thursday.year, next_week_thursday.month)[1]  # Get the last day of the month
#         last_thursday = max(
#             [day for day in range(last_day - 6, last_day + 1) if datetime(next_week_thursday.year, next_week_thursday.month, day).weekday() == 3]
#         )  # Find the last Thursday of the month

#         # Nuvama_date = "25" + next_week_thursday.strftime("%b").upper() if next_week_thursday.day == last_thursday else dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")

# print(get_expiry_date())





# Function to get the upcoming Thursday as expiry date
# def get_expiry_date():
#     today = datetime.now().date()  #

#     today ="2025-03-06"

#     print("Get today's date",today)

#     # Thursday is weekday number 3
#     if today.weekday() <= 3:  # If today is before or on Thursday
#         days_until_next_thursday = (10 - today.weekday())  # Skip to next week's Thursday
#     else:  # If today is after Thursday
#         days_until_next_thursday = (3 - today.weekday() + 7)

#     next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday

#     # Format the date as 'DDMMMYY'
#     formatted_date = next_week_thursday.strftime('%d%b%y').upper()
#     print("Next Week's Thursday Date:", formatted_date)

#     # nuvama date formated 
#     #25220
#     dt = datetime.strptime(formatted_date, "%d%b%y")
#     Nuvama_date = dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")


#     print("Nuvama Date:", Nuvama_date)
#     return formatted_date,Nuvama_date


# print(get_expiry_date())





from datetime import datetime, timedelta

def get_expiry_date():
    # today = datetime.now().date()  # Original line (commenting for manual testing)
    
    today = datetime.strptime("2025-02-24", "%Y-%m-%d").date()  # Convert string to date object

    print("Get today's date:", today)

    # Thursday is weekday number 3
    if today.weekday() <= 3:  # If today is before or on Thursday
        days_until_next_thursday = (10 - today.weekday())  # Skip to next week's Thursday
    else:  # If today is after Thursday
        days_until_next_thursday = (3 - today.weekday() + 7)

    next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday

    # Format the date as 'DDMMMYY'
    formatted_date = next_week_thursday.strftime('%d%b%y').upper()
    print("Next Week's Thursday Date:", formatted_date)

    # Nuvama date formatted 
    dt = datetime.strptime(formatted_date, "%d%b%y")
    Nuvama_date = dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")

    print("Nuvama Date:", Nuvama_date)
    return formatted_date, Nuvama_date

print(get_expiry_date())
