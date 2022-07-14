## Azure Cache for Redis: Azure AD with redis client library

### Table of contents

- [Authenticate with Azure AD - Hello World](#authenticate-with-azure-ad-hello-world)
- [Authenticate with Azure AD - Handle Re-authentication](#authenticate-with-azure-ad-handle-re-authentication)

#### Samples guidance

Familiarity with the [redis](https://pypi.org/project/redis/) and [azure-identity for Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity) client libraries is assumed.

[Authenticate with Azure AD - Hello World](#authenticate-with-azure-ad-hello-world)
This sample is recommended for users getting started to use Azure AD authentication with Azure Cache for Redis.

[Authenticate with Azure AD - Handle Re-Authentication](#authenticate-with-azure-ad-handle-re-authentication)
This sample is recommended to users looking to build long-running applications that would like to handle re-authenticating with Azure AD upon token expiry.

**Note:** The below sample uses the Azure Identity library's `ClientSecretCredential`. The credential can be replaced with any of the other `TokenCredential` implementations offered by the azure-identity library.

#### Authenticate with Azure AD: hello world

This sample is intended to assist in authenticating with Azure AD via the redis client library. It focuses on displaying the logic required to fetch an Azure AD access token and to use it as password when setting up the redis instance.

##### Migration guidance

When migrating your existing application code, you need to replace the password input with the Azure AD token.
Integrate the logic in your application code to fetch an Azure AD access token via the azure-identity library as shown below and replace it with the password configuring/retrieving logic in your application code.

```py
import redis
from azure.identity import DefaultAzureCredential

scope = "https://*.cacheinfra.windows.net:10225/appid/.default"  # The scope will be changed for AAD Public Preview
host = ""  # Required
port = 6380  # Required
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

if __name__ == '__main__':
    hello_world()
```

#### Authenticate with Azure AD: handle re-authentication

This sample is intended to assist in authenticating with Azure AD via redis client library. It focuses on displaying the logic required to fetch an Azure AD access token and to use it as password when setting up the redis instance. It also shows how to recreate and authenticate the redis instance when its connection is broken in error/exception scenarios.

##### Migration guidance

When migrating your existing application code, you need to replace the password input with the Azure AD token.
Integrate the logic in your application code to fetch an Azure AD access token via the azure-identity library as shown below and replace it with the password configuring/retrieving logic in your application code.

```py
import logging
import redis
from azure.identity import DefaultAzureCredential

scope = "https://*.cacheinfra.windows.net:10225/appid/.default"  # The scope will be changed for AAD Public Preview
host = ""  # Required
port = 6380  # Required
user_name = ""  # Required

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
    re_authentication()
```