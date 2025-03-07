import hashlib
import requests
import json

#f
# login before run this code in alice blue web app
def key_genrater():
    # Input values
    user_id = "1721033"          # Replace with your UserId
    each_code = ""      # Replace with your Each Code
    api_key = "Z7PigAB8aqzbupeF32NaqM7DysmojljIUTK1754cb2M2vQLxePl0Rnscuz2p5uaaJPeXBJcVGQrHXENy1rB1sEEF7Yq0JZ02D8KkCcq5OlC3EknP6N0IkvzGo1DPbUas"          # Replace with your API Key
    #  code for opening each_code and URL
    # URL for the each_code API
    url = "https://ant.aliceblueonline.com/rest/AliceBlueAPIService/api/customer/getAPIEncpkey"
    # Payload with userId
    payload = json.dumps({
        "userId": user_id})
    # Headers
    headers = {
        'Content-Type': 'application/json'
    }
    # Sending the POST request
    response = requests.request("POST", url, headers=headers, data=payload)
    # Debugging: Print the raw response text
    #     # Parsing the JSON response
    try:
        response_json = response.json()  # Convert response text to JSON
        # Extract the `encKey` field if it exists
        enc_key = response_json.get("encKey")
        if enc_key:
            each_code=enc_key
        # else:
        #     print("Error: 'encKey' not found in the response.")
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON.")
    # Combine the values into a single string
    combined_string = f"{user_id}{api_key}{each_code}"
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    # Update the hash object with the combined string (encoded to bytes)
    sha256_hash.update(combined_string.encode('utf-8'))
    # Get the hexadecimal representation of the hash
    hash_digest = sha256_hash.hexdigest()
    #user data is hash id
    # userData=hash_digest
    # Print the result
    # print("Combined String:", combined_string)
    # print("SHA-256 Hash:", hash_digest)
    # Url for creating session id and code for activated session id 
    url = "https://ant.aliceblueonline.com/rest/AliceBlueAPIService/api/customer/getUserSID"
    payload = json.dumps({
    "userId": "1721033",
    "userData": hash_digest})
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return
    # print(response.text)
    # Before Createing New Session ID daily You need to create an
    #  Enc Key First then Hash that anf put into the User data 




# key_genrater()
# import hashlib

# api_key = "877nujhgiEqQhg"
# api_secret = "74BjQ&3cylKWKot("

# # Combine the keys
# data = api_key + api_secret

# # Generate a SHA-256 hash
# session_id = hashlib.sha256(data.encode()).hexdigest()[:16]  # Truncate to 16 characters

# print("Generated Session ID:", session_id)

