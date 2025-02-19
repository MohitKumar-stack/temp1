# from datetime import datetime, timedelta

# def get_expiry_date():
#     today = datetime.now().date()  # Get today's date
#     print("Today's Date:", today.strftime('%A, %d %b %Y'))  # Print today's date with the day
#     print("Weekday Number:", today.weekday())  # Print the numeric representation of the weekday (Monday = 0, Sunday = 6)

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
#         Nuvama_date = dt.strftime("%y%-m%d") if dt.month > 9 else dt.strftime("%y") + str(dt.month) + dt.strftime("%d")

#     print("Nuvama Date:", Nuvama_date)
# #     return formatted_date, Nuvama_date

# # # Run the function
# # get_expiry_date()

at_10 = {'Instrument': 'C', 'Quantity': 1}
at_1015 = {}
at_1030 = {'Instrument': 'P', 'Quantity': 1}
at_1 = {'Instrument': 'P', 'Quantity': 1}
at_115 = {}
at_130 = {'Instrument': 'C', 'Quantity': 1}

# # Dictionary mapping variable names to their values
# var_dict = {
#     "at_10": at_10,
#     "at_1015": at_1015,
#     "at_1030": at_1030,
#     "at_1": at_1,
#     "at_115": at_115,
#     "at_130": at_130
# }

# temp = []

# # Store variable names
# for var_name, var_value in var_dict.items():
#     if var_value and "Quantity" in var_value and var_value["Quantity"] > 0:
#         temp.append(var_name) 

# # for var_name, var_value in var_dict.items():
# #     if var_value["Quantity"] > 0:
# #         temp.append(var_name)  # Store the variable name as a string

# print("Temp list values are", temp)

# # Fetch values using variable names
# for name in temp:
#     if var_dict[name] and "Instrument" in var_dict[name]:  # Check if dict is not empty and key exists
#         print(var_dict[name]["Instrument"])

at_10 = {'Instrument': 'C', 'Quantity': 1}
at_1015 = {}
at_1030 = {'Instrument': 'C', 'Quantity': 1}
at_1 ={}
at_115 = {'Instrument': 'C', 'Quantity': 1}
at_130 = {'Instrument': 'C', 'Quantity': 1}

# Dictionary mapping variable names to values
var_dict = {
    "at_10": at_10,
    "at_1015": at_1015,
    "at_1030": at_1030,
    "at_1": at_1,
    "at_115": at_115,
    "at_130": at_130
}
ls=[at_10,at_1015,at_1030,at_1,at_115,at_130]

for i in ls:
    if i:
        print(i["Instrument"])
# Iterate through the list & check "Instrument"
# for name in ls:
#     if var_dict[name].get("Instrument") == "C":  # Use .get() to avoid KeyError
#         print(name)  # Print variable name if Instrument is "C"
