# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import six.moves.urllib as urllib
import re
import logging
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.transport import RequestsTransport
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
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

    def __init__(
        self, repository_location=None, dependency_resolution=None, api_version=None, **kwargs
    ):
        """
        :param str repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :param str api_version: The API version for the Models Repository Service you wish to
            access.
        :param str dependency_resolution: Dependency resolution mode.
            Possible values:
                - "disabled": Do not resolve model dependencies
                - "enabled": Resolve model dependencies from the repository
                - "tryFromExpanded": Attempt to resolve model and dependencies from an expanded
                        DTDL document in the repository. If this is not successful, will fall back
                        on manually resolving dependencies in the repository
            If using the default repository location, the default dependency resolution mode will
            be "tryFromExpanded". If using a custom repository location, the default dependency
            resolution mode will be "enabled".

        :raises: ValueError if repository_location is invalid
        :raises: ValueError if dependency_resolution is invalid
        """
        repository_location = (
            _DEFAULT_LOCATION if repository_location is None else repository_location
        )
        _LOGGER.debug("Client configured for respository location %s", repository_location)

        if dependency_resolution is None:
            # If using the default repository location, the resolution mode should default to
            # expanded mode because the defeault repo guarantees the existence of expanded DTDLs
            if repository_location == _DEFAULT_LOCATION:
                self.resolution_mode = DEPENDENCY_MODE_TRY_FROM_EXPANDED
            else:
                self.resolution_mode = DEPENDENCY_MODE_ENABLED
        else:
            if dependency_resolution not in [
                DEPENDENCY_MODE_ENABLED,
                DEPENDENCY_MODE_DISABLED,
                DEPENDENCY_MODE_TRY_FROM_EXPANDED,
            ]:
                raise ValueError(
                    "Invalid dependency resolution mode: {}".format(dependency_resolution)
                )
            self.resolution_mode = dependency_resolution
        _LOGGER.debug("Client configured for dependency mode %s", self.resolution_mode)

        # TODO: Should api_version be a kwarg in the API surface?
        kwargs.setdefault("api_verison", api_version)

        # NOTE: depending on how this class develops over time, may need to adjust relationship
        # between some of these objects
        self.fetcher = _create_fetcher(
            location=repository_location, api_version=api_version, **kwargs
        )
        self.resolver = _resolver.DtmiResolver(self.fetcher)
        self._psuedo_parser = _pseudo_parser.PseudoParser(self.resolver)

    @distributed_trace
    def get_models(self, dtmis, dependency_resolution=None):
        """Retrieve a model from the Models Repository.

        :param list[str] dtmis: The DTMIs for the models you wish to retrieve
        :param str dependency_resolution: Dependency resolution mode override. This value takes
            precedence over the value set on the client.
            Possible values:
                - "disabled": Do not resolve model dependencies
                - "enabled": Resolve model dependencies from the repository
                - "tryFromExpanded": Attempt to resolve model and dependencies from an expanded DTDL
                        document in the repository. If this is not successful, will fall back on
                        manually resolving dependencies in the repository

        :raises: ValueError if given an invalid dependency resolution mode
        :raises: ResolverError if there is an error retrieving a model

        :returns: Dictionary mapping DTMIs to models
        :rtype: dict
        """
        # TODO: Use better error surface than the custom ResolverError
        if dependency_resolution is None:
            dependency_resolution = self.resolution_mode

        if dependency_resolution == DEPENDENCY_MODE_DISABLED:
            # Simply retrieve the model(s)
            _LOGGER.debug("Getting models w/ dependency resolution mode: disabled")
            _LOGGER.debug("Retreiving model(s): %s...", dtmis)
            model_map = self.resolver.resolve(dtmis)
        elif dependency_resolution == DEPENDENCY_MODE_ENABLED:
            # Manually resolve dependencies using pseudo-parser
            _LOGGER.debug("Getting models w/ dependency resolution mode: enabled")
            _LOGGER.debug("Retreiving model(s): %s...", dtmis)
            base_model_map = self.resolver.resolve(dtmis)
            base_model_list = list(base_model_map.values())
            _LOGGER.debug("Retreiving model dependencies for %s...", dtmis)
            model_map = self._psuedo_parser.expand(base_model_list)
        elif dependency_resolution == DEPENDENCY_MODE_TRY_FROM_EXPANDED:
            _LOGGER.debug("Getting models w/ dependency resolution mode: tryFromExpanded")
            # Try to use an expanded DTDL to resolve dependencies
            try:
                _LOGGER.debug("Retreiving expanded model(s): %s...", dtmis)
                model_map = self.resolver.resolve(dtmis, expanded_model=True)
            except _resolver.ResolverError:
                # Fallback to manual dependency resolution
                _LOGGER.debug("Could not retreive model(s) from expanded DTDL - fallback to manual dependency resolution mode")
                _LOGGER.debug("Retreiving model(s): %s...", dtmis)
                base_model_map = self.resolver.resolve(dtmis)
                base_model_list = list(base_model_map.items())
                _LOGGER.debug("Retreiving model dependencies for %s...", dtmis)
                model_map = self._psuedo_parser.expand(base_model_list)
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
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        _LOGGER.debug("Repository Location identified as POSIX fileystem path - using FilesystemFetcher")
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme == "" and re.search(r"\.[a-zA-z]{2,63}$", location[: location.find("/")]):
        # Web URL with protocol unspecified - default to HTTPS
        _LOGGER.debug("Repository Location identified as remote endpoint without protocol specified - using HttpFetcher")
        location = "https://" + location
        pipeline = _create_pipeline(**kwargs)
        fetcher = _resolver.HttpFetcher(location, pipeline)
    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        _LOGGER.debug("Repository Location identified as drive letter fileystem path - using FilesystemFetcher")
        fetcher = _resolver.FilesystemFetcher(location)
    else:
        raise ValueError("Unable to identify location: {}".format(location))
    return fetcher


def _create_pipeline(**kwargs):
    """Creates and returns a PipelineClient configured for the provided base_url and kwargs"""
    transport = kwargs.get("transport", RequestsTransport(**kwargs))
    policies = _create_policies_list(**kwargs)
    return Pipeline(policies=policies, transport=transport)


def _create_policies_list(**kwargs):
    """Creates and returns a list of policies based on provided kwargs (or default policies)"""
    policies = [
        kwargs.get("user_agent_policy", UserAgentPolicy(_constants.USER_AGENT, **kwargs)),
        kwargs.get("headers_policy", HeadersPolicy(**kwargs)),
        kwargs.get("retry_policy", RetryPolicy(**kwargs)),
        kwargs.get("redirect_policy", RedirectPolicy(**kwargs)),
        kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs)),
        kwargs.get("proxy_policy", ProxyPolicy(**kwargs)),
    ]
    auth_policy = kwargs.get("authentication_policy")
    if auth_policy:
        policies.append(auth_policy)
    return policies
