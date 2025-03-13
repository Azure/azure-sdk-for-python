import time

from azure.core.exceptions import ServiceRequestError, ServiceResponseError

from azure.cosmos import exceptions
from azure.cosmos.aio import _retry_utility_async

from workload_configs import COSMOS_URI, MOCK_EXECUTE_STATUS_CODE


class MockExecuteServiceRequestException(object):
    def __init__(self, original_func):
        self.original_func = original_func
        self.start_time = time.time()

    async def __call__(self, func, *args, **kwargs):
        # after 10 minutes, we will start to throw exceptions and ends after 30 minutes
        if time.time() - self.start_time >= 600 and time.time() <= self.start_time + 1800 and args:
            if args[1].endpoint_override:
                if args[1].endpoint_override == COSMOS_URI:
                    raise_exception()
            elif args[1].location_endpoint_to_route == COSMOS_URI:
                raise_exception()
        return await self.original_func(func, *args, **kwargs)

def raise_exception():
    if MOCK_EXECUTE_STATUS_CODE == 1:
        exception = ServiceRequestError("mock exception")
        exception.exc_type = Exception
        raise exception
    else:
        raise exceptions.CosmosHttpResponseError(
            status_code=MOCK_EXECUTE_STATUS_CODE,
            message="Some Exception",
            response=FakeResponse({}))

class FakeResponse:
    def __init__(self, headers):
        self.headers = headers
        self.reason = "foo"
        self.status_code = MOCK_EXECUTE_STATUS_CODE


def mock_execute_func():
       if MOCK_EXECUTE_STATUS_CODE != 0:
           mf = MockExecuteServiceRequestException(_retry_utility_async.ExecuteFunctionAsync)
           _retry_utility_async.ExecuteFunctionAsync = mf
