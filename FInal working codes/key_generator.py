import hashlib
import requests
import json


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

# call the function 
key_genrater()

#eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIyam9lOFVScGxZU3FTcDB3RDNVemVBQkgxYkpmOE4wSDRDMGVVSWhXUVAwIn0.eyJleHAiOjE3NDAxOTY2MzMsImlhdCI6MTczNTAxMjYzMywianRpIjoiZDcxMzAyOTAtYjYwNS00YjQ5LWFjMTctOTE3NDhhNWI2YzZhIiwiaXNzIjoiaHR0cHM6Ly9pZGFhcy5hbGljZWJsdWVvbmxpbmUuY29tL2lkYWFzL3JlYWxtcy9BbGljZUJsdWUiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMGY2YzJiMmYtYTc4Yy00MTNiLWJlNWMtYzFlNmZhMDU5Yjg0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYWxpY2Uta2IiLCJzaWQiOiJlZTgwNDQyZS1mMWM1LTRkYmItYmE4Mi0xOWNhMTM0NzU4NTMiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDozMDAyIiwiaHR0cDovL2xvY2FsaG9zdDo1MDUwIiwiaHR0cDovL2xvY2FsaG9zdDo5OTQzIiwiaHR0cDovL2xvY2FsaG9zdDo5MDAwIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsImRlZmF1bHQtcm9sZXMtYWxpY2VibHVla2IiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFsaWNlLWtiIjp7InJvbGVzIjpbIkdVRVNUX1VTRVIiLCJBQ1RJVkVfVVNFUiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIG9wZW5pZCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJ1Y2MiOiIxNzIxMDMzIiwiY2xpZW50Um9sZSI6WyJHVUVTVF9VU0VSIiwiQUNUSVZFX1VTRVIiXSwibmFtZSI6Ik1PSElUIEtVTUFSIiwibW9iaWxlIjoiOTM4OTg4Mzk5MiIsInByZWZlcnJlZF91c2VybmFtZSI6IjE3MjEwMzMiLCJnaXZlbl9uYW1lIjoiTU9ISVQgS1VNQVIiLCJlbWFpbCI6Imt1bWFybW9oaXRzaDIxOEBnbWFpbC5jb20ifQ.AAq-0E8i7uQIXob_ODUo1pFa9KqE96FyRnfheokJRin4ucl1u3-rqNzAiXH2Y4bH3s8VuSBG4PVoQAshMLPJtmXBC9rW02_cVfZhOxUEL29Vuf7SgkmgA8H977ViTfbWA_XSRS6doP5pNy153xDzSD14l510952y0iqkW_sxNGbdwHkfIH-1JZKS2jaarLWLLsjn-hVAieFXGpmrJynKzyvN3ESbIPNFcaXobVxb2T0FIVz6UuIHBFqka8omAcwonxsC20DO6zbjesVsrzB1GDyBLayOOB6vTLs9vBAkGTWCgB_TU45k7_76VG2neOBDaZ5AifOzU9W-cH3qEzRclQ