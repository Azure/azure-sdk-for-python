# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import six.moves.urllib as urllib
import re
from azure.core import PipelineClient
from azure.core.pipeline.transport import RequestsTransport
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    BearerTokenCredentialPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from . import resolver
from . import pseudo_parser


# Public constants exposed to consumers
DEPENDENCY_MODE_TRY_FROM_EXPANDED = "tryFromExpanded"
DEPENDENCY_MODE_DISABLED = "disabled"
DEPENDENCY_MODE_ENABLED = "enabled"


# Convention-private constants
_DEFAULT_LOCATION = "https://devicemodels.azure.com"
_DEFAULT_API_VERSION = "2021-02-11"
_REMOTE_PROTOCOLS = ["http", "https"]


class ModelsRepositoryClient(object):
    """Client providing APIs for Models Repository operations"""

    # TODO: Should api_version be a kwarg?
    def __init__(self, repository_location=None, api_version=None, **kwargs):
        """
        :param str repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :param str api_version: The API version for the Models Repository Service you wish to
            access.

        :raises: ValueError if repository_location is invalid
        """
        repository_location = (
            _DEFAULT_LOCATION if repository_location is None else repository_location
        )
        # api_version = _DEFAULT_API_VERSION if api_version is None else api_version

        kwargs.setdefault("api_verison", api_version)

        # NOTE: depending on how this class develops over time, may need to adjust relationship
        # between some of these objects
        self.fetcher = _create_fetcher(
            location=repository_location, api_version=api_version, **kwargs
        )
        self.resolver = resolver.DtmiResolver(self.fetcher)
        self.pseudo_parser = pseudo_parser.PseudoParser(self.resolver)

    def get_models(self, dtmis, dependency_resolution=DEPENDENCY_MODE_DISABLED):
        """Retrieve a model from the Models Repository.

        :param list[str] dtmis: The DTMIs for the models you wish to retrieve
        :param str dependency_resolution : Dependency resolution mode. Possible values:
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
        # TODO: If not ResolverError, then what?
        if dependency_resolution == DEPENDENCY_MODE_DISABLED:
            # Simply retrieve the model(s)
            model_map = self.resolver.resolve(dtmis)
        elif dependency_resolution == DEPENDENCY_MODE_ENABLED:
            # Manually resolve dependencies using pseudo-parser
            base_model_map = self.resolver.resolve(dtmis)
            base_model_list = list(base_model_map.values())
            model_map = self.pseudo_parser.expand(base_model_list)
        elif dependency_resolution == DEPENDENCY_MODE_TRY_FROM_EXPANDED:
            # Try to use an expanded DTDL to resolve dependencies
            try:
                model_map = self.resolver.resolve(dtmis, expanded_model=True)
            except resolver.ResolverError:
                # Fallback to manual dependency resolution
                base_model_map = self.resolver.resolve(dtmis)
                base_model_list = list(base_model_map.items())
                model_map = self.pseudo_parser.expand(base_model_list)
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
        self._api_version = kwargs.get("api_version", _DEFAULT_API_VERSION)


def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in _REMOTE_PROTOCOLS:
        # HTTP/HTTPS URL
        client = _create_pipeline_client(base_url=location, **kwargs)
        fetcher = resolver.HttpFetcher(client)
    elif scheme == "file":
        # Filesystem URI
        location = location[len("file://") :]
        fetcher = resolver.FilesystemFetcher(location)
    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        fetcher = resolver.FilesystemFetcher(location)
    elif scheme == "" and re.search(r"\.[a-zA-z]{2,63}$", location[: location.find("/")]):
        # Web URL with protocol unspecified - default to HTTPS
        location = "https://" + location
        client = _create_pipeline_client(base_url=location, **kwargs)
        fetcher = resolver.HttpFetcher(client)
    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        fetcher = resolver.FilesystemFetcher(location)
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
    config.headers_policy = kwargs.get(
        "headers_policy", HeadersPolicy({"CustomHeader": "Value"}, **kwargs)
    )
    config.user_agent_policy = kwargs.get(
        "user_agent_policy", UserAgentPolicy("ServiceUserAgentValue", **kwargs)
    )
    config.authentication_policy = kwargs.get("authentication_policy")
    config.retry_policy = kwargs.get("retry_policy", RetryPolicy(**kwargs))
    config.redirect_policy = kwargs.get("redirect_policy", RedirectPolicy(**kwargs))
    config.logging_policy = kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs))
    config.proxy_policy = kwargs.get("proxy_policy", ProxyPolicy(**kwargs))
    return config
