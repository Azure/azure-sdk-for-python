## Long-running operation (LRO) customization

Operations that are started by an initial call, then need to be monitored for status until completion are often represented as long-running operations (LRO).
The `azure-core` library provides the [LROPoller][lro_poller] (and [AsyncLROPoller][async_lro_poller]) protocols
that expose methods to interact with the LRO such as waiting until the operation reaches a terminal state, checking its status, or
providing a callback to do work on the final result when it is ready. If the LRO follows the 
[Azure REST API guidelines][rest_api_guidelines_lro], 
it's likely that the generated client library code should _just work_. 
In cases where the LRO diverges from the guidelines, you may need to customize your code to achieve the desired scenario.

There are 3 options to customize the logic for LROs.

1) [Polling strategy - OperationResourcePolling, LocationPolling, StatusCheckPolling](#polling-strategy---operationresourcepolling-locationpolling-statuscheckpolling)
    - You need to customize the polling strategy
2) [Polling method - LROBasePolling/AsyncLROBasePolling](#polling-method---lrobasepollingasynclrobasepolling)
    - You need to customize the polling loop
3) [Poller API - LROPoller/AsyncLROPoller](#poller-api---lropollerasynclropoller)
    - You need to customize the public interface of the poller

The "poller API" is what the user uses to interact with the LRO. Internally, the poller uses the "polling method" to run the polling
loop which makes calls to the status monitor, controls delay, and determines when the LRO has reached a terminal state.
The "polling method" uses a "polling strategy" to determine how to extract the status information from the responses 
returned by the status monitoring.

### Polling strategy - OperationResourcePolling, LocationPolling, StatusCheckPolling

The `azure.core.polling` module provides three built-in strategies for polling -[OperationResourcePolling][operation_resource_polling],
[LocationPolling][location_polling], and [StatusCheckPolling][status_check_polling]. The type of polling needed will be 
determined automatically using the response structure, unless otherwise specified by the client library developer. If 
the LRO is determined not to fit either `OperationResourcePolling` or `LocationPolling`, `StatusCheckPolling` serves as 
a fallback strategy which will not perform polling, but instead return a successful response for a 2xx status code.

If you need to customize the polling strategy, choose a polling algorithm that closely represents what you need to do
or create your own that inherits from [azure.core.polling.base_polling.LongRunningOperation][long_running_operation] 
and implements the necessary methods.

For our example, let's say that `OperationResourcePolling` closely resembles what the service does, but we
need to account for a non-standard status.

#### Example: Raise exception for a non-standard status that is returned via the initial POST call - "ValidationFailed".

```python
from azure.core.polling.base_polling import OperationResourcePolling, _as_json
from azure.core.exceptions import HttpResponseError


class CustomOperationResourcePolling(OperationResourcePolling):
    """Implements a operation resource polling, typically from the Operation-Location header.
    Customized to raise an exception in the case of a "ValidationFailed" status returned
    from the service.
    """

    def get_status(self, pipeline_response: "PipelineResponseType") -> str:
        """This method is called on the response for each polling request
        and is used to extract and return the LRO status from that response. 
        In the case that the operation has failed (i.e. a non-successful status),
        an exception should be raised. This will bring polling to an end and raise
        the failure to the listener.
        """
        status = super().get_status(pipeline_response)
        if status.lower() == "validationfailed":
            response = pipeline_response.http_response
            body = _as_json(response)
            raise HttpResponseError(response=response, error=body["error"])
        return status
```

You can then wrap a client method that was generated as an LRO, and pass the additional `polling` keyword argument. The `polling`
keyword argument takes an implementation of [azure.core.polling.PollingMethod][polling_method] 
(e.g. [azure.core.polling.base_polling.LROBasePolling][lro_base_polling]) and allows for a custom strategy to be passed 
in to the keyword argument `lro_algorithms`:

```python
from typing import AnyStr, MutableMapping, Any
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
JSON = MutableMapping[str, Any]


class ServiceOperations:

    def begin_analyze(self, data: AnyStr, name: str, **kwargs) -> LROPoller[JSON]:
        return self._generated_client.begin_analyze(
            data,
            name,
            polling=LROBasePolling(
                lro_algorithms=[
                    CustomOperationResourcePolling()  # overrides other LRO strategies
                ]
            ),
            **kwargs
        )
```

This example uses the default polling method - `LROBasePolling` and just overrides the strategy used for polling.
If you need to control the polling loop, then see the next section.


### Polling method - LROBasePolling/AsyncLROBasePolling

Built-in methods for polling are included in `azure-core` as both sync / async variants - [LROBasePolling][lro_base_polling] 
and [AsyncLROBasePolling][async_lro_base_polling]. The polling method runs the polling loop and performs GET requests 
to the status monitor to check if a terminal state is reached. In between polls it inserts delay based on 
1) the service sent `retry-after` header, or 2) the given `polling_interval` if no retry-after header is present.

