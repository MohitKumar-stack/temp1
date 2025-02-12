import requests
import pandas as pd

# HubSpot API Key
API_KEY = "pat-na1-b1d4ba68-8d61-4618-ae01-6601edaa3064"

# HubSpot API URLs
MERGE_COMPANY_URL = "https://api.hubapi.com/crm/v3/objects/companies/merge"

# Read CSV file (Ensure it has 'Vid' and 'New Company Name' columns)
df = pd.read_csv("/Users/mohitkumar/Downloads/Php Project/Final_working_codes/hubspot_companies_filtered_duplicate.csv")

# Drop rows where 'Vid' or 'New Company Name' is missing
df = df.dropna(subset=["Vid"])

# Function to merge companies
def merge_companies(primary_id, secondary_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "primaryObjectId": primary_id,  # The first company ID
        "objectIdToMerge": secondary_id  # The second company ID to be merged
    }

    response = requests.post(MERGE_COMPANY_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Successfully merged {secondary_id} into {primary_id}")
    else:
        print(f"❌ Failed to merge {secondary_id}. Error: {response.text}")

# Function to process Vid and merge companies
def process_and_merge_companies():
    for _, row in df.iterrows():
        # Split Vid by '&' to get a list of company IDs
        company_ids = row["Vid"].split(" & ")

        # Merge the company IDs two by two
        for i in range(len(company_ids) - 1):
            primary_id = int(company_ids[i])  # First company ID
            secondary_id = int(company_ids[i + 1])  # Second company ID
            
            # Merge the companies
            merge_companies(primary_id, secondary_id)

print("✅ Starting company merge process...")
process_and_merge_companies()
print("✅ Company merge process completed.")
