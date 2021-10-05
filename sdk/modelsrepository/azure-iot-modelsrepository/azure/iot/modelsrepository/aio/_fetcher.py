# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import json
import abc
import os
import io
import six
import re
import urllib
from azure.core.pipeline.transport import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import (
    map_error,
    ResourceNotFoundError,
    HttpResponseError,
    raise_with_traceback,
)
from ..dtmi_conventions import METADATA_FILE, _convert_dtmi_to_path
from .._common import ErrorFetchingModelContent, FetchingModelContent

_LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Fetcher(object):
    """Interface for fetching from a generic location"""

    @distributed_trace_async
    async def fetch(self, dtmi="", try_from_expanded=True):
        """Fetch and return the contents of the given DTMI. If try_from_expanded
            is true, will try the expanded form first and fall back to non expanded if needed.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)
        :param bool try_from_expanded: Whether the path should be expanded

        :returns: Tuple representing JSON data at the path and if the expanded form was used.
        :rtype: (JSON object, bool)
        """
        dtdl_path = _convert_dtmi_to_path(dtmi, expanded=try_from_expanded)
        if try_from_expanded:
            try:
                return (await self._fetch_model_data(dtdl_path), True)
            except:
                # Fallback to non expanded model
                _LOGGER.debug(ErrorFetchingModelContent.format(dtmi))
                dtdl_path = _convert_dtmi_to_path(dtmi, expanded=False)

        # Let errors from this bubble up
        return (await self._fetch_model_data(dtdl_path), False)

    @distributed_trace_async
    async def fetch_metadata(self):
        """Fetch and return the repository metadata

        :returns: JSON object representing the repository metadata
        :rtype: JSON object
        """
        return await self._fetch_model_data(METADATA_FILE)

    @abc.abstractmethod
    @distributed_trace_async
    async def _fetch_model_data(self, path):
        pass

    @abc.abstractmethod
    @distributed_trace_async
    async def __aenter__(self):
        pass

    @abc.abstractmethod
    @distributed_trace_async
    async def __aexit__(self, *exc_details):
        pass


class HttpFetcher(Fetcher):
    """Fetches JSON data from a web endpoint"""

    error_map = {404: ResourceNotFoundError}

    def __init__(self, base_url, pipeline):
        """
        :param pipeline: Pipeline (pre-configured)
        :type pipeline: :class:`azure.core.pipeline.AsyncPipeline`
        """
        self.pipeline = pipeline
        self.base_url = base_url

    @distributed_trace_async
    async def __aenter__(self):
        await self.pipeline.__aenter__()
        return self

    @distributed_trace_async
    async def __aexit__(self, *exc_details):
        await self.pipeline.__aexit__(*exc_details)

    @distributed_trace_async
    async def _fetch_model_data(self, path=""):
        """Fetch and return the contents of a JSON file at a given web path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ServiceRequestError if there is an error sending the request
        :raises: ServiceResponseError if no response was received for the request
        :raises: ResourceNotFoundError if the JSON file cannot be found
        :raises: HttpResponseError if there is some other failure during fetch

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug(FetchingModelContent.format(path))
        url = urllib.parse.urljoin(self.base_url, path)

        # Fetch
        request = HttpRequest("GET", url)
        _LOGGER.debug("GET %s", url)

        pipeline_result = await self.pipeline.run(request)
        response = pipeline_result.http_response
        if response.status_code != 200:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(
                "Failed to fetch from remote endpoint. Status code: {}".format(response.status_code)
            )

        # Remove trailing commas if needed
        content = re.sub(",[ \t\r\n]+}", "}", response.text())
        content = re.sub(",[ \t\r\n]+\]", "]", content)
        json_response = json.loads(content)
        return json_response


class FilesystemFetcher(Fetcher):
    """Fetches JSON data from a local filesystem endpoint"""

    def __init__(self, base_filepath):
        """
        :param str base_filepath: The base filepath for fetching from
        """
        self.base_filepath = base_filepath

    @distributed_trace_async
    async def __aenter__(self):
        # Nothing is required here for filesystem
        return self

    @distributed_trace_async
    async def __aexit__(self, *exc_details):
        # Nothing is required here for filesystem
        pass

    @distributed_trace_async
    async def _fetch_model_data(self, path=""):
        """Fetch and return the contents of a JSON file at a given filesystem path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ResourceNotFoundError if the JSON file cannot be found

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug(FetchingModelContent.format(path))
        abs_path = os.path.join(self.base_filepath, path)
        abs_path = os.path.normpath(abs_path)

        # Fetch
        try:
            _LOGGER.debug("File open on %s", abs_path)
            with io.open(abs_path, encoding="utf-8-sig") as f:
                file_str = f.read()
        except (OSError, IOError):
            # In Python 3 a FileNotFoundError is raised when a file doesn't exist.
            # In Python 2 an IOError is raised when a file doesn't exist.
            # Both of these errors are inherited from OSError, so we use this to catch them both.
            # The semantics would ideally be better, but this is the price of supporting both.
            raise_with_traceback(ResourceNotFoundError, message="Could not open file")

        # Remove trailing commas if needed
        content = re.sub(",[ \t\r\n]+}", "}", file_str)
        content = re.sub(",[ \t\r\n]+\]", "]", content)
        return json.loads(content)
