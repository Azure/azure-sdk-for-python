# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._generated import AzureDigitalTwinsAPI

class QueryClient(object):
    """Creates an instance of AzureDigitalTwinsAPI.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authenticate requests to the service
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :**kwargs Used to configure the service client.
    :type **kwargs: any
    """
    def __init__(self, endpoint, credential, **kwargs: any):
        # type: (str, AzureKeyCredential, **Any) -> None

        self.endpoint = endpoint #type: str
        self.credential = credential #type AzureKeyCredential
        self._client = AzureDigitalTwinsAPI(
            credential=credential,
            base_url=endpoint,
            **kwargs
        ) #type: AzureDigitalTwinsAPI

    def query_twins(self, query_specification, **kwargs):
        # type: ("models.QuerySpecification", **Any) -> "models.QueryResult"
        """Query for digital twins

        :param query_specification: The query specification to execute.
        :type query_specification: ~azure.digitaltwins.models.QuerySpecification
        :**kwargs The operation options
        :type **kwargs: any
        :returns: The QueryResult object
        :rtype: ~azure.digitaltwins.models.QueryResult
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.query.query_twins(query_specification, **kwargs)
