import requests
import time
from collections import defaultdict

import requests
from collections import defaultdict

# Your HubSpot API Key
HUBSPOT_API_KEY = "pat-na1-b1d4ba68-8d61-4618-ae01-6601edaa3064"

# API Headers
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

# Function to get all contacts
def get_all_contacts():
    url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=100&properties=email"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error fetching contacts: {response.text}")
        return []

# Function to find duplicate contacts by email
def find_duplicate_contacts():
    contacts = get_all_contacts()
    email_map = defaultdict(list)

    for contact in contacts:
        email = contact["properties"].get("email")
        if email:
            email_map[email].append(contact["id"])

    duplicates = {email: ids for email, ids in email_map.items() if len(ids) > 1}

    return duplicates

# Run the function and print duplicate contacts
duplicates = find_duplicate_contacts()

if duplicates:
    print("🚀 Duplicate Contacts Found:")
    for email, ids in duplicates.items():
        print(f"Email: {email} | Contact IDs: {ids}")
else:
    print("✅ No duplicate contacts found.")