You can also use [azure.core.polling.NoPolling][no_polling](or [AsyncNoPolling][async_no_polling]) which will not 
initiate polling and simply return the deserialized initial response when called with `poller.result()`.

To use `NoPolling`, you can pass `polling=False` to an operation generated as an LRO:

```python
from typing import AnyStr, MutableMapping, Any
from azure.core.polling import LROPoller
JSON = MutableMapping[str, Any]


class ServiceOperations:

    def begin_analyze(self, data: AnyStr, name: str, **kwargs) -> LROPoller[JSON]:
        return self._generated_client.begin_analyze(
            data,
            name,
            polling=False,
            **kwargs
        )
```

To customize parts of the polling method, you can create a subclass which uses [LROBasePolling][lro_base_polling] and overrides necessary methods.
If significant customization is necessary, use [azure.core.polling.PollingMethod][polling_method] 
(or [AsyncPollingMethod][async_polling_method])and implement all the necessary methods.

#### Example: Create an LRO method which will poll for when a file gets uploaded successfully (greatly simplified)

For this example, the customization necessary requires defining our own polling strategy and polling method.
First, we'll define a simple polling strategy that the polling method will use to get the status information from the response.

```python
from typing import Optional, MutableMapping, Any
from azure.core.polling.base_polling import LongRunningOperation, OperationFailed
from azure.core.pipeline import PipelineResponse
JSON = MutableMapping[str, Any]


class CustomPollingStrategy(LongRunningOperation):
    """CustomPollingStrategy which provides default logic
    for interpreting operation responses and status updates.
    """

    def can_poll(self, pipeline_response: PipelineResponse) -> bool:
        """Determine from the initial response that we can poll.
        In this example, we need a file_id present to proceed with polling.

        :param PipelineResponse pipeline_response: initial REST call response.
        """
        response = pipeline_response.http_response.json()
        if response.get("file_id", None) is None:
            return False
        return True

    def get_polling_url(self) -> str:
        """Return the polling URL. This is the URL for the status monitor
        and where the GET requests will be made during polling.
        
        For this example, we don't need to extract the URL
        from the initial response so it is not implemented.
        """
        raise NotImplementedError("The polling strategy does not need to extract a polling URL.")

    def set_initial_status(self, pipeline_response: PipelineResponse) -> str:
        """Process first response after initiating long running operation and set initial status.

        :param PipelineResponse pipeline_response: initial REST call response.
        """

        response = pipeline_response.http_response
        if response.status_code == 200:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_status(self, response: JSON) -> str:
        """Return the status based on this response.

        Typically, this method extracts a status string from the 
        response. In this example, we determine status based on whether our
        result is populated or not. 
        """
        if response is None:
            return "InProgress"
        return "Succeeded"

    def get_final_get_url(self, pipeline_response: PipelineResponse) -> Optional[str]:
        """If a final GET is needed when the LRO is complete, returns the URL.

        :rtype: str
        """
        return None
```

Next, we'll define the custom polling method:


