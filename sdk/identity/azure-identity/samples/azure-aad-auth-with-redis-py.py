# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""

This sample is intended to assist in authenticating with AAD via redis-py library. 
It focuses on displaying the logic required to fetch an AAD access token and to use it as password when setting up the redis client.

"""

import redis
from azure.identity import ClientSecretCredential
tenant_id = ""
client_id = ""
client_secret = ""
scope = "https://*.cacheinfra.windows.net:10225/appid/.default"
host = ""
port = 6379
user_name = ""

def hello_world():
    cred = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    token = cred.get_token(scope)
    r = redis.Redis(host=host, port=port, username=user_name, password=token.token, decode_responses=True)
    r.set("Az:key1", "value1")
    t = r.get("Az:key1")
    print(t)

def re_authentication():
    cred = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    token = cred.get_token(scope)
    r = redis.Redis(host=host, port=port, username=user_name, password=token.token, decode_responses=True)
    max_retry = 3
    for index in range(max_retry):
        try:
            r.set("Az:key1", "value1")
            t = r.get("Az:key1")
            print(t)
            break
        except redis.RedisError as ex:
            token = cred.get_token(scope)
            r = redis.Redis(host=host, port=port, username=user_name, password=token.token, decode_responses=True)

if __name__ == '__main__':
    hello_world()
    re_authentication()
