#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import json
import logging
import uuid
from azure.core import PipelineClient
from azure.core.configuration import Configuration, ConnectionConfiguration
from azure.core.pipeline.transport import HttpRequest, RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RedirectPolicy,
    RetryPolicy,
    HeadersPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    BearerTokenCredentialPolicy
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceResponseError,
    raise_with_traceback
)
from ._enums import InkStrokeKind, ApplicationKind, InkPointUnit, ServiceVersion
from ._models import _parse_recognition_units


_DEFAULT_ARGUMENTS = {
    "application_kind": ApplicationKind.MIXED,
    "ink_point_unit": InkPointUnit.MM,
    "language": "en-US",
    "unit_multiple": 1.0,
    "service_version": ServiceVersion.PREVIEW
}


def _validate_param(param, param_name, valid_type):
    if not isinstance(param, valid_type):
        supported_type = "<%s>" % valid_type.__name__
        if param is None:
            type_got = "None"
        else:
            type_got = type(param).__name__
        error_info = "%s should be %s, got <%s>." % (param_name, supported_type, type_got)
        raise ValueError(error_info)


def _get_and_validate_param(kwargs, param_name, valid_type=None, factory=None, default=None):
    value = kwargs.pop(param_name, None)
    if value is None:
        return default

    if valid_type:
        _validate_param(value, param_name, valid_type)
    if factory:
        try:
            value = factory(value)
        except ValueError as e:
            error_info = "%s: %s" % (param_name, str(e))
            raise ValueError(error_info)
    return value


class _AzureConfiguration(Configuration):
    def __init__(self, credential, **kwargs):  # pylint:disable=super-init-not-called
        self._set_universal(**kwargs)
        # sync-specific azure pipeline policies
        if isinstance(credential, str):
            self.headers_policy.add_header("Ocp-Apim-Subscription-Key", credential)
        else:
            scopes = kwargs.pop("scopes", [])
            self.authentication_policy = BearerTokenCredentialPolicy(credential, *scopes, **kwargs)
        self.retry_policy = kwargs.get("retry_policy", RetryPolicy(**kwargs))
        self.redirect_policy = kwargs.get("redirect_policy", RedirectPolicy(**kwargs))
        self.transport = kwargs.get("transport", RequestsTransport())

    def _set_universal(self, **kwargs):
        Configuration.__init__(self)
        self.connection = kwargs.get("connection_configuration", ConnectionConfiguration(**kwargs))
        self.user_agent_policy = kwargs.get("user_agent_policy", UserAgentPolicy(**kwargs))
        self.proxy_policy = kwargs.get("proxy_policy", ProxyPolicy(**kwargs))
        self.logging_policy = kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs))
        self.headers_policy = kwargs.get("headers_policy", HeadersPolicy(**kwargs))


class _InkRecognizerConfiguration(object):
    def __init__(self, **kwargs):
        # Ink Recognizer request arguments
        self.application_kind = _get_and_validate_param(kwargs, "application_kind", valid_type=ApplicationKind)
        self.ink_point_unit = _get_and_validate_param(kwargs, "ink_point_unit", valid_type=InkPointUnit)
        self.language = _get_and_validate_param(kwargs, "language", factory=str)
        self.unit_multiple = _get_and_validate_param(kwargs, "unit_multiple", factory=float)
        self.service_version = _get_and_validate_param(kwargs, "service_version", valid_type=ServiceVersion)
        # azure service common arguments
        self.response_hook = kwargs.get("response_hook", None)
        if self.response_hook is not None:
            if not callable(self.response_hook):
                raise ValueError("response_hook should be callable.")
        timeout = _get_and_validate_param(kwargs, "timeout", factory=float)
        client_request_id = _get_and_validate_param(kwargs, "client_request_id", factory=str)
        self.headers = _get_and_validate_param(kwargs, "headers", default={})
        self.headers["x-ms-client-request-id"] = client_request_id or str(uuid.uuid4())  # generate random uuid
        if timeout is not None:
            kwargs["connection_timeout"] = timeout
        self.kwargs = kwargs


class _InkRecognizerClientBase(object):
    def __init__(self, url, credential, **kwargs):
        # type: (str, TokenCredential, Any) -> None

        self._url = str(url)
        self._default_arguments = _DEFAULT_ARGUMENTS.copy()
        self._default_arguments.update(kwargs)

        azure_config = _AzureConfiguration(credential, **kwargs)
        self._pipeline_client = PipelineClient(
            base_url=url, config=azure_config, transport=azure_config.transport)

    def __enter__(self):
        self._pipeline_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._pipeline_client.__exit__(*exc_details)

    def _generate_config(self, request_arguments):
        arguments = self._default_arguments.copy()
        arguments.update(request_arguments)
        config = _InkRecognizerConfiguration(**arguments)
        return config

    def _generate_url(self, config):
        return self._url + config.service_version._to_string()  # pylint:disable=protected-access

    def _pack_one_stroke(self, stroke):  # pylint:disable=no-self-use
        stroke_points = [{"x": point.x, "y": point.y} for point in stroke.points]
        stroke_json = {
            "id": stroke.id,
            "points": stroke_points,
        }
        if stroke.kind in [InkStrokeKind.DRAWING, InkStrokeKind.WRITING]:
            stroke_json["kind"] = stroke.kind.value
        if stroke.language:
            stroke_json["language"] = stroke.language
        return stroke_json

    def _pack_request(self, ink_stroke_list, config):
        return json.dumps({
            "applicationType": config.application_kind.value,
            "language": config.language,
            "unit": config.ink_point_unit.value,
            "unitMultiple": config.unit_multiple,
            "strokes": [self._pack_one_stroke(stroke)
                        for stroke in ink_stroke_list
                        if len(stroke.points) != 0]
        })

    def _parse_result(self, response, config):  # pylint:disable=inconsistent-return-statements
        status_code = response.status_code
        headers = response.headers
        content = response.body().decode("utf-8")

        if status_code == 200:
            content_json = json.loads(content, encoding="utf-8")
            if config.response_hook:
                config.response_hook(headers, content_json)
            try:
                return _parse_recognition_units(content_json)
            except Exception as err:  # pylint:disable=broad-except
                msg = "Cannot parse response from server."
                raise_with_traceback(ServiceResponseError, msg, err)
        else:
            self._error_handler(status_code, content)

    def _error_handler(self, status_code, content):  # pylint:disable=no-self-use
        if status_code == 404:
            logging.warning(content)
            raise ResourceNotFoundError(content)
        if status_code == 401:
            logging.warning(content)
            raise ClientAuthenticationError(content)
        logging.warning(content)
        raise HttpResponseError(content)


