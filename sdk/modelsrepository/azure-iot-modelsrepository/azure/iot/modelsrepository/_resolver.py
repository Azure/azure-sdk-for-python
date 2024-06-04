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
import urllib
from azure.core.pipeline.transport import HttpRequest
from azure.core.exceptions import (
    map_error,
    ResourceNotFoundError,
    HttpResponseError,
    raise_with_traceback,
)
from azure.iot.modelsrepository.exceptions import ModelError
from . import dtmi_conventions

_LOGGER = logging.getLogger(__name__)


class DtmiResolver(object):
    def __init__(self, fetcher):
        """
        :param fetcher: A Fetcher configured to an endpoint to resolve DTMIs from
        :type fetcher: :class:`azure.iot.modelsrepository._resolver.Fetcher`
        """
        self.fetcher = fetcher

    def resolve(self, dtmis, expanded_model=False):
        """Resolve a DTMI from the configured endpoint and return the resulting JSON model.

        :param list[str] dtmis: DTMIs to resolve
        :param bool expanded_model: Indicates whether to resolve a regular or expanded model

        :raises: ValueError if the DTMI is invalid.
        :raises: ModelError if there is an error with the contents of the JSON model.

        :returns: A dictionary mapping DTMIs to models
        :rtype: dict
        """
        model_map = {}
        for dtmi in dtmis:
            # pylint: disable=protected-access
            dtdl_path = dtmi_conventions._convert_dtmi_to_path(dtmi)
            if expanded_model:
                dtdl_path = dtdl_path.replace(".json", ".expanded.json")
            _LOGGER.debug("Model %s located in repository at %s", dtmi, dtdl_path)

            # Errors raised here bubble up
            dtdl = self.fetcher.fetch(dtdl_path)

            if expanded_model:
                # Verify that the DTMI of the "root" model (i.e. the model we requested the
                # expanded DTDL for) within the expanded DTDL matches the DTMI of the request
                if True not in (model["@id"] == dtmi for model in dtdl):
                    raise ModelError("DTMI mismatch on expanded DTDL - Request: {}".format(dtmi))
                # Add all the models in the expanded DTDL to the map
                for model in dtdl:
                    model_map[model["@id"]] = model
            else:
                model = dtdl
                # Verify that the DTMI of the fetched model matches the DTMI of the request
                if model["@id"] != dtmi:
                    raise ModelError(
                        "DTMI mismatch - Request: {}, Response: {}".format(dtmi, model["@id"])
                    )
                # Add the model to the map
                model_map[dtmi] = dtdl
        return model_map


class Fetcher(metaclass=abc.ABCMeta):
    """Interface for fetching from a generic location"""

    @abc.abstractmethod
    def fetch(self, path):
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, *exc_details):
        pass


class HttpFetcher(Fetcher):
    """Fetches JSON data from a web endpoint"""

    error_map = {404: ResourceNotFoundError}

    def __init__(self, base_url, pipeline):
        """
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

    def fetch(self, path):
        """Fetch and return the contents of a JSON file at a given web path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ServiceRequestError if there is an error sending the request
        :raises: ServiceResponseError if no response was received for the request
        :raises: ResourceNotFoundError if the JSON file cannot be found
        :raises: HttpResponseError if there is some other failure during fetch

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug("Fetching %s from remote endpoint", path)
        url = urllib.parse.urljoin(self.base_url, path)

        # Fetch
        request = HttpRequest("GET", url)
        _LOGGER.debug("GET %s", url)
        response = self.pipeline.run(request).http_response
        if response.status_code != 200:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(
                "Failed to fetch from remote endpoint. Status code: {}".format(response.status_code)
            )

        json_response = json.loads(response.text())
        return json_response


class FilesystemFetcher(Fetcher):
    """Fetches JSON data from a local filesystem endpoint"""

    def __init__(self, base_filepath):
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

    def fetch(self, path):
        """Fetch and return the contents of a JSON file at a given filesystem path.

        :param str path: Path to JSON file (relative to the base_filepath of the Fetcher)

        :raises: ResourceNotFoundError if the JSON file cannot be found

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug("Fetching %s from local filesystem", path)
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
        return json.loads(file_str)
