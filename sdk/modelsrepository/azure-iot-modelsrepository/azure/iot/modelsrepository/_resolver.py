# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
from queue import Queue
import six.moves.urllib as urllib
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    BearerTokenCredentialPolicy,
)
from .dtmi_conventions import is_valid_dtmi
from .exceptions import ModelError
from ._common import (
    DependencyModeType,
    RemoteProtocolType,
    DiscoveredDependencies,
    IncorrectDtmiCasing,
    InvalidDtmiFormat,
    FailureProcessingRepositoryMetadata,
    SkippingPreProcessedDtmi,
    USER_AGENT,
)
from ._fetcher import HttpFetcher, FilesystemFetcher
from ._model_query import ModelQuery

_LOGGER = logging.getLogger(__name__)


class DtmiResolver(object):
    def __init__(self, location, **kwargs):
        """
        :param fetcher: A Fetcher configured to an endpoint to resolve DTMIs from
        :type fetcher: :class:`azure.iot.modelsrepository._resolver.Fetcher`
        """
        self.fetcher = _create_fetcher(location, **kwargs)

    def __enter__(self):
        self.fetcher.__enter__()
        return self

    def __exit__(self, *exc_details):
        self.fetcher.__exit__(*exc_details)

    def resolve(self, dtmis, dependency_resolution=DependencyModeType.enabled.value):
        """Resolve a DTMI from the configured endpoint and return the resulting JSON model.

        :param list[str] dtmis: DTMIs to resolve
        :param bool expanded_model: Indicates whether to resolve a regular or expanded model

        :raises: ValueError if the DTMI is invalid.
        :raises: ModelError if there is an error with the contents of the JSON model.

        :returns: A dictionary mapping DTMIs to models
        :rtype: dict
        """
        processed_models = {}
        to_process_models = self._prepare_queue(dtmis)
        try_from_expanded = False

        if dependency_resolution == DependencyModeType.enabled.value:
            try:
                metadata = self.fetcher.fetch_metadata()
                if metadata and metadata.get("features") and metadata["features"].get("expanded"):
                    try_from_expanded = True
            except:
                _LOGGER.debug(FailureProcessingRepositoryMetadata)

        while not to_process_models.empty():
            target_dtmi = to_process_models.get()

            if target_dtmi in processed_models:
                _LOGGER.debug(SkippingPreProcessedDtmi.format(target_dtmi))
                continue

            dtdl, expanded_result = self.fetcher.fetch(target_dtmi, try_from_expanded=try_from_expanded)
            model_metadata = ModelQuery(dtdl).parse_model()
            dependencies = model_metadata.dependencies

            # Add dependencies if the result has them
            if expanded_result:
                for name in dependencies:
                    if name not in processed_models:
                        processed_models[name] = dependencies[name]

            # Add dependencies to to_process_queue if manual resolution is needed
            if dependency_resolution == DependencyModeType.enabled.value and not expanded_result:
                if len(dependencies) > 0:
                    _LOGGER.debug(DiscoveredDependencies.format('", "'.join(dependencies)))
                for dep in dependencies:
                    to_process_models.put(dep)

            parsed_dtmi = model_metadata.id
            if target_dtmi != parsed_dtmi:
                raise ModelError(IncorrectDtmiCasing.format(target_dtmi, parsed_dtmi))

            processed_models[parsed_dtmi] = dtdl

        return processed_models

    def _prepare_queue(self, dtmis):
        to_process_models = Queue()
        for dtmi in dtmis:
            if is_valid_dtmi(dtmi):
                to_process_models.put(dtmi)
            else:
                raise ValueError(InvalidDtmiFormat.format(dtmi))
        return to_process_models

def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in [RemoteProtocolType.http.value, RemoteProtocolType.https.value]:
        # HTTP/HTTPS URL
        _LOGGER.debug("Repository Location identified as HTTP/HTTPS endpoint - using HttpFetcher")
        pipeline = _create_pipeline(**kwargs)
        fetcher = HttpFetcher(location, pipeline)
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
        fetcher = HttpFetcher(location, pipeline)
    elif scheme == "file":
        # Filesystem URI
        _LOGGER.debug("Repository Location identified as filesystem URI - using FilesystemFetcher")
        location = location[len("file://") :]
        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)
    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        _LOGGER.debug(
            "Repository Location identified as POSIX fileystem path - using FilesystemFetcher"
        )
        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)
    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        _LOGGER.debug(
            "Repository Location identified as drive letter fileystem path - using FilesystemFetcher"
        )
        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)
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


