# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from azure.core.tracing.decorator_async import distributed_trace_async
from ._resolver import DtmiResolver
from .._common import DEFAULT_LOCATION, DEFAULT_API_VERSION, CLIENT_INIT_MSG, DependencyModeType

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
        :param credential: Credentials to use when connecting to the service.
        :param repository_location: Location of the Models Repository you wish to access.
            This location can be a remote HTTP/HTTPS URL, or a local filesystem path.
            If omitted, will default to using "https://devicemodels.azure.com".
        :type repository_location: str
        :keyword str api_version: The API version for the Models Repository Service you wish to
            access.

        For additional request configuration options, please see [core options](https://aka.ms/azsdk/python/options).

        :raises: ValueError if an invalid argument is provided
        """
        self.repository_uri = repository_location if repository_location else DEFAULT_LOCATION
        info_msg = CLIENT_INIT_MSG.format(self.repository_uri)
        _LOGGER.debug(info_msg)

        self.resolver = DtmiResolver(location=self.repository_uri, **kwargs)

        # Store api version here (for now). Currently doesn't do anything
        self._api_version = kwargs.get("api_version", DEFAULT_API_VERSION)

    async def __aenter__(self):
        await self.resolver.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        await self.resolver.__aexit__(*exc_details)

    async def close(self):
        # type: () -> None
        """Close the client, preventing future operations"""
        await self.__aexit__()

    @distributed_trace_async
    async def get_models(self, dtmis, dependency_resolution=DependencyModeType.enabled.value, **kwargs):
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
        if isinstance(dtmis, str):
            dtmis = [dtmis]

        return await self.resolver.resolve(dtmis, dependency_resolution=dependency_resolution, **kwargs)
