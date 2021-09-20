# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import six.moves.urllib as urllib
import re
import logging
import os
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    BearerTokenCredentialPolicy,
)
from . import (
    _resolver,
    _pseudo_parser,
)
from azure.iot.modelsrepository._common import (
    USER_AGENT,
    DependencyModeType,
    RemoteProtocolType,
    DEFAULT_LOCATION,
    DEFAULT_API_VERSION
)

_LOGGER = logging.getLogger(__name__)


class ModelsRepositoryClient(object):
    """Client providing APIs for Models Repository operations"""

    def __init__(
        self,
        credential=None,
        repository_location=DEFAULT_LOCATION,
        **kwargs
    ):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (Any, TokenCredential, str, str) -> None
        """
        :param credential: Credentials to use when connecting to the service.
        :type credential: ~azure.core.credentials.TokenCredential
        :param repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :type repository_location: str
        :keyword str api_version: The API version for the Models Repository Service you wish to
            access.

        For additional request configuration options, please see [core options](https://aka.ms/azsdk/python/options).

        :raises: ValueError if an invalid argument is provided
        """
        repository_location = repository_location if repository_location else DEFAULT_LOCATION
        _LOGGER.debug("Client configured for respository location %s", repository_location)

        # NOTE: depending on how this class develops over time, may need to adjust relationship
        # between some of these objects
        self.fetcher = _create_fetcher(location=repository_location, **kwargs)
        self.resolver = _resolver.DtmiResolver(self.fetcher)
        self._pseudo_parser = _pseudo_parser.PseudoParser(self.resolver)

        # Store api version here (for now). Currently doesn't do anything
        self._api_version = kwargs.get("api_version", DEFAULT_API_VERSION)

    async def __aenter__(self):
        self.fetcher.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        self.fetcher.__aexit__(*exc_details)

    async def close(self):
        # type: () -> None
        """Close the client, preventing future operations"""
        self.__aexit__()

    @distributed_trace_async
    async def get_models(self, dtmis, dependency_resolution=DependencyModeType.enabled.value, **kwargs):
        # type: (Union[List[str], str], str, Any) -> Dict[str, Any]
        """Retrieve a model from the Models Repository.

        :param dtmis: The DTMI(s) for the model(s) you wish to retrieve
        :type dtmis: str or list[str]
        :param dependency_resolution: Dependency resolution mode.
            Possible values:
                - "disabled": Do not resolve model dependencies
                - "enabled": Resolve model dependencies from the repository
            If omitted, the default dependency resolution mode will be "enabled".
        :type dependency_resolution: str

        :raises: ValueError if given an invalid dependency resolution mode
        :raises: ~azure.iot.modelsrepository.ModelError if there is an error parsing the retrieved model(s)
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the model(s) cannot be found in the repository
        :raises: ~azure.core.exceptions.ServiceRequestError if there is an error sending a request for the model(s)
        :raises: ~azure.core.exceptions.ServiceResponseError if the model(s) cannot be retrieved
        :raises: ~azure.core.exceptions.HttpResponseError if a failure response is received

        :returns: Dictionary mapping DTMIs to models
        :rtype: dict
        """
        if isinstance(dtmis, str):
            dtmis = [dtmis]

        if dependency_resolution == DependencyModeType.disabled.value:
            # Simply retrieve the model(s)
            _LOGGER.debug("Getting models w/ dependency resolution mode: disabled")
            _LOGGER.debug("Retrieving model(s): %s...", dtmis)
            model_map = self.resolver.resolve(dtmis)
        elif dependency_resolution == DependencyModeType.enabled.value:
            # Fetch the metadata and ensure dependency resolution is enabled for the repository
            expanded_availiability = False
            try:
                metadata = await self.resolver.resolve_metadata()
                print(f"Metadata: {metadata}")
                if (
                    metadata and
                    metadata.get("features") and
                    metadata["features"].get("expanded")
                ):
                    expanded_availiability = (
                        metadata["features"]["expanded"] == DependencyModeType.enabled.value
                    )
            except:
                # Expanded form is not availiable - will need to fetch dependencies manually
                expanded_availiability = False
                _LOGGER.debug(
                    "Expanded model form is not available in repository - "
                    "will fallback to manual dependency resolution mode"
                )

            _LOGGER.debug("Getting models w/ dependency resolution mode: enabled")

            try:
                _LOGGER.debug("Retrieving expanded model(s): %s...", dtmis)
                model_map = await self.resolver.resolve(dtmis, expanded_model=expanded_availiability)
            except ResourceNotFoundError:
                # Fallback to manual dependency resolution
                _LOGGER.debug(
                    "Could not retrieve model(s) from expanded model DTDL - "
                    "fallback to manual dependency resolution mode"
                )
                _LOGGER.debug("Retrieving model(s): %s...", dtmis)
                model_map = await self.resolver.resolve(dtmis)

            # Fetch dependencies manually if needed
            if not expanded_availiability:
                base_model_list = list(model_map.values())
                _LOGGER.debug("Retrieving model dependencies for %s...", dtmis)
                model_map = await self._pseudo_parser.expand(base_model_list)

        return model_map