class InkRecognizerClient(_InkRecognizerClientBase):
    """
    The InkRecognizerClient communicates with the service using default
    configuration settings or settings provided by the caller (which override
    the default settings). Communication with the service is
    blocking/synchronous.

    :param str url: target url of the Ink Recognizer service.

    :param ~azure.core.TokenCredential credential: An available Azure Active
    Directory credential for Ink Recognition Service.

    Key word arguments include Ink Recognizer specific arguments, azure service
    common arguments and azure pipline policies.

    Ink Recognizer specific arguments:

    :param ServiceVersion service_version: Version of Ink Recognizer Service.
    Default is ServiceVersion.Preview.

    :param ApplicationKind application_kind: Inform Ink Recognizer Service of
    contents of the application. This can facilitate faster processing as the
    service will skip some classification steps. Default is ApplicationKind.MIXED.

    :param InkPointUnit ink_point_unit: unit of the x and y axis coordinates
    for each InkPoint. Default is InkPointUnit.MM.

    :param str language: Language (IETF BCP-47) of strokes, can be overwritten
    by stroke-specific language. Default is "en-US".

    :param float unit_multiple: multiplier for unit. Each value in InkPoint
    will be multiplied by this value on server side. Default is 1.0.

    Azure service common arguments:

    :param ~azure.core.pipeline.transport.HttpTransport transport: transport
    instance for the client. Default is RequestsTransport().

    :param float timeout: Timeout in seconds.

    :param dict headers: Custom headers to include in the service request.

    :param str client_request_id: Caller-specified identification of the request.

    :param callable response_hook: callable that is called with
    (headers, deserialized_response) if the http status is 200.

    :param list[str] scopes: let you specify the type of access needed during authentication.

    Azure pipeline policies:
    https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md
    """

    def _send_request(self, data, config):
        request = HttpRequest("PUT", self._generate_url(config), data=data)
        response = self._pipeline_client._pipeline.run(  # pylint:disable=protected-access
            request, headers=config.headers, **config.kwargs)
        return response.http_response

    @distributed_trace
    def recognize_ink(self, ink_stroke_list, **kwargs):
        # type: (Iterable[IInkStroke], Any) -> InkRecognitionRoot
        """
        Synchronously sends data to the service and returns a tree structure
        containing all the recognition units from Ink Recognizer Service.

        :param Iterable[IInkStroke] ink_stroke_list: an iterable that contanins
        stroke instances.

        Key word arguments include Ink Recognizer specific arguments, azure
        service common arguments and azure pipline policies.

        Ink Recognizer specific arguments:

        :param ServiceVersion service_version: Version of Ink Recognizer Service.
        Default is ServiceVersion.Preview.

        :param ApplicationKind application_kind: Inform Ink Recognizer Service of
        contents of the application. This can facilitate faster processing as the
        service will skip some classification steps. Default is ApplicationKind.MIXED.

        :param InkPointUnit ink_point_unit: unit of the x and y axis coordinates
        for each InkPoint. Default is InkPointUnit.MM.

        :param str language: Language (IETF BCP-47) of strokes, can be overwritten
        by stroke-specific language. Default is "en-US".

        :param float unit_multiple: multiplier for unit. Each value in InkPoint
        will be multiplied by this value on server side. Default is 1.0.

        Azure service common arguments:

        :param float timeout: Timeout in seconds.

        :param dict headers: Custom headers to include in the service request.

        :param str client_request_id: Caller-specified identifier for the request.

        :param callable response_hook: callable that is called with
        (headers, deserialized_response) if the http status is 200.

        Azure pipeline policies:
        https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md

        :rtype: InkRecognitionRoot

        **Exceptions:**

        :raise ServerResponseError: Unexpected Server response that can't be parsed by client.

        :raise ResourceNotFoundError: Indicates URL is invalid.

        :raise ClientAuthenticationError: Authentication issue.

        :raise HttpResponseError: Unclassified error.
        """
        config = self._generate_config(kwargs)
        request_data = self._pack_request(ink_stroke_list, config)
        response = self._send_request(data=request_data, config=config)
        return self._parse_result(response, config)
