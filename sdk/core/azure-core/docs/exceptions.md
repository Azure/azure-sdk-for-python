# Azure Core Library Exceptions

## AzureError
AzureError is the base exception for all errors.
```python
class AzureError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.inner_exception = kwargs.get('error')
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.exc_type = self.exc_type.__name__ if self.exc_type else type(self.inner_exception)
        self.exc_msg = "{}, {}: {}".format(message, self.exc_type, self.exc_value)  # type: ignore
        self.message = str(message)
        super(AzureError, self).__init__(self.message, *args)
```

*message* is any message (str) to be associated with the exception. 

*args* are any additional args to be included with exception.

*kwargs* are keyword arguments to include with the exception. Use the keyword *error* to pass in an internal exception.


**The following exceptions inherit from AzureError:**

## ServiceRequestError
An error occurred while attempt to make a request to the service. No request was sent.

## ServiceResponseError
The request was sent, but the client failed to understand the response.
The connection may have timed out. These errors can be retried for idempotent or safe operations.


## HttpResponseError
Error occurs when a request was made, and a non-success status code was received from the service.
```python
class HttpResponseError(AzureError):
    def __init__(self, message=None, response=None, **kwargs):
        self.reason = None
        self.response = response
        if response:
            self.reason = response.reason
        message = "Operation returned an invalid status code '{}'".format(self.reason)
        try:
            try:
                if self.error.error.code or self.error.error.message:
                    message = "({}) {}".format(
                        self.error.error.code,
                        self.error.error.message)
            except AttributeError:
                if self.error.message: #pylint: disable=no-member
                    message = self.error.message #pylint: disable=no-member
        except AttributeError:
            pass
        super(HttpResponseError, self).__init__(message=message, **kwargs)
```

*response* is the HTTP response (optional).

*kwargs* are keyword arguments to include with the exception.


**The following exceptions inherit from HttpResponseError:**

## DecodeError
An error raised during response deserialization.

## ResourceExistsError
An error response with status code 4xx. This will not be raised directly by the Azure core pipeline.

## ResourceNotFoundError
An error response, typically triggered by a 412 response (for update) or 404 (for get/post).

## ClientAuthenticationError
An error response with status code 4xx. This will not be raised directly by the Azure core pipeline.

## ResourceModifiedError
An error response with status code 4xx, typically 412 Conflict. This will not be raised directly by the Azure core pipeline.

## TooManyRedirectsError
An error raised when the maximum number of redirect attempts is reached. The maximum amount of redirects can be configured in the RedirectPolicy.
```python
class TooManyRedirectsError(HttpResponseError):
    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)
```

*history* is used to document the requests/responses that resulted in redirected requests.

*args* are any additional args to be included with exception.

*kwargs* are keyword arguments to include with the exception.