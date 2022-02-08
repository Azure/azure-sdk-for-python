# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
import io
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from azure.core.pipeline.transport import HttpRequest
from azure.core.exceptions import (
    map_error,
    ResourceNotFoundError,
    HttpResponseError,
    raise_with_traceback,
)
from .dtmi_conventions import _convert_dtmi_to_path
from ._common import (
    ERROR_FETCHING_MODEL_CONTENT,
    FETCHING_MODEL_CONTENT,
    METADATA_FILE,
)
from ._models import FetchModelResult, ModelsRepositoryMetadata


if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

    from azure.core.pipeline import Pipeline


_LOGGER = logging.getLogger(__name__)


class Fetcher(ABC):
    """Interface for fetching from a generic location"""

    def fetch(self, dtmi="", try_from_expanded=True, **kwargs):
        # type: (str, bool, Any) -> FetchModelResult
        """
        Fetch and return the contents of the given DTMI. If try_from_expanded
        is true, will try the expanded form first and fall back to non-expanded if needed.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)
        :param bool try_from_expanded: Whether the path should be expanded

        :returns: FetchModelResult representing data at the path and if the expanded form was used.
        :rtype: FetchModelResult
        """
        dtdl_path = _convert_dtmi_to_path(dtmi, expanded=try_from_expanded)
        if try_from_expanded:
            try:
                info_msg = FETCHING_MODEL_CONTENT.format(dtdl_path)
                _LOGGER.debug(info_msg)

                return FetchModelResult(self._fetch_model_data(dtdl_path, **kwargs), dtdl_path)
            except (ResourceNotFoundError, HttpResponseError):
                # Fallback to non expanded model
                info_msg = ERROR_FETCHING_MODEL_CONTENT.format(dtmi)
                _LOGGER.debug(info_msg)
                dtdl_path = _convert_dtmi_to_path(dtmi, expanded=False)

        info_msg = FETCHING_MODEL_CONTENT.format(dtdl_path)
        _LOGGER.debug(info_msg)

        # Let errors from this bubble up
        return FetchModelResult(self._fetch_model_data(dtdl_path, **kwargs), dtdl_path)

    def fetch_metadata(self, **kwargs):
        # type: (Any) -> ModelsRepositoryMetadata
        """Fetch and return the repository metadata

        :returns: metadata file contents
        :rtype: str
        """
        metadata = self._fetch_model_data(METADATA_FILE, **kwargs)
        return ModelsRepositoryMetadata.from_json_str(metadata)

    @abstractmethod
    def _fetch_model_data(self, path):
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, *exc_details):
        pass


class HttpFetcher(Fetcher):
    """Fetches JSON data from a web endpoint"""

    error_map = {404: ResourceNotFoundError}

    def __init__(self, base_url, pipeline):
        # type: (str, Pipeline) -> None
        """
        :param base_url: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
        :type base_url: str
        :param pipeline: Pipeline (pre-configured)
        :type pipeline: :class:`azure.core.pipeline.Pipeline`
        """
        self.pipeline = pipeline
        self.base_url = base_url

    def __enter__(self):
        self.pipeline.__enter__()
        return self

    def __exit__(self, *exc_details):
        self.pipeline.__exit__(*exc_details)

    def _fetch_model_data(self, path="", **kwargs):
        # type: (str, Any) -> str
        """Fetch and return the contents of a JSON file at a given web path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ServiceRequestError if there is an error sending the request
        :raises: ServiceResponseError if no response was received for the request
        :raises: ResourceNotFoundError if the JSON file cannot be found
        :raises: HttpResponseError if there is some other failure during fetch

        :returns: file contents at the path
        :rtype: str
        """
        url = urljoin(self.base_url, path)

        # Fetch
        request = HttpRequest("GET", url)
        info_msg = "GET {}".format(url)
        _LOGGER.debug(info_msg)

        response = self.pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(
                "Failed to fetch from remote endpoint. Status code: {}".format(response.status_code)
            )
        return response


class FilesystemFetcher(Fetcher):
    """Fetches JSON data from a local filesystem endpoint"""

    def __init__(self, base_filepath):
        # type: (str) -> None
        """
        :param str base_filepath: The base filepath for fetching from
        """
        self.base_filepath = base_filepath

    def __enter__(self):
        # Nothing is required here for filesystem
        return self

    def __exit__(self, *exc_details):
        # Nothing is required here for filesystem
        pass

    def _fetch_model_data(self, path=""):
        # type: (str) -> str
        """Fetch and return the contents of a JSON file at a given filesystem path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ResourceNotFoundError if the JSON file cannot be found

        :returns: file contents at the path
        :rtype: str
        """
        abs_path = os.path.join(self.base_filepath, path)
        abs_path = os.path.normpath(abs_path)

        # Fetch
        try:
            info_msg = "File open on {}".format(abs_path)
            _LOGGER.debug(info_msg)

            with io.open(abs_path, encoding="utf-8-sig") as f:
                file_str = f.read()
        except OSError:
            raise_with_traceback(ResourceNotFoundError, message="Could not open file")
        return file_str
