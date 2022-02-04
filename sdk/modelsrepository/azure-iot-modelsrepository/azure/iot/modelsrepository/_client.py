# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from uuid import uuid4
from six import string_types
from azure.core.tracing.decorator import distributed_trace
from ._repository_handler import RepositoryHandler
from ._common import (
    DEFAULT_LOCATION,
    DEFAULT_API_VERSION,
    CLIENT_INIT_MSG,
    INVALID_DEPEDENCY_MODE,
    DependencyMode
)

_LOGGER = logging.getLogger(__name__)


class ModelsRepositoryClient(object):
    """Client providing APIs for Models Repository operations"""

    def __init__(
        self,
        repository_location=DEFAULT_LOCATION,
        **kwargs
    ):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (str, Any) -> None
        """
        :param repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :type repository_location: str

        :keyword str api_version: The API version for the Models Repository Service you wish to
            access.
        :keyword bool metadata_enabled: Whether the client will fetch and cache metadata.

        For additional request configuration options, please see [core options](https://aka.ms/azsdk/python/options).

        :raises: ValueError if an invalid argument is provided
        """
        # Store api version here (for now). Currently doesn't do anything
        self._api_version = kwargs.get("api_version", DEFAULT_API_VERSION)
        metadata_enabled = kwargs.pop("metadata_enabled", True)

        self.repository_uri = repository_location if repository_location else DEFAULT_LOCATION
        self._client_id = uuid4()
        info_msg = CLIENT_INIT_MSG.format(self._client_id, self.repository_uri)
        _LOGGER.debug(info_msg)

        self.repository_handler = RepositoryHandler(
            location=self.repository_uri,
            metadata_enabled=metadata_enabled,
            **kwargs
        )

    def __enter__(self):
        self.repository_handler.__enter__()
        return self

    def __exit__(self, *exc_details):
        self.repository_handler.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """Close the client, preventing future operations"""
        self.__exit__()

    @distributed_trace
    def get_models(self, dtmis, dependency_resolution=DependencyMode.enabled.value, **kwargs):
        # type: (Union[List[str], str], str, Any) -> Dict[str, Any]
        """Retrieve a model from the Models Repository.

        :param dtmis: The DTMI(s) for the model(s) you wish to retrieve
        :type dtmis: str or list[str]
        :param dependency_resolution: Dependency resolution mode.
            Possible values:
                - "disabled": Do not resolve model dependencies
                - "enabled": Resolve model dependencies from the repository
            If omitted, the default dependency resolution mode will be "enabled".
        :type dependency_resolution: str

        :raises: ValueError if given an invalid dependency resolution mode
        :raises: ~azure.iot.modelsrepository.ModelError if there is an error parsing the retrieved model(s)
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the model(s) cannot be found in the repository
        :raises: ~azure.core.exceptions.ServiceRequestError if there is an error sending a request for the model(s)
        :raises: ~azure.core.exceptions.ServiceResponseError if the model(s) cannot be retrieved
        :raises: ~azure.core.exceptions.HttpResponseError if a failure response is received

        :returns: Dictionary mapping DTMIs to models
        :rtype: dict
        """
        if isinstance(dtmis, string_types):
            dtmis = [dtmis]

        if dependency_resolution not in [DependencyMode.enabled.value, DependencyMode.disabled.value]:
            raise ValueError(INVALID_DEPEDENCY_MODE)

        return self.repository_handler.process(dtmis, dependency_resolution=dependency_resolution, **kwargs)
