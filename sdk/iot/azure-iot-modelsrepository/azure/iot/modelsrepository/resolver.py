# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import six
import json
import abc
import re
import os
from .chainable_exception import ChainableException

logger = logging.getLogger(__name__)


class ResolverError(ChainableException):
    pass


class DtmiResolver(object):
    def __init__(self, fetcher):
        """
        :param fetcher: A Fetcher configured to an endpoint to resolve DTMIs from
        :type fetcher: :class:`azure.iot.modelsrepository.resolver`
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
            dtdl_path = _convert_dtmi_to_path(dtmi)
            if expanded_model:
                dtdl_path = dtdl_path.replace(".json", ".expanded.json")

            try:
                dtdl = self.fetcher.fetch(dtdl_path)
            except FetcherError as e:
                raise ResolverError("Failed to resolve dtmi: {}".format(dtmi), cause=e)

            if expanded_model:
                for model in dtdl:
                    model_map[model["@id"]] = model
            else:
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
        # Format path
        path = os.path.join(self.base_path, path)
        path = os.path.normcase(path)
        path = os.path.normpath(path)

        # TODO: Ensure support for relative and absolute paths
        # TODO: Need robust suite of testing for different types of paths

        # Fetch
        try:
            with open(path) as f:
                file_str = f.read()
        except Exception as e:
            raise FetcherError("Failed to fetch from Filesystem", e)
        return json.loads(file_str)


def _convert_dtmi_to_path(dtmi):
    """Converts a DTMI into a DTMI path

    E.g:
    dtmi:com:example:Thermostat;1 -> dtmi/com/example/thermostat-1.json
    """
    pattern = re.compile(
        "^dtmi:[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?(?::[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?)*;[1-9][0-9]{0,8}$"
    )
    if not pattern.match(dtmi):
        raise ValueError("Invalid DTMI")
    else:
        return dtmi.lower().replace(":", "/").replace(";", "-") + ".json"
