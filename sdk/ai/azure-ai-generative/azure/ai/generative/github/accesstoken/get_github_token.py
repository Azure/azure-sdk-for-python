# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import requests
import time

def get_github_token(client_id):
    device_url = 'https://github.com/login/device/code'
    data = {
        'client_id': client_id
    }
    headers = {'Accept': 'application/json'}
    response = requests.post(device_url, data=data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        device_code = response_json['device_code']
        user_code = response_json['user_code']
        verification_uri = response_json['verification_uri']

        print(f"Please visit {verification_uri} and enter code: {user_code}")

        # Prompt the user to press any key to continue
        input("After authorization, press Enter to continue...")

        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'client_id': client_id,
            'device_code': device_code           
        }
        
        while True:           
            token_response = requests.post(token_url, data=data)
            token_data = token_response.text
            result_dict = parse_string_to_dict(token_data)
    
            if 'access_token' in token_data:
                access_token = result_dict['access_token']
                print("Access Token:", access_token)
                return access_token
            elif 'error=authorization_pending' in token_data:
                error = result_dict['error']
                print(f"{error}")
                time.sleep(response_json['interval'])
            else:
                print("Failed to retrieve access token.")
                return None
    else:
        print("Failed to request device code.")

def parse_string_to_dict(token_text):
    pairs = token_text.split('&')
    result_dict = {}
    for pair in pairs:
        key, value = pair.split('=')
        result_dict[key] = value    
    return result_dict

    
# Replace 'YOUR_CLIENT_ID' with your GitHub app client ID
client_id = 'Iv1.92bc1d7e31af9373'
get_github_token(client_id)
