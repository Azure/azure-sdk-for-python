# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""

This sample is intended to assist in authenticating with AAD via redis-py library. 
It focuses on displaying the logic required to fetch an AAD access token and to use it as password when setting up the redis client.

"""

import logging
import redis
from azure.identity import DefaultAzureCredential

scope = "https://*.cacheinfra.windows.net:10225/appid/.default"  # The scope will be changed for AAD Public Preview
host = ""  # Required
port = 6379  # Required
user_name = ""  # Required


def hello_world():
    cred = DefaultAzureCredential()
    token = cred.get_token(scope)
    r = redis.Redis(host=host,
                    port=port,
                    ssl=True,
                    username=user_name,
                    password=token.token,
                    decode_responses=True)
    r.set("Az:key1", "value1")
    t = r.get("Az:key1")
    print(t)


def re_authentication():
    _LOGGER = logging.getLogger(__name__)
    cred = DefaultAzureCredential()
    token = cred.get_token(scope)
    r = redis.Redis(host=host,
                    port=port,
                    ssl=True,
                    username=user_name,
                    password=token.token,
                    decode_responses=True)
    max_retry = 3
    for index in range(max_retry):
        try:
            r.set("Az:key1", "value1")
            t = r.get("Az:key1")
            print(t)
            break
        except redis.ConnectionError as ex:
            _LOGGER.info("Connection lost. Reconnecting.")
            token = cred.get_token(scope)
            r = redis.Redis(host=host,
                            port=port,
                            ssl=True,
                            username=user_name,
                            password=token.token,
                            decode_responses=True)
        except Exception:
            _LOGGER.info("Unknown failures.")
            break


if __name__ == '__main__':
    hello_world()
    re_authentication()
