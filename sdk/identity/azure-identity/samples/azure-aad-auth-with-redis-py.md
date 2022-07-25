## Azure Cache for Redis: Azure AD with redis client library

### Table of contents

- [Prerequisites](#prerequisites)
- [Samples guidance](#samples-guidance)
- [Authenticate with Azure AD - Hello World](#authenticate-with-azure-ad-hello-world)
- [Authenticate with Azure AD - Handle Re-authentication](#authenticate-with-azure-ad-handle-re-authentication)
- [Troubleshooting](#troubleshooting)

#### Prerequisites

- Configuration of Role and Role Assignments is required before using the sample code in this document.
- Dependency requirements:
  - [redis](https://pypi.org/project/redis/)
  - [azure-identity for Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity)

#### Samples guidance

[Authenticate with Azure AD - Hello World](#authenticate-with-azure-ad-hello-world)
This sample is recommended for users getting started to use Azure AD authentication with Azure Cache for Redis.

[Authenticate with Azure AD - Handle Re-Authentication](#authenticate-with-azure-ad-handle-re-authentication)
This sample is recommended to users looking to build long-running applications that would like to handle re-authenticating with Azure AD upon token expiry.

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
                    ssl=True,    # ssl connection is required.
                    username=user_name,
                    password=token.token,
                    decode_responses=True)
    r.set("Az:key1", "value1")
    t = r.get("Az:key1")
    print(t)

if __name__ == '__main__':
    hello_world()
```

##### Supported Token Credentials for Azure AD Authentication

**Note:** The samples in this doc use the azure-identity library's `DefaultAzureCredential` to fetch Azure AD Access Token. The other supported `TokenCredential` implementations that can be used from azure-identity for Python are as follows:

- [Client Certificate Credential](https://aka.ms/azsdk/python/identity/certificatecredential)
- [Client Secret Credential](https://aka.ms/azsdk/python/identity/clientsecretcredential)
- [Managed Identity Credential](https://aka.ms/azsdk/python/identity/managedidentitycredential)
- [Username Password Credential](https://aka.ms/azsdk/python/identity/usernamepasswordcredential)
- [Azure CLI Credential](https://aka.ms/azsdk/python/identity/azclicredential)
- [Interactive Browser Credential](https://aka.ms/azsdk/python/identity/interactivebrowsercredential)
- [Device Code Credential](https://aka.ms/azsdk/python/identity/devicecodecredential)

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
                    ssl=True,    # ssl connection is required.
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
        except redis.ConnectionError:
            _LOGGER.info("Connection lost. Reconnecting.")
            token = cred.get_token(scope)
            r = redis.Redis(host=host,
                            port=port,
                            ssl=True,    # ssl connection is required.
                            username=user_name,
                            password=token.token,
                            decode_responses=True)
        except Exception:
            _LOGGER.info("Unknown failures.")
            break

if __name__ == '__main__':
    re_authentication()
```

#### Troubleshooting

##### Invalid Username Password Pair Error

In this error scenario, the username provided and the access token used as password are not compatible.
To mitigate this error, ensure that:

- On Portal, Under your Redis Cache Resource -> RBAC Rules, you've assigned the required role to your user/service principal identity.
- On Portal, Under your Redis Cache Resource -> Advanced settings -> AAD Access Authorization box is checked/enabled, if not enable it and press the Save button.

##### Permissions not granted / NOPERM Error

In this error scenario, the authentication was successful, but your registered user/service principal is not granted the RBAC permission to perform the action.
To mitigate this error, ensure that:

- On Portal, Under your Redis Cache Resource -> RBAC Rules, you've assigned the appropriate role (Owner, Contributor, Reader) to your user/service principal identity.
- In the event you're using a custom role, then ensure the permissions granted under your custom role include the one required for your target action.
