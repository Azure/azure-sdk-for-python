# Azure WebPubSub Cloud Events client library for Python

This is the Microsoft Azure Web PubSub Upstream Library.
This package has been tested with python 3.9.

To understand the protocol, see [CloudEvents extension for Azure Web PubSub](https://docs.microsoft.com/azure/azure-web-pubsub/reference-cloud-events)

## Getting started

```bash
pip install azure-messaging-webpubsub-upstream
```

1. First, create a handler with following code:
   ```python
    from azure.messaging.webpubsub.upstream import (
        EventHandler,
    )
    handler = EventHandler(handle_connect=handle_connect)
   ```
2. We offered helper functions for handling requests
   ```
   # To check if a preflight request is valid.
   preflight = handler.preflight(headers)
   # To parse a ServiceRequest with ConnectionContext from HTTP request.
   request = handler.from_http(headers, body)
   # To generate a ServiceResponse for sending HTTP response.
   response = handler.handle(headers, body)
   ```
   These methods could be helpful when you writing your cloud event handlers.
3. We also offered a `wsgi` wrapper to handle requests:

    ```python
    wrapped_wsgi_app = handler.wrap(wsgi_app)
    ```
    Please check our samples for furthur usages.
    - Azure Functions HTTP Trigger
    - Flask
    - Django
    - Pyrimid

## Key concepts

### Request Validation

You could enable request validation by injecting a `RequestValidator`

This could effect both `preflight` and `signature check`.

Both of them will return **True** when request validation is disabled.

### Access Key Validation

```python
from http import HTTPStatus

from azure.messaging.webpubsub.upstream import (
    EventHandler,
    AccessKeyValidator,
)

from azure.messaging.webpubsub.upstream.exceptions import (
    ValidationFailedError,
)

validator = AccessKeyValidator("<connection string>")

def handle_exception(e):
    if isinstance(e, ValidationFailedError):
        print(e.context)
        return int(HTTPStatus.FORBIDDEN) # we will return `401 UNAUTHORIZED` by default


helper = EventHandler(request_validator=validator, handle_exception=handle_exception)
```

## Examples

### Handle Cloud Events

Blocking events:
- Connect Event
- User Message Event

NonBlocking events:
- Connected Event
- Disconnected Event

It is recommend to write an api handler with your Web Framework.

Let's use Flask as a example:

```python
from flask import (
    Flask,
    request,
    Response,
)

from azure.messaging.webpubsub.upstream import (
    EventHandler,
)

app = Flask(__name__)

helper = EventHandler(handle_connect=handle_connect, handle_connected=handle_connected, ...)

@app.route("/upstream")
def upstream_api():
    # Get headers & body from your web framework
    # (headers, body) = ...

    response = helper.handle(request.headers, request.data)

    # Use these properties to build your own response for specific web framework.
    print(response.status_code)
    print(response.headers)
    print(response.body)
    return Response(response.body, headers=response.headers, status=response.status_code)
```

### Handle Blocking Events

#### Handle `ConnectEvent`

```python
def handle_connect(request):
    print(request.connection_id)
    print(request.hub)
    print(request.connection_state)
    print(request.webhook_request_origin)

    print(request.claims)
    assert event.query == query
    assert event.subprotocols == subprotocols
    assert event.client_certificates == client_certificates

    return {
        "groups": ["foo", "bar"],
        "userId": "user1",
        "roles": ["webpubsub.sendToGroup"],
        "subprotocol": "protocol1",
    }

helper = EventHandler(handle_connect=handle_connect)
```

#### Handle `UserMessageEvent`

```python
from azure.messaging.webpubsub.upstream import (
    EventHandler,
    ConnectEventRequest,
)

def handler_user_message(request):
    print(request.connection_id)
    print(request.hub)
    print(request.connection_state)
    print(request.webhook_request_origin)
    return "customized response"

helper = EventHandler(handle_user_message=handle_user_message)
```

#### Update connection state

You can update connection state in `response` if it was returned by one of the blocking events:

```python
response.set_state("key", "next_state")
```

By doing this we will update the headers field to help you generate `base64` encoded connection state.

```python
print(response.headers)

'''
Output:
{
    "ce-connectionState": "eyJrZXkiOiAibmV4dF9zdGF0ZSJ9"
}
'''
```

Or simply clear connection state by calling `clear_states`:

```python
response.clear_states()
```

We will also help you update the header field.

*Mention: Only `Connect` and `UserMessage` event can update connection state.*

### Handle Non-Blocking Events

Non-Blocking events should be handled asynchronously if possible.

We only accept `200 OK` response for these events and we will **NOT** wait for other response status codes.

If you'd like to handle it asynchronously in your server, the `from_http` method may help you distinguish between `BlockingEvents` and `NonBlockingEvents`. 

Let's still use `Flask` as a example.

```python
from flask import (
    Flask,
    request,
    Response,
)

from azure.messaging.webpubsub.upstream import (
    EventHandler,
)

app = Flask(__name__)

helper = EventHandler(handle_connect=handle_connect, handle_connected=handle_connected, ...)

@app.after_response()
def after():
    helper.handle(request.headers, request.data)

@app.route("/upstream")
def upstream_api():
    # Get headers & body from your web framework
    # (headers, body) = ...

    request = helper.from_http(request.headers, request.data)
    if not request.is_blocking:
        return Response(status=HTTPStatus.OK)

    response = helper.handle(request)

    # Use these properties to build your own response for specific web framework.
    print(response.status_code)
    print(response.headers)
    print(response.body)
    return Response(response.body, headers=response.headers, status=response.status_code)
```

#### Handle `ConnctedEvent`

```python
from azure.messaging.webpubsub.upstream import (
    EventHandler,
    ConnectEventRequest,
)

def handle_connected(request):
    print(request.connection_id)
    print(request.hub)
    print(request.connection_state)
    print(request.webhook_request_origin)

helper = EventHandler(handle_connected=handle_connected)
```

#### Handle `DisconnectedEvent`

```python
from azure.messaging.webpubsub.upstream import (
    EventHandler,
    ConnectEventRequest,
)

def handle_disconnected(request):
    print(request.connection_id)
    print(request.hub)
    print(request.connection_state)
    print(request.webhook_request_origin)

helper = EventHandler(handle_disconnected=handle_disconnected)
```

### Handle Exceptions

Built-in exceptions can be imported from:

```python
from azure.messaging.webpubsub.upstream.exceptions import (
    ValidationFailedError,
    InvalidEventTypeError,
    # ...
)
```

This ia a list of all built-in exceptions with descriptions:

| Type                       | description                                                   | properties              | status code |
| -------------------------- | ------------------------------------------------------------- | ----------------------- | ----------- |
| HeaderNotFound             | Indicates the request misses a require header                 | `key`                   | 400         |
| InvalidConnectRequestError | Indicates the body of the connect request is not a valid JSON | `key`                   | 400         |
| InvalidEventTypeError      | Indicates the event type is not expected                      | `context`, `event_type` | 400         |
| InvalidEventNameError      | Indicates the event name is not expected                      | `context`, `event_name` | 400         |
| ValidationFailedError      | Indicates the request is unauthorized                         | `context`               | 401         |

By default we will handle those exceptions and generate `ErrorResponse` with `4xx` status code.

But if you'd like to write some logs or debug your codes, you could write your own exception handler to replace ours.

```python
from http import HTTPStatus

from azure.messaging.webpubsub.upstream import (
    EventHandler,
)

from azure.messaging.webpubsub.upstream.exceptions import (
    ValidationFailedError
)

def handle_exception(e):
    if isinstance(e, ValidationFailedError):
        print("some metric")
    print(repr(e)) # logging
    return HTTPStatus.INTERNAL_SERVER_ERROR # override the 400 BAD REQUEST


helper = EventHandler(handle_exception=handle_exception)
```


## Troubleshooting

We strongly suggest to use `virtualenv` to run the test cases.

To create a virtualenv and active it, run the following commands:

```
python3 -m venv wpsenv
source wps/bin/activate
```

Than run following commands to install the package and test requirements

```bash
python setup.py develop
pip install -r dev_requirements.txt
```

Now you can use this command to run test cases.

```
pytest tests
```

## Next steps

Learn how to integret with mainstream web frameworks/containers:

- Azure Function
- Flask
- Django
- Pyramid
- Tornado

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[webpubsubservice_docs]: https://aka.ms/awps/doc