```python
import functools
import time
import base64
from typing import Any, Tuple, Callable, MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.polling import PollingMethod
from azure.core.polling.base_polling import BadResponse
from azure.core.exceptions import ResourceNotFoundError
JSON = MutableMapping[str, Any]


class CustomPollingMethod(PollingMethod):
    def __init__(self, polling_interval: float = 30, **kwargs: Any) -> None:
        """Creates a custom polling method which polls until a file is uploaded.
        For our example, the operation is considered to have reached a terminal state once a successful GET
        is done on the file (e.g. no ResourceNotFoundError is raised).

        :param polling_interval: The amount of time to wait between polls. This fictitious service does not
            use retry-after so we will default to this value.
        :param kwargs: Any operation-specific keyword arguments that should be passed into the GET call.
        """
        self._polling_interval = polling_interval
        self._kwargs = kwargs

    def initialize(self, client: Any, initial_response: PipelineResponse, deserialization_callback: Callable) -> None:
        """Set the initial status of this LRO, verify that we can poll, and 
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # verify we have the information to poll
        if self._operation.can_poll(initial_response) is False:
            raise BadResponse("No file_id in response.")
        
        response = initial_response.http_response.json()

        # initialize
        self.client = client
        self.file_id = response["file_id"]
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._resource = None
        self._finished = False
        
        # sets our strategy
        self._operation = CustomPollingStrategy()
    
        # create the command which will be polled against as the status monitor
        self._command = functools.partial(self.client.get_upload_file, file_id=self.file_id, **self._kwargs)
        
        # set initial status
        self._status = self._operation.set_initial_status(initial_response)

        
    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state 
            or False if polling should continue.
        :rtype: bool
        """
        return True if self.status() == "Succeeded" else False

    def resource(self) -> JSON:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize()) 
        to transform or customize the final result, if necessary.
        """
        return self._deserialization_callback(self._resource)

    def run(self) -> None:
        """The polling loop.
        
        The polling should call the status monitor, evaluate and set the current status, 
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # inserts delay if not done
                time.sleep(self._polling_interval)

    def update_status(self):
        """Update the current status of the LRO by calling the status monitor 
        and then using the polling strategy's get_status() to set the status."""
        try:
            self._resource = self._command()
        except ResourceNotFoundError:
            pass
        
        self._status = self._operation.get_status(self._resource)
                
    def get_continuation_token(self) -> str:
        """Returns an opaque token which can be used by the user to rehydrate/restart the LRO.
        Saves the initial state of the LRO so that polling can be resumed from that context.

        .. code-block:: python

            initial_poller = client.begin_upload(data)
            continuation_token = initial_poller.continuation_token()

            poller: LROPoller = client.begin_upload(None, continuation_token=continuation_token)
            poller.result()

        In standard LROs, the PipelineResponse is serialized here, however, there may be a need to
        customize this further depending on your scenario.
        """
        import pickle

        return base64.b64encode(pickle.dumps(self._initial_response)).decode("ascii")

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Tuple[Any, PipelineResponse, Callable]:
        """Deserializes the user-provided continuation_token to the initial response and returns 
        the context necessary to rebuild the LROPoller from its classmethod.
        """
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token")

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError(
                "Need kwarg 'deserialization_callback' to be recreated from continuation_token"
            )
        
        import pickle

        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        # Restore the transport in the context
        initial_response.context.transport = client._client._pipeline._transport  # pylint: disable=protected-access
        return client, initial_response, deserialization_callback
```

And now, to plug into the client code:

```python
from typing import AnyStr, MutableMapping, Any
from azure.core.polling import LROPoller
JSON = MutableMapping[str, Any]


class ServiceOperations:

    def begin_upload(self, data: AnyStr, **kwargs) -> LROPoller[JSON]:
        continuation_token = kwargs.pop("continuation_token", None)
        polling_method = CustomPollingMethod(**kwargs)
        
        # if continuation_token is provided, we should rehydrate the LRO using the from_continuation_token method
        # which calls our implementation on the CustomPollingMethod method
        if continuation_token is not None:
            return LROPoller.from_continuation_token(
                continuation_token=continuation_token,
                polling_method=polling_method,
                deserialization_callback=lambda x: x,
                client=self
            )

        # the initial call. We pass in `cls` to receive the pipeline_response.
        pipeline_response = self._generated_client.create_upload(data, cls=lambda response, x, y: response, **kwargs)

        return LROPoller(
            client=self,
            initial_response=pipeline_response,
            deserialization_callback=lambda x: x,  # returning the result as-is, but could be a callable to transform the final result
            polling_method=polling_method,
        )
```

Note that we need to account for a `continuation_token` being passed by the user, in which case we should not make the
initial call again, but rather resume polling from the rehydrated state. Since passing `continuation_token` doesn't 
require the user to provide the parameters for the initial call, it can be helpful to add overloads to the method to 
clarify its usage, especially in cases where required parameters become non-required:

