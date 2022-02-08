# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
import re
from queue import Queue
from typing import TYPE_CHECKING
from urllib.parse import urlparse
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from .dtmi_conventions import is_valid_dtmi
from .exceptions import ModelError
from ._common import (
    DependencyMode,
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
from ._metadata_scheduler import MetadataScheduler
from ._model_query import ModelQuery
from ._models import ModelResult
if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, List


_LOGGER = logging.getLogger(__name__)


class RepositoryHandler(object):
    def __init__(self, location, metadata_enabled, **kwargs):
        # type: (str, bool, Any) -> None
        """
        :param location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
        :type location: str
        :type metadata_expiration: int
        :param metadata_enabled: Whether the client will fetch and cache metadata.
        :type metadata_enabled: bool
        """
        self.fetcher = _create_fetcher(location, **kwargs)
        self._metadata_scheduler = MetadataScheduler(metadata_enabled)
        self._repository_supports_expanded = False

    def __enter__(self):
        self.fetcher.__enter__()
        return self

    def __exit__(self, *exc_details):
        self.fetcher.__exit__(*exc_details)

    def process(self, dtmis, dependency_resolution=DependencyMode.enabled.value, **kwargs):
        # type: (List[str] | str, str, Any) -> ModelResult
        """Process a DTMI from the configured endpoint and return the resulting JSON model.

        If ModelDependencyResolution.Enabled is requested the client will first attempt to fetch
        metadata.json content from the target repository. The metadata object includes supported features
        of the repository.
        If the metadata indicates expanded models are available. The client will try to fetch pre-computed model
        dependencies using .expanded.json.
        If the model expanded form does not exist fall back to computing model dependencies just-in-time.

        :param list[str] dtmis: DTMIs to process
        :param bool expanded_model: Indicates whether to process a regular or expanded model

        :raises: ValueError if the DTMI is invalid.
        :raises: ModelError if there is an error with the contents of the JSON model.

        :returns: A dictionary mapping DTMIs to models
        :rtype: dict
        """
        processed_models = {}
        to_process_models = _prepare_queue(dtmis)

        if (
            dependency_resolution == DependencyMode.enabled.value and
            self._metadata_scheduler.should_fetch_metadata()
        ):
            try:
                metadata = self.fetcher.fetch_metadata(**kwargs)
                self._repository_supports_expanded = (
                    metadata and
                    metadata.features and
                    metadata.features.expanded
                )
                self._metadata_scheduler.mark_as_fetched()
            except (ResourceNotFoundError, HttpResponseError):
                _LOGGER.debug(FAILURE_PROCESSING_REPOSITORY_METADATA)

        # Covers case when the repository supports expanded but dependency resolution is disabled.
        try_from_expanded = (
            dependency_resolution == DependencyMode.enabled.value and
            self._repository_supports_expanded
        )

        while not to_process_models.empty():
            target_dtmi = to_process_models.get()

            if target_dtmi in processed_models:
                info_msg = SKIPPING_PRE_PROCESSED_DTMI.format(target_dtmi)
                _LOGGER.debug(info_msg)
                continue

            info_msg = PROCESSING_DTMI.format(target_dtmi)
            _LOGGER.debug(info_msg)

            fetched_model_result = self.fetcher.fetch(
                target_dtmi, try_from_expanded=try_from_expanded, **kwargs
            )

            # Add dependencies if the result is expanded
            if fetched_model_result.from_expanded:
                expanded = ModelQuery(fetched_model_result.definition).parse_models_from_list()
                for item in expanded:
                    if item not in processed_models:
                        processed_models[item] = expanded[item]
                continue

            model_metadata = ModelQuery(fetched_model_result.definition).parse_model()

            # Add dependencies to to_process_queue if manual resolution is needed
            if dependency_resolution == DependencyMode.enabled.value and not fetched_model_result.from_expanded:
                dependencies = model_metadata.dependencies
                if len(dependencies) > 0:
                    info_msg = DISCOVERED_DEPENDENCIES.format('", "'.join(dependencies))
                    _LOGGER.debug(info_msg)
                for dep in dependencies:
                    to_process_models.put(dep)

            parsed_dtmi = model_metadata.dtmi
            if target_dtmi != parsed_dtmi:
                raise ModelError(
                    GENERIC_GET_MODELS_ERROR.format(target_dtmi) + " " +
                    INVALID_DTMI_FORMAT.format(target_dtmi, parsed_dtmi)
                )

            processed_models[parsed_dtmi] = fetched_model_result.definition

        return ModelResult(contents=processed_models)

def _prepare_queue(dtmis):
    # type: (List[str]) -> Queue
    to_process_models = Queue()
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
    # type: (str, Any) -> HttpFetcher | FilesystemFetcher
    """Return a Fetcher based upon the type of location"""
    scheme = urlparse(location).scheme
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
    # type: (Any) -> Pipeline
    """Creates and returns a PipelineClient configured for the provided kwargs"""
    transport = kwargs.get("transport", RequestsTransport(**kwargs))

    if kwargs.get('policies'):
        policies = kwargs['policies']
    else:
        policies = [
            kwargs.get("user_agent_policy", UserAgentPolicy(USER_AGENT, **kwargs)),
            kwargs.get("headers_policy", HeadersPolicy(**kwargs)),
            kwargs.get("authentication_policy"),
            kwargs.get("retry_policy", RetryPolicy(**kwargs)),
            kwargs.get("redirect_policy", RedirectPolicy(**kwargs)),
            kwargs.get("logging_policy", NetworkTraceLoggingPolicy(**kwargs)),
            kwargs.get("proxy_policy", ProxyPolicy(**kwargs)),
        ]
    return Pipeline(policies=policies, transport=transport)


def _sanitize_filesystem_path(path):
    # type: (str) -> str
    """Sanitize the filesystem path to be formatted correctly for the current OS"""
    path = os.path.normcase(path)
    path = os.path.normpath(path)
    return path
