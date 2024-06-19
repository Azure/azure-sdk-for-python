# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import urllib
import re
import logging
import os
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from . import (
    _resolver,
    _pseudo_parser,
    _constants,
)

_LOGGER = logging.getLogger(__name__)


# Public constants exposed to consumers
DEPENDENCY_MODE_TRY_FROM_EXPANDED = "tryFromExpanded"
DEPENDENCY_MODE_DISABLED = "disabled"
DEPENDENCY_MODE_ENABLED = "enabled"


# Convention-private constants
_DEFAULT_LOCATION = "https://devicemodels.azure.com"
_REMOTE_PROTOCOLS = ["http", "https"]
_TRACE_NAMESPACE = "modelsrepository"


class ModelsRepositoryClient(object):
    """Client providing APIs for Models Repository operations"""

    def __init__(self, **kwargs):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (Any) -> None
        """Create a client for working with the Azure IoT Models Repository.

        For additional request configuration options, please see [core options](https://aka.ms/azsdk/python/options).

        :keyword str repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :keyword str dependency_resolution: Dependency resolution mode.
            Possible values:

            - "disabled": Do not resolve model dependencies
            - "enabled": Resolve model dependencies from the repository
            - "tryFromExpanded": Attempt to resolve model and dependencies from an expanded
                model DTDL document in the repository. If this is not successful, will fall
                back on manually resolving dependencies in the repository.

            If using the default repository location, the default dependency resolution mode will
            be "tryFromExpanded". If using a custom repository location, the default dependency
            resolution mode will be "enabled".
        :keyword str api_version: The API version for the Models Repository Service you wish to
            access.
        :raises: ValueError if an invalid argument is provided
        """
        repository_location = kwargs.get("repository_location", _DEFAULT_LOCATION)
        _LOGGER.debug("Client configured for respository location %s", repository_location)

        self.resolution_mode = kwargs.get(
            "dependency_resolution",
            DEPENDENCY_MODE_TRY_FROM_EXPANDED
            if repository_location == _DEFAULT_LOCATION
            else DEPENDENCY_MODE_ENABLED,
        )
        if self.resolution_mode not in [
            DEPENDENCY_MODE_ENABLED,
            DEPENDENCY_MODE_DISABLED,
            DEPENDENCY_MODE_TRY_FROM_EXPANDED,
        ]:
            raise ValueError("Invalid dependency resolution mode: {}".format(self.resolution_mode))
        _LOGGER.debug("Client configured for dependency mode %s", self.resolution_mode)

        # NOTE: depending on how this class develops over time, may need to adjust relationship
        # between some of these objects
        self.fetcher = _create_fetcher(location=repository_location, **kwargs)
        self.resolver = _resolver.DtmiResolver(self.fetcher)
        self._pseudo_parser = _pseudo_parser.PseudoParser(self.resolver)

        # Store api version here (for now). Currently doesn't do anything
        self._api_version = kwargs.get("api_version", _constants.DEFAULT_API_VERSION)

    def __enter__(self):
        self.fetcher.__enter__()
        return self

    def __exit__(self, *exc_details):
        self.fetcher.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """Close the client, preventing future operations"""
        self.__exit__()

    @distributed_trace
    def get_models(self, dtmis, **kwargs):
        # type: (Union[List[str], str], Any) -> Dict[str, Any]
        """Retrieve a model from the Models Repository.

        :param dtmis: The DTMI(s) for the model(s) you wish to retrieve
        :type dtmis: str or list[str]
        :keyword str dependency_resolution: Dependency resolution mode override. This value takes
            precedence over the value set on the client.
            Possible values:
    
            - "disabled": Do not resolve model dependencies
            - "enabled": Resolve model dependencies from the repository
            - "tryFromExpanded": Attempt to resolve model and dependencies from an expanded
                model DTDL document in the repository. If this is not successful, will fall
                back on manually resolving dependencies in the repository

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

        dependency_resolution = kwargs.get("dependency_resolution", self.resolution_mode)

        if dependency_resolution == DEPENDENCY_MODE_DISABLED:
            # Simply retrieve the model(s)
            _LOGGER.debug("Getting models w/ dependency resolution mode: disabled")
            _LOGGER.debug("Retrieving model(s): %s...", dtmis)
            model_map = self.resolver.resolve(dtmis)
        elif dependency_resolution == DEPENDENCY_MODE_ENABLED:
            # Manually resolve dependencies using pseudo-parser
            _LOGGER.debug("Getting models w/ dependency resolution mode: enabled")
            _LOGGER.debug("Retrieving model(s): %s...", dtmis)
            base_model_map = self.resolver.resolve(dtmis)
            base_model_list = list(base_model_map.values())
            _LOGGER.debug("Retrieving model dependencies for %s...", dtmis)
            model_map = self._pseudo_parser.expand(base_model_list)
        elif dependency_resolution == DEPENDENCY_MODE_TRY_FROM_EXPANDED:
            _LOGGER.debug("Getting models w/ dependency resolution mode: tryFromExpanded")
            # Try to use an expanded DTDL to resolve dependencies
            try:
                _LOGGER.debug("Retrieving expanded model(s): %s...", dtmis)
                model_map = self.resolver.resolve(dtmis, expanded_model=True)
            except ResourceNotFoundError:
                # Fallback to manual dependency resolution
                _LOGGER.debug(
                    "Could not retrieve model(s) from expanded model DTDL - "
                    "fallback to manual dependency resolution mode"
                )
                _LOGGER.debug("Retrieving model(s): %s...", dtmis)
                base_model_map = self.resolver.resolve(dtmis)
                base_model_list = list(base_model_map.values())
                _LOGGER.debug("Retrieving model dependencies for %s...", dtmis)
                model_map = self._pseudo_parser.expand(base_model_list)
        else:
            raise ValueError("Invalid dependency resolution mode: {}".format(dependency_resolution))
        return model_map


def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in _REMOTE_PROTOCOLS:
        # HTTP/HTTPS URL
        _LOGGER.debug("Repository Location identified as HTTP/HTTPS endpoint - using HttpFetcher")
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
    elif scheme == "" and re.search(
        r"\.[a-zA-z]{2,63}$",
        location[: location.find("/") if location.find("/") >= 0 else len(location)],
    ):
        # Web URL with protocol unspecified - default to HTTPS
        _LOGGER.debug(
            "Repository Location identified as remote endpoint without protocol specified - using HttpFetcher"
        )
        location = "https://" + location
        pipeline = _create_pipeline(**kwargs)
        fetcher = _resolver.HttpFetcher(location, pipeline)
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


def _create_pipeline(**kwargs):
    """Creates and returns a PipelineClient configured for the provided base_url and kwargs"""
    transport = kwargs.get("transport", RequestsTransport(**kwargs))
    policies = [
        kwargs.get("user_agent_policy", UserAgentPolicy(_constants.USER_AGENT, **kwargs)),
        kwargs.get("headers_policy", HeadersPolicy(**kwargs)),
        kwargs.get("authentication_policy"),
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