```python
from typing import AnyStr, MutableMapping, Any, overload
from azure.core.polling import LROPoller
JSON = MutableMapping[str, Any]


class ServiceOperations:
    @overload
    def begin_upload(self, data: AnyStr, **kwargs: Any) -> LROPoller[JSON]:
        ...


    @overload
    def begin_upload(self, *, continuation_token: str, **kwargs: Any) -> LROPoller[JSON]:
        ...

    def begin_upload(self, *args, **kwargs) -> LROPoller[JSON]:
        continuation_token = kwargs.pop("continuation_token", None)
        polling_method = CustomPollingMethod(**kwargs)
        if continuation_token is not None:
            return LROPoller.from_continuation_token(
                continuation_token=continuation_token,
                polling_method=polling_method,
                deserialization_callback=lambda x: x,
                client=self
            )

        data = kwargs.pop("data", None)
        if data is None:
            try:
                data = args[0]
            except IndexError:
                raise TypeError("begin_upload() missing 1 required positional argument: 'data'")

        pipeline_response = self._generated_client.create_upload(data, cls=lambda response, x, y: response, **kwargs)

        return LROPoller(
            client=self,
            initial_response=pipeline_response,
            deserialization_callback=lambda x: x,
            polling_method=polling_method,
        )
```


### Poller API - LROPoller/AsyncLROPoller

The last option is if you need to customize the public interface of the `LROPoller` / `AsyncLROPoller`.
Reasons to do this might include exposing important attributes or metadata of the operation in progress, 
or adding new features to interact with the operation, such as to pause/resume or cancel it.

#### Example: I want to add a cancel method to my poller

This example builds off the previous example and uses the custom polling method defined above. The custom polling
method gives us access to the client and `file_id` needed to make the `cancel` call. If you support rehydration of 
the LRO via `continuation_token`, you must override the `from_continuation_token` method so that the custom poller is used.

```python
from typing import TypeVar
from azure.core.polling import LROPoller, PollingMethod
PollingReturnType = TypeVar("PollingReturnType")


class CustomLROPoller(LROPoller[PollingReturnType]):

    def cancel(self, **kwargs) -> None:
        """Cancel the upload"""
        return self.polling_method().client.cancel_upload_file(self.polling_method().file_id, **kwargs)

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[PollingReturnType], continuation_token: str, **kwargs
    ) -> "CustomLROPoller[PollingReturnType]":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)
        return cls(client, initial_response, deserialization_callback, polling_method)

```

And now, to plug into the client code:

```python
from typing import AnyStr, MutableMapping, Any
JSON = MutableMapping[str, Any]


class ServiceOperations:

    def begin_upload(self, data: AnyStr, **kwargs) -> CustomLROPoller[JSON]:
        continuation_token = kwargs.pop("continuation_token", None)
        polling_method = CustomPollingMethod(**kwargs)
        if continuation_token is not None:
            return CustomLROPoller.from_continuation_token(
                continuation_token=continuation_token,
                deserialization_callback=lambda x: x,
                polling_method=polling_method,
                client=self
            )
        response = self._generated_client.create_upload(data, **kwargs)
        return CustomLROPoller[JSON](
            client=self,
            initial_response=response,
            deserialization_callback=lambda x: x,
            polling_method=polling_method,
        )
```

Note that we updated the `begin_upload` return type to `CustomLROPoller`. You should only need to explicitly reference
the custom poller if a new public API has been added. The custom poller should additionally be added to the package 
`__init__.py` so that the new public API will be properly documented.


[rest_api_guidelines_lro]: https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md#long-running-operations--jobs
[operation_resource_polling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/base_polling.py#L178
[location_polling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/base_polling.py#L277
[status_check_polling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/base_polling.py#L325
[lro_poller]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.LROPoller
[lro_base_polling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/base_polling.py#L357
[long_running_operation]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/base_polling.py#L121-L161
[polling_method]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.PollingMethod
[async_polling_method]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.AsyncPollingMethod
[async_lro_poller]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.AsyncLROPoller
[async_lro_base_polling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/async_base_polling.py#L40
[no_polling]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.NoPolling
[async_no_polling]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.polling.html#azure.core.polling.AsyncNoPolling
