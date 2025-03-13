
from datetime import datetime,timedelta
def get_expiry_date():
    global formatted_date, Nuvama_date
    today = datetime.now().date() 
    
    # Thursday is weekday number 3
    if today.weekday() <= 3:  # If today is before or on Thursday
        days_until_next_thursday = (10 - today.weekday())  # Skip to next week's Thursday
    else:  # If today is after Thursday
        days_until_next_thursday = (3 - today.weekday() + 7)
    
    next_week_thursday = today + timedelta(days=days_until_next_thursday)  # Get next week's Thursday
    
    # Format the date as 'DDMMMYY'
    formatted_date = next_week_thursday.strftime('%d%b%y').upper()
    print("Next Week's Thursday Date:", formatted_date)
    
    dt = datetime.strptime(formatted_date, "%d%b%y")
    # print("dt:", dt.day)
    # Check if the day is 24 or later
    if dt.day >= 24:
        Nuvama_date = dt.strftime("%y%b").upper()  # Format as "YYMMM" only
    else:
        Nuvama_date = dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")
    
    return 

formatted_date, Nuvama_date= get_expiry_date()
print(formatted_date, Nuvama_date)