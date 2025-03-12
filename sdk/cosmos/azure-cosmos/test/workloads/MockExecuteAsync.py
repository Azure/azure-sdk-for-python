import time

from azure.core.exceptions import ServiceRequestError, ServiceResponseError

from azure.cosmos import exceptions
from azure.cosmos.aio import _retry_utility_async
from .. import test_config

from workload_configs import COSMOS_URI, MOCK_EXECUTE_STATUS_CODE


class MockExecuteServiceRequestException(object):
    def __init__(self, original_func):
        self.original_func = original_func
        self.start_time = time.time()

    def __call__(self, func, *args, **kwargs):
        if args[1].location_endpoint_to_route == COSMOS_URI and time.time() - self.start_time >= 600\
                and time.time() <= self.start_time + 1800:
            if MOCK_EXECUTE_STATUS_CODE == 1:
                exception = ServiceResponseError("mock exception")
                exception.exc_type = Exception
                raise exception
            else:
                raise exceptions.CosmosHttpResponseError(
                    status_code=MOCK_EXECUTE_STATUS_CODE,
                    message="Some Exception",
                    response=test_config.FakeResponse({}))
        else:
            self.original_func(func, *args, **kwargs)


def mock_execute_func():
       if MOCK_EXECUTE_STATUS_CODE == 0:
           return
       else:
           mf = MockExecuteServiceRequestException(_retry_utility_async)
           _retry_utility_async.ExecuteFunctionAsync = mf
