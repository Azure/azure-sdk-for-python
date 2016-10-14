import requests

from requests_oauthlib import OAuth2Session
import oauthlib
from pprint import pprint

from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
from azure.common.credentials import UserPassCredentials

def callback(server, resource, scope):
    creds = UserPassCredentials('user', 'pass', verify=False, resource=resource, cached=False)
    token = creds.__dict__['token']['access_token']
    auth = (creds.scheme, token)
    print(auth)
    return auth

vault_name = 'keyvault-tjp'
client = KeyVaultClient(KeyVaultAuthentication(callback))
results = client.get_keys('https://{}.vault.azure.net'.format(vault_name))
pprint(results.next())