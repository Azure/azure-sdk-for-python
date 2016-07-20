#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# This script creates the credentials_real.json file in the tests folder
# which is required when running live tests.

# You should create a new user with global admin rights in your AAD
# and pass that to this script, along with the password and subscription id.
# If you've just created the user, make sure to login using the portal first
# before using this script, because Azure requires you to create a new
# password on first login.

import argparse
import json
import os.path
import requests
import getpass

try:
    input = raw_input
except:
    pass


def get_token(username, password):
    #  the client id we can borrow from azure xplat cli
    client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
    grant_type = 'password'
    resource = 'https://management.core.windows.net/'
    token_url = 'https://login.windows.net/common/oauth2/token'

    payload = {
        'grant_type': grant_type,
        'client_id': client_id,
        'username': username,
        'password': password,
        'resource': resource,
    }
    response = requests.post(token_url, data=payload).json()
    return response['access_token']


front_url = "https://management.azure.com"
front_api_version = "2014-01-01"

def get_tenant_ids(auth_header):
    response = requests.get(
        "{}/tenants?api-version={}".format(front_url, front_api_version),
        headers={
            'Authorization': auth_header,
        }
    ).json()

    ids = [item['tenantId'] for item in response['value']]
    return ids


def get_subscription_ids(auth_header):
    response = requests.get(
        "{}/subscriptions?api-version={}".format(front_url, front_api_version),
        headers={
            'Authorization': auth_header,
        }
    ).json()

    ids = [item['subscriptionId'] for item in response['value']]
    return ids


def choose_subscription(auth_header):
    # TODO: this doesn't work, we'll need ADAL for this
    # tenants = get_tenant_ids(auth_header)
    # print('tenants: {}'.format(tenants))

    # subs = get_subscription_ids(auth_header)
    # print('subs: {}'.format(subs))

    # for now just ask the user to type it
    return input('Enter subscription id:')


def write_credentials_file(sub_id, token):
    folder = os.path.dirname(__file__)
    path = os.path.join(folder, 'credentials_real.json')
    credentials = {
        'subscriptionid': sub_id,
        'authorization_header': 'Bearer {}'.format(token),
    }

    with open(path, 'w') as f:
        f.write(json.dumps(credentials))

    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='User name. Ex: username@mylogin.onmicrosoft.com')
    parser.add_argument('-p', '--password', help='User password')
    parser.add_argument('-s', '--subscription', help='Subscription id. Ex: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    args = parser.parse_args()

    username = args.user
    password = args.password
    sub_id = args.subscription

    if not username:
        username = input('Enter username:')

    if not password:
        password = getpass.getpass('Enter password:')

    token = get_token(username, password)

    if not sub_id:
        auth_header = 'Bearer {}'.format(token)
        sub_id = choose_subscription(auth_header)

    creds_path = write_credentials_file(sub_id, token)
    print('Credentials written to {}'.format(creds_path))
