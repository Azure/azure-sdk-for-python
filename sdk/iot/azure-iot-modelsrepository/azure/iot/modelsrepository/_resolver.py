# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import json
import abc
import os
import six
from . import dtmi_conventions
from ._chainable_exception import ChainableException

_LOGGER = logging.getLogger(__name__)


class ResolverError(ChainableException):
    pass


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

        :raises: ValueError if the DTMI is invalid
        :raises: ResolverError if the DTMI cannot be resolved to a model

        :returns: A dictionary mapping DTMIs to models
        :rtype: dict
        """
        model_map = {}
        for dtmi in dtmis:
            dtdl_path = dtmi_conventions._convert_dtmi_to_path(dtmi)
            if expanded_model:
                dtdl_path = dtdl_path.replace(".json", ".expanded.json")
            _LOGGER.debug("Model %s located in repository at %s", dtmi, dtdl_path)

            try:
                dtdl = self.fetcher.fetch(dtdl_path)
            except FetcherError as e:
                raise ResolverError("Failed to resolve dtmi: {}".format(dtmi), cause=e)

            if expanded_model:
                # Verify that the DTMI of the "root" model (i.e. the model we requested the
                # expanded DTDL for) within the expanded DTDL matches the DTMI of the request
                if True not in (model["@id"] == dtmi for model in dtdl):
                    raise ResolverError("DTMI mismatch on expanded DTDL - Request: {}".format(dtmi))
                # Add all the models in the expanded DTDL to the map
                for model in dtdl:
                    model_map[model["@id"]] = model
            else:
                model = dtdl
                # Verify that the DTMI of the fetched model matches the DTMI of the request
                if model["@id"] != dtmi:
                    raise ResolverError(
                        "DTMI mismatch - Request: {}, Response: {}".format(dtmi, model["@id"])
                    )
                # Add the model to the map
                model_map[dtmi] = dtdl
        return model_map


class FetcherError(ChainableException):
    pass


@six.add_metaclass(abc.ABCMeta)
class Fetcher(object):
    """Interface for fetching from a generic location"""

    @abc.abstractmethod
    def fetch(self, path):
        pass


class HttpFetcher(Fetcher):
    """Fetches JSON data from a web endpoint"""

    def __init__(self, http_client):
        """
        :param http_client: PipelineClient that has been configured for an endpoint
        :type http_client: :class:`azure.core.PipelineClient`
        """
        self.client = http_client

    def fetch(self, path):
        """Fetch and return the contents of a JSON file at a given web path.
        The path can be relative to the path configured in the Fetcher's HttpClient,
        or it can be an absolute path.

        :raises: FetcherError if data cannot be fetched

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug("Fetching %s from remote endpoint", path)
        request = self.client.get(url=path)
        response = self.client._pipeline.run(request).http_response
        if response.status_code != 200:
            raise FetcherError("Failed to fetch from remote endpoint")
        json_response = json.loads(response.text())
        return json_response


class FilesystemFetcher(Fetcher):
    """Fetches JSON data from a local filesystem endpoint"""

    def __init__(self, base_path):
        """
        :param str base_path: The base filepath for fetching from
        """
        self.base_path = base_path

    def fetch(self, path):
        """Fetch and return the contents of a JSON file at a given filesystem path.
        The path can be relative to the Fetcher's base_path, or it can be an absolute path.

        :raises: FetcherError if data cannot be fetched

        :returns: JSON data at the path
        :rtype: JSON object
        """
        _LOGGER.debug("Fetching %s from local filesystem", path)
        # Format path
        path = os.path.join(self.base_path, path)
        path = os.path.normcase(path)
        path = os.path.normpath(path)

        # TODO: Ensure support for relative and absolute paths
        # TODO: Need robust suite of testing for different types of paths

        # Fetch
        try:
            _LOGGER.debug("File open on %s", path)
            with open(path) as f:
                file_str = f.read()
        except Exception as e:
            raise FetcherError("Failed to fetch from Filesystem", e)
        return json.loads(file_str)
