# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
import re
import six.moves.urllib as urllib
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    AsyncRetryPolicy,
    AsyncRedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from ..dtmi_conventions import is_valid_dtmi
from ..exceptions import ModelError
from .._common import (
    DependencyModeType,
    RemoteProtocolType,
    DISCOVERED_DEPENDENCIES,
    GENERIC_GET_MODELS_ERROR,
    INVALID_DTMI_FORMAT,
    FAILURE_PROCESSING_REPOSITORY_METADATA,
    PROCESSING_DTMI,
    SKIPPING_PRE_PROCESSED_DTMI,
    USER_AGENT,
    FETCHER_INIT_MSG,
)
from ._fetcher import HttpFetcher, FilesystemFetcher
from .._model_query import ModelQuery

try:
    import queue
except ImportError:
    import Queue as queue


_LOGGER = logging.getLogger(__name__)


class DtmiResolver(object):
    def __init__(self, location, **kwargs):
        """
        :param location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
        :type location: str
        """
        self.fetcher = _create_fetcher(location, **kwargs)

    @distributed_trace_async
    async def __aenter__(self):
        await self.fetcher.__aenter__()
        return self

    @distributed_trace_async
    async def __aexit__(self, *exc_details):
        await self.fetcher.__aexit__(*exc_details)

    @distributed_trace_async
    async def resolve(self, dtmis, dependency_resolution=DependencyModeType.enabled.value):
        """Resolve a DTMI from the configured endpoint and return the resulting JSON model.

        :param list[str] dtmis: DTMIs to resolve
        :param bool expanded_model: Indicates whether to resolve a regular or expanded model

        :raises: ValueError if the DTMI is invalid.
        :raises: ModelError if there is an error with the contents of the JSON model.

        :returns: A dictionary mapping DTMIs to models
        :rtype: dict
        """
        processed_models = {}
        to_process_models = await _prepare_queue(dtmis)
        try_from_expanded = False

        if dependency_resolution == DependencyModeType.enabled.value:
            try:
                metadata = await self.fetcher.fetch_metadata()
                if metadata and metadata.get("features") and metadata["features"].get("expanded"):
                    try_from_expanded = True
            except (ResourceNotFoundError, HttpResponseError):
                _LOGGER.debug(FAILURE_PROCESSING_REPOSITORY_METADATA)

        while not to_process_models.empty():
            target_dtmi = to_process_models.get()

            if target_dtmi in processed_models:
                info_msg = SKIPPING_PRE_PROCESSED_DTMI.format(target_dtmi)
                _LOGGER.debug(info_msg)
                continue

            info_msg = PROCESSING_DTMI.format(target_dtmi)
            _LOGGER.debug(info_msg)

            dtdl, expanded_result = await self.fetcher.fetch(target_dtmi, try_from_expanded=try_from_expanded)

            # Add dependencies if the result is expanded
            if expanded_result:
                for item in dtdl:
                    model_metadata = ModelQuery(item).parse_model()
                    if model_metadata.dtmi not in processed_models:
                        processed_models[model_metadata.dtmi] = item

                continue

            model_metadata = ModelQuery(dtdl).parse_model()
            dependencies = model_metadata.dependencies

            # Add dependencies to to_process_queue if manual resolution is needed
            if dependency_resolution == DependencyModeType.enabled.value and not expanded_result:
                if len(dependencies) > 0:
                    info_msg = DISCOVERED_DEPENDENCIES.format('", "'.join(dependencies))
                    _LOGGER.debug(info_msg)
                for dep in dependencies:
                    to_process_models.put(dep)

            parsed_dtmi = model_metadata.dtmi
            if target_dtmi != parsed_dtmi:
                raise ModelError(
                    GENERIC_GET_MODELS_ERROR.format(target_dtmi) +
                    INVALID_DTMI_FORMAT.format(target_dtmi, parsed_dtmi)
                )

            processed_models[parsed_dtmi] = dtdl

        return processed_models


@distributed_trace_async
async def _prepare_queue(dtmis):
    to_process_models = queue.Queue()
    for dtmi in dtmis:
        if is_valid_dtmi(dtmi):
            to_process_models.put(dtmi)
        else:
            raise ValueError(
                GENERIC_GET_MODELS_ERROR.format(dtmi) +
                INVALID_DTMI_FORMAT.format(dtmi)
            )
    return to_process_models


def _create_fetcher(location, **kwargs):
    """Return a Fetcher based upon the type of location"""
    scheme = urllib.parse.urlparse(location).scheme
    if scheme in [RemoteProtocolType.http.value, RemoteProtocolType.https.value]:
        # HTTP/HTTPS URL
        info_msg = FETCHER_INIT_MSG.format("HTTP/HTTPS endpoint", "HttpFetcher")
        _LOGGER.debug(info_msg)

        pipeline = _create_pipeline(**kwargs)
        fetcher = HttpFetcher(location, pipeline)

    elif scheme == "" and re.search(
        r"\.[a-zA-z]{2,63}$",
        location[: location.find("/") if location.find("/") >= 0 else len(location)],
    ):
        # Web URL with protocol unspecified - default to HTTPS
        info_msg = FETCHER_INIT_MSG.format(
            "remote endpoint without protocol specified", "HttpFetcher"
        )
        _LOGGER.debug(info_msg)

        location = RemoteProtocolType.https.value + "://" + location
        pipeline = _create_pipeline(**kwargs)
        fetcher = HttpFetcher(location, pipeline)

    elif scheme == "file":
        # Filesystem URI
        info_msg = FETCHER_INIT_MSG.format("filesystem URI", "FilesystemFetcher")
        _LOGGER.debug(info_msg)

        location = location[len("file://") :]
        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)

    elif scheme == "" and location.startswith("/"):
        # POSIX filesystem path
        info_msg = FETCHER_INIT_MSG.format("POSIX fileystem path", "FilesystemFetcher")
        _LOGGER.debug(info_msg)

        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)

    elif scheme != "" and len(scheme) == 1 and scheme.isalpha():
        # Filesystem path using drive letters (e.g. "C:", "D:", etc.)
        info_msg = FETCHER_INIT_MSG.format("drive letter fileystem path", "FilesystemFetcher")
        _LOGGER.debug(info_msg)

        location = _sanitize_filesystem_path(location)
        fetcher = FilesystemFetcher(location)

    else:
        raise ValueError("Unable to identify location: {}".format(location))
    return fetcher


def _create_pipeline(**kwargs):
    """Creates and returns a PipelineClient configured for the provided base_url and kwargs"""
    from azure.core.pipeline.transport import AioHttpTransport
    transport = kwargs.get("transport", AioHttpTransport(**kwargs))

    if kwargs.get('policies'):
        policies = kwargs['policies']
    else:
        policies = [
            kwargs.get("user_agent_policy", UserAgentPolicy(USER_AGENT, **kwargs)),
            kwargs.get("headers_policy", HeadersPolicy(**kwargs)),
            kwargs.get("authentication_policy"),
            kwargs.get("retry_policy", AsyncRetryPolicy(**kwargs)),
            kwargs.get("redirect_policy", AsyncRedirectPolicy(**kwargs)),
            kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs)),
            kwargs.get("proxy_policy", ProxyPolicy(**kwargs)),
        ]
    return AsyncPipeline(policies=policies, transport=transport)


def _sanitize_filesystem_path(path):
    """Sanitize the filesystem path to be formatted correctly for the current OS"""
    path = os.path.normcase(path)
    path = os.path.normpath(path)
    return path