def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in [RemoteProtocolType.http.value, RemoteProtocolType.https.value]:
        # HTTP/HTTPS URL
        _LOGGER.debug("Repository Location identified as HTTP/HTTPS endpoint - using HttpFetcher")
        pipeline = _create_pipeline(**kwargs)
        fetcher = _resolver.HttpFetcher(location, pipeline)
    elif scheme == "" and re.search(
        r"\.[a-zA-z]{2,63}$",
        location[: location.find("/") if location.find("/") >= 0 else len(location)],
    ):
        # Web URL with protocol unspecified - default to HTTPS
        _LOGGER.debug(
            "Repository Location identified as remote endpoint without protocol specified - using HttpFetcher"
        )
        location = RemoteProtocolType.https.value + "://" + location
        pipeline = _create_pipeline(**kwargs)
        fetcher = _resolver.HttpFetcher(location, pipeline)
    elif scheme == "file":
        # Filesystem URI
        _LOGGER.debug("Repository Location identified as filesystem URI - using FilesystemFetcher")
        location = location[len("file://") :]
        location = _sanitize_filesystem_path(location)
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        _LOGGER.debug(
            "Repository Location identified as POSIX fileystem path - using FilesystemFetcher"
        )
        location = _sanitize_filesystem_path(location)
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        _LOGGER.debug(
            "Repository Location identified as drive letter fileystem path - using FilesystemFetcher"
        )
        location = _sanitize_filesystem_path(location)
        fetcher = _resolver.FilesystemFetcher(location)
    else:
        raise ValueError("Unable to identify location: {}".format(location))
    return fetcher


def _create_pipeline(base_url=None, credential=None, transport=None, **kwargs):
    """Creates and returns a PipelineClient configured for the provided base_url and kwargs"""
    transport = transport if transport else kwargs.get("transport", RequestsTransport(**kwargs))

    if kwargs.get('policies'):
        policies = kwargs['policies']
    else:
        if credential and hasattr(credential, "get_token"):
            scope = base_url.strip("/") + "/.default"
            authentication_policy = BearerTokenCredentialPolicy(credential, scope)
        elif credential:
            raise ValueError(
                "Please provide an instance from azure-identity or a class that implement the 'get_token protocol"
            )
        else:
            authentication_policy = kwargs.get("authentication_policy")
        policies = [
            kwargs.get("user_agent_policy", UserAgentPolicy(USER_AGENT, **kwargs)),
            kwargs.get("headers_policy", HeadersPolicy(**kwargs)),
            authentication_policy,
            kwargs.get("retry_policy", RetryPolicy(**kwargs)),
            kwargs.get("redirect_policy", RedirectPolicy(**kwargs)),
            kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs)),
            kwargs.get("proxy_policy", ProxyPolicy(**kwargs)),
        ]
    return Pipeline(policies=policies, transport=transport)


def _sanitize_filesystem_path(path):
    """Sanitize the filesystem path to be formatted correctly for the current OS"""
    path = os.path.normcase(path)
    path = os.path.normpath(path)
    return path
