# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""

This sample is intended to assist in authenticating with AAD via redis-py library. 
It focuses on displaying the logic required to fetch an AAD access token and to use it as password when setting up the redis client.

"""

import time
import logging
import redis
from azure.identity import DefaultAzureCredential

scope = "acca5fbb-b7e4-4009-81f1-37e38fd66d78/.default"  # The current scope is for public preview and may change for GA release.
host = ""  # Required
port = 6380  # Required
user_name = ""  # Required


def hello_world():
    cred = DefaultAzureCredential()
    token = cred.get_token(scope)
    r = redis.Redis(
        host=host,
        port=port,
        ssl=True,  # ssl connection is required.
        username=user_name,
        password=token.token,
        decode_responses=True,
    )
    r.set("Az:key1", "value1")
    t = r.get("Az:key1")
    print(t)


def re_authentication():
    _LOGGER = logging.getLogger(__name__)
    cred = DefaultAzureCredential()
    token = cred.get_token(scope)
    r = redis.Redis(
        host=host,
        port=port,
        ssl=True,  # ssl connection is required.
        username=user_name,
        password=token.token,
        decode_responses=True,
    )
    max_retry = 3
    for index in range(max_retry):
        try:
            if _need_refreshing(token):
                _LOGGER.info("Refreshing token...")
                tmp_token = cred.get_token(scope)
                if tmp_token:
                    token = tmp_token
                r.execute_command("AUTH", user_name, token.token)
            r.set("Az:key1", "value1")
            t = r.get("Az:key1")
            print(t)
            break
        except redis.ConnectionError:
            _LOGGER.info("Connection lost. Reconnecting.")
            token = cred.get_token(scope)
            r = redis.Redis(
                host=host,
                port=port,
                ssl=True,  # ssl connection is required.
                username=user_name,
                password=token.token,
                decode_responses=True,
            )
        except Exception:
            _LOGGER.info("Unknown failures.")
            break


def _need_refreshing(token, refresh_offset=300):
    return not token or token.expires_on - time.time() < refresh_offset


if __name__ == "__main__":
    hello_world()
    re_authentication()
