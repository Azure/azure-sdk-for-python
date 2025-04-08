# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import urllib.parse as url_parse

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import AioHttpTransport, RequestsTransport

from devtools_testutils import trim_kwargs_from_test_function
from devtools_testutils.helpers import is_live_and_not_recording
from devtools_testutils.proxy_testcase import (
    get_test_id,
    start_record_or_playback,
    transform_request,
    stop_record_or_playback,
)

from async_wrapper import wrap_result


# A modified version of devtools_testutils.aio.recorded_by_proxy_async
# that modifies AioHttpTransport.send and RequestsTransport.send to make
# both async and sync calls work with the proxy.
def recorded_by_proxy_async(test_func):
    """Decorator that redirects network requests to target the azure-sdk-tools test proxy. Use with recorded tests.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    async def record_wrap(*args, **kwargs):
        def transform_args(*args, **kwargs):
            copied_positional_args = list(args)
            request = copied_positional_args[1]

            transform_request(request, recording_id)

            return tuple(copied_positional_args), kwargs

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(test_func, trimmed_kwargs)

        if is_live_and_not_recording():
            return await test_func(*args, **trimmed_kwargs)

        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)
        async_transport_func = AioHttpTransport.send
        sync_transport_func = RequestsTransport.send

        async def combined_call_async(*args, **kwargs):
            adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
            result = await async_transport_func(*adjusted_args, **adjusted_kwargs)

            # make the x-recording-upstream-base-uri the URL of the request
            # this makes the request look like it was made to the original endpoint instead of to the proxy
            # without this, things like LROPollers can get broken by polling the wrong endpoint
            parsed_result = url_parse.urlparse(result.request.url)
            upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
            upstream_uri_dict = {
                "scheme": upstream_uri.scheme,
                "netloc": upstream_uri.netloc,
            }
            original_target = parsed_result._replace(**upstream_uri_dict).geturl()

            result.request.url = original_target
            return result

        def combined_call_sync(*args, **kwargs):
            adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
            result = sync_transport_func(*adjusted_args, **adjusted_kwargs)

            # make the x-recording-upstream-base-uri the URL of the request
            # this makes the request look like it was made to the original endpoint instead of to the proxy
            # without this, things like LROPollers can get broken by polling the wrong endpoint
            parsed_result = url_parse.urlparse(result.request.url)
            upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
            upstream_uri_dict = {
                "scheme": upstream_uri.scheme,
                "netloc": upstream_uri.netloc,
            }
            original_target = parsed_result._replace(**upstream_uri_dict).geturl()

            result.request.url = original_target
            return result

        AioHttpTransport.send = combined_call_async
        RequestsTransport.send = combined_call_sync

        # call the modified function
        # we define test_variables before invoking the test so the variable is defined in case of an exception
        test_variables = None
        # this tracks whether the test has been run yet; used when calling the test function with/without `variables`
        # running without `variables` in the `except` block leads to unnecessary exceptions in test execution output
        test_run = False
        try:
            try:
                test_variables = await test_func(*args, variables=variables, **trimmed_kwargs)
                test_run = True
            except TypeError as error:
                if "unexpected keyword argument" in str(error) and "variables" in str(error):
                    logger = logging.getLogger()
                    logger.info(
                        "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                        "`variables` parameter to make use of recorded test variables."
                    )
                else:
                    raise error
            # if the test couldn't accept `variables`, run the test without passing them
            if not test_run:
                test_variables = await test_func(*args, **trimmed_kwargs)

        except ResourceNotFoundError as error:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            error_with_message = ResourceNotFoundError(message=message, response=error.response)
            raise error_with_message from error

        finally:
            AioHttpTransport.send = async_transport_func
            RequestsTransport.send = sync_transport_func
            stop_record_or_playback(test_id, recording_id, test_variables)

        return test_variables

    return record_wrap


def client_setup(test_func):
    def _batch_url(batch):
        if batch.account_endpoint.startswith("https://"):
            return batch.account_endpoint
        else:
            return "https://" + batch.account_endpoint

    def create_client(BatchClient, batch_account, credential, **kwargs):
        client = BatchClient(credential=credential, endpoint=_batch_url(batch_account))
        return client

    async def wrapper(self, BatchClient, **kwargs):
        kwargs["credential"] = self.get_credential(BatchClient)  # TODO: look into sharedkey auth to fix this workaround
        client = create_client(BatchClient, **kwargs)
        try:
            await test_func(self, client, **kwargs)
        except Exception as err:
            raise err
        finally:
            await wrap_result(client.close())

    return wrapper
