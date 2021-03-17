# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import six.moves.urllib as urllib
import re
from azure.core import PipelineClient
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

        # TODO: Should api_version be a kwarg in the API surface?
        kwargs.setdefault("api_verison", api_version)

        # NOTE: depending on how this class develops over time, may need to adjust relationship
        # between some of these objects
        self.fetcher = _create_fetcher(
            location=repository_location, api_version=api_version, **kwargs
        )
        self.resolver = _resolver.DtmiResolver(self.fetcher)
        self._psuedo_parser = _pseudo_parser.PseudoParser(self.resolver)

    @distributed_trace(name_of_span=_TRACE_NAMESPACE + "/get_models")
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
            model_map = self.resolver.resolve(dtmis)
        elif dependency_resolution == DEPENDENCY_MODE_ENABLED:
            # Manually resolve dependencies using pseudo-parser
            base_model_map = self.resolver.resolve(dtmis)
            base_model_list = list(base_model_map.values())
            model_map = self._psuedo_parser.expand(base_model_list)
        elif dependency_resolution == DEPENDENCY_MODE_TRY_FROM_EXPANDED:
            # Try to use an expanded DTDL to resolve dependencies
            try:
                model_map = self.resolver.resolve(dtmis, expanded_model=True)
            except _resolver.ResolverError:
                # Fallback to manual dependency resolution
                base_model_map = self.resolver.resolve(dtmis)
                base_model_list = list(base_model_map.items())
                model_map = self._psuedo_parser.expand(base_model_list)
        else:
            raise ValueError("Invalid dependency resolution mode: {}".format(dependency_resolution))
        return model_map


class ModelsRepositoryClientConfiguration(Configuration):
    """ModelsRepositoryClient-specific variant of the Azure Core Configuration for Pipelines"""

    def __init__(self, **kwargs):
        super(ModelsRepositoryClientConfiguration, self).__init__(**kwargs)
        # NOTE: There might be some further organization to do here as it's kind of weird that
        # the generic config (which could be used for any remote repository) always will have
        # the default repository's api version stored. Keep this in mind when expanding the
        # scope of the client in the future - perhaps there may need to eventually be unique
        # configs for default repository vs. custom repository endpoints
        self._api_version = kwargs.get("api_version", _constants.DEFAULT_API_VERSION)


def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in _REMOTE_PROTOCOLS:
        # HTTP/HTTPS URL
        client = _create_pipeline_client(base_url=location, **kwargs)
        fetcher = _resolver.HttpFetcher(client)
    elif scheme == "file":
        # Filesystem URI
        location = location[len("file://") :]
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        fetcher = _resolver.FilesystemFetcher(location)
    elif scheme == "" and re.search(r"\.[a-zA-z]{2,63}$", location[: location.find("/")]):
        # Web URL with protocol unspecified - default to HTTPS
        location = "https://" + location
        client = _create_pipeline_client(base_url=location, **kwargs)
        fetcher = _resolver.HttpFetcher(client)
    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        fetcher = _resolver.FilesystemFetcher(location)
    else:
        raise ValueError("Unable to identify location: {}".format(location))
    return fetcher


def _create_pipeline_client(base_url, **kwargs):
    """Creates and returns a PipelineClient configured for the provided base_url and kwargs"""
    transport = kwargs.get("transport", RequestsTransport(**kwargs))
    config = _create_config(**kwargs)
    policies = [
        config.user_agent_policy,
        config.headers_policy,
        config.authentication_policy,
        ContentDecodePolicy(),
        config.proxy_policy,
        config.redirect_policy,
        config.retry_policy,
        config.logging_policy,
    ]
    return PipelineClient(base_url=base_url, config=config, policies=policies, transport=transport)


def _create_config(**kwargs):
    """Creates and returns a ModelsRepositoryConfiguration object"""
    config = ModelsRepositoryClientConfiguration(**kwargs)
    config.headers_policy = kwargs.get("headers_policy", HeadersPolicy(**kwargs))
    config.user_agent_policy = kwargs.get(
        "user_agent_policy", UserAgentPolicy(_constants.USER_AGENT, **kwargs)
    )
    config.authentication_policy = kwargs.get("authentication_policy")
    config.retry_policy = kwargs.get("retry_policy", RetryPolicy(**kwargs))
    config.redirect_policy = kwargs.get("redirect_policy", RedirectPolicy(**kwargs))
    config.logging_policy = kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs))
    config.proxy_policy = kwargs.get("proxy_policy", ProxyPolicy(**kwargs))
    return config
