# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" This is an example to use for quick pylint tests
"""
from azure.core import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
import logging
from azure.core.pipeline.policies import NetworkTraceLoggingPolicy
from azure.core.polling import LROPoller
_LOGGER = logging.getLogger(__name__)

class PylintError(BaseException):
    pass

class MyExampleClient(object):
    """ A simple, canonical client

    .. code-block:: python
        thing = 5
    """

    def __init__(self, base_url, credential, **kwargs):
        """ This constructor follows the canonical pattern.
        """
        self._client = None

    @distributed_trace
    def create_configuration(self, **kwargs) -> None:
        """ All methods should allow for a configuration instance to be created.

        """
        results_per_page = kwargs.pop('results_per_page', None)
        return results_per_page


    @distributed_trace
    def list_thing(self, one, two, three, four):
        """ Getting a single instance should include a required parameter

        - The first positional parameter should be a name or some other identifying
        attribute of the `thing`.
        """
        command = 1
        return list()

    @distributed_trace_async
    def list_key(self, name: str, version: str = None):
        """hel
        .. code-block:: python
            thing = 5
        """
        return ItemPaged()

    def from_connection_string(self):
        return LROPoller()


class StorageLoggingPolicy(NetworkTraceLoggingPolicy):
    """A policy that logs HTTP request and response to the DEBUG logger.

    This accepts both global configuration, and per-request level with "enable_http_logger"
    """

    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        http_request = request.http_request
        options = request.context.options
        if options.pop("logging_enable", self.enable_http_logger):
            request.context["logging_enable"] = True
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            try:
                log_url = http_request.url
                query_params = http_request.query
                if 'sig' in query_params:
                    log_url = log_url.replace(query_params['sig'], "sig=*****")
                _LOGGER.debug("Request URL: %r", log_url)
                _LOGGER.debug("Request method: %r", http_request.method)
                _LOGGER.debug("Request headers:")
                for header, value in http_request.headers.items():
                    if header.lower() == 'authorization':
                        value = '*****'
                    elif header.lower() == 'x-ms-copy-source' and 'sig' in value:
                        # take the url apart and scrub away the signed signature
                        scheme, netloc, path, params, query, fragment = urlparse(value)
                        parsed_qs = dict(parse_qsl(query))
                        parsed_qs['sig'] = '*****'

                        # the SAS needs to be put back together
                        value = urlunparse((scheme, netloc, path, params, urlencode(parsed_qs), fragment))

                    _LOGGER.debug("    %r: %r", header, value)
                _LOGGER.debug("Request body:")

                # We don't want to log the binary data of a file upload.
                if isinstance(http_request.body, types.GeneratorType):
                    _LOGGER.debug("File upload")
                else:
                    _LOGGER.debug(str(http_request.body))
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Failed to log request: %r", err)

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse, Any) -> None
        if response.context.pop("logging_enable", self.enable_http_logger):
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            try:
                _LOGGER.debug("Response status: %r", response.http_response.status_code)
                _LOGGER.debug("Response headers:")
                for res_header, value in response.http_response.headers.items():
                    _LOGGER.debug("    %r: %r", res_header, value)

                # We don't want to log binary data if the response is a file.
                _LOGGER.debug("Response content:")
                pattern = re.compile(r'attachment; ?filename=["\w.]+', re.IGNORECASE)
                header = response.http_response.headers.get('content-disposition')

                if header and pattern.match(header):
                    filename = header.partition('=')[2]
                    _LOGGER.debug("File attachments: %s", filename)
                elif response.http_response.headers.get("content-type", "").endswith("octet-stream"):
                    _LOGGER.debug("Body contains binary data.")
                elif response.http_response.headers.get("content-type", "").startswith("image"):
                    _LOGGER.debug("Body contains image data.")
                else:
                    if response.context.options.get('stream', False):
                        _LOGGER.debug("Body is streamable")
                    else:
                        _LOGGER.debug(response.http_response.text())
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Failed to log response: %s", repr(err))



# class MyExamplefClient(object):
#     """ A simple, canonical client
#     """
#
#     def __init__(self, base_url, credential, **kwargs):
#         """ This constructor follows the canonical pattern.
#         """
#
#     @staticmethod
#     def create_configuration(cls, param):
#         """ All methods should allow for a configuration instance to be created.
#         """
#
#     async def get_thing(self, name):
#         # type: (str) -> Thing
#         """ Getting a single instance should include a required parameter
#
#         - The first positional parameter should be a name or some other identifying
#         attribute of the `thing`.
#         """
#
#     def list_things(self): # pylint: disable=client-method-missing-tracing-decorator
#         """ Getting a list of instances should not include any required parameters.
#         """
#
#     def check_if_exists(self):
#         """Checking if something exists
#         """
#
#     def _ignore_me(self):
#         """Ignore this internal method
#         """
#
# def put_thing():
#     """Not an approved name prefix.
#     """
#     client(one, two, three, four)