# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import typing
import jwt
import six
import base64
import hmac
import hashlib
from datetime import datetime, timedelta, tzinfo
from typing import TYPE_CHECKING
import importlib


from ._version import VERSION
from ._client import BatchServiceClient as GenerateBatchServiceClient
from ._configuration import BatchServiceClientConfiguration
#from ._batch_service_client import BatchServiceClient as GenerateBatchServiceClient

from msrest import Deserializer, Serializer
from azure.core.pipeline import policies
from azure.core import PipelineClient
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from msrest import Serializer
from msrest.serialization import TZ_UTC
from azure.core.pipeline import PipelineRequest
from .operations import AccountOperations, ApplicationOperations, CertificateOperations, ComputeNodeExtensionOperations, ComputeNodeOperations, FileOperations, JobOperations, JobScheduleOperations, PoolOperations, TaskOperations

try:
    from urlparse import urlparse, parse_qs

except ImportError:
    from urllib.parse import urlparse, parse_qs

__all__ = ['BatchServiceClient','BatchSharedKeyCredential']  # Add all objects you want publicly available to users at this package level

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Optional, TypeVar, Union, List
    from ._operations._operations import JSONType

    T = TypeVar('T')
    ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Type, TypeVar, Any, Union, Dict, List

    ClientType = TypeVar("ClientType", bound="BatchServiceClient")

    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineRequest


class BatchSharedKeyCredential:
    """Credential type used for authenticating to an Azure Metrics Advisor service.

    :param str subscription_key: The subscription key
    :param str api_key: The api key
    :raises: TypeError
    """
    def __init__(self, account_name: str, key: str) -> None:

        self._account_name: str = account_name
        self._key: str = key

    @property
    def account_name(self) -> str:
        """The value of the api key.

        :rtype: str
        """
        return self._account_name

    @property
    def key(self) -> str:
        """The value of the api key.

        :rtype: str
        """
        return self._key


class BatchSharedKeyAuthPolicy(SansIOHTTPPolicy):


    headers_to_sign = [
        'content-encoding',
        'content-language',
        'content-length',
        'content-md5',
        'content-type',
        'date',
        'if-modified-since',
        'if-match',
        'if-none-match',
        'if-unmodified-since',
        'range']

    def __init__(self, credential: BatchSharedKeyCredential):
        super(BatchSharedKeyAuthPolicy, self).__init__()
        self._account_name = credential.account_name
        self._key = credential.key

    def on_request(self, request: PipelineRequest):
        if not request.http_request.headers.get('ocp-date'):
            now = datetime.utcnow()
            now = now.replace(tzinfo=TZ_UTC)
            request.http_request.headers['ocp-date'] = Serializer.serialize_rfc(now)

        url = urlparse(request.http_request.url)
        uri_path = url.path

        # method to sign
        string_to_sign = request.http_request.method + '\n'

        # get headers to sign
        request_header_dict = {
            key.lower(): val for key, val in request.http_request.headers.items() if val}

        request_headers = [
            str(request_header_dict.get(x, '')) for x in self.headers_to_sign]

        string_to_sign += '\n'.join(request_headers) + '\n'

        # get ocp- header to sign
        ocp_headers = []
        for name, value in request.http_request.headers.items():
            if 'ocp-' in name and value:
                ocp_headers.append((name.lower(), value))

        for name, value in sorted(ocp_headers):
            string_to_sign += "{}:{}\n".format(name, value)

        # get account_name and uri path to sign
        string_to_sign += "/{}{}".format(self._account_name, uri_path)

        # get query string to sign if it is not table service
        query_to_sign = parse_qs(url.query)

        for name in sorted(query_to_sign.keys()):
            value = query_to_sign[name][0]
            if value:
                string_to_sign += "\n{}:{}".format(name, value)

        # sign the request
        auth_string = "SharedKey {}:{}".format(
            self._account_name, self._sign_string(string_to_sign))

        request.http_request.headers["Authorization"] = auth_string

        return super().on_request(request)

    def _sign_string(self, string_to_sign):

        _key = self._key.encode('utf-8')
        string_to_sign = string_to_sign.encode('utf-8')

        try:
            key = base64.b64decode(_key)
        except TypeError:
            raise ValueError("Invalid key value: {}".format(self._key))

        signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
        digest = signed_hmac_sha256.digest()

        return base64.b64encode(digest).decode('utf-8')


class BatchServiceClient(GenerateBatchServiceClient):
    """BatchServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, batch_url: str, credential: str, **kwargs):
        super().__init__(
            batch_url=batch_url,
            credential=credential,
            authentication_policy=kwargs.pop("authentication_policy", BatchSharedKeyAuthPolicy(credential)),
            **kwargs
        )

def patch_sdk():
    curr_package = importlib.import_module("azure.batch")
    curr_package.BatchServiceClient = BatchServiceClient
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """