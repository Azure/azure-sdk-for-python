# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._generated import AzureDigitalTwinsAPI

class EventRoutesClient(object):
    """Creates an instance of AzureDigitalTwinsAPI.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authenticate requests to the service
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :**kwargs Used to configure the service client.
    :type **kwargs: any
    """
    def __init__(self, endpoint: str, credential: object, **kwargs: any):
        # type: (str, AzureKeyCredential, **Any) -> None

        self.endpoint = endpoint #type: str
        self.credential = credential #type AzureKeyCredential
        self._client = AzureDigitalTwinsAPI(
            credential=credential,
            base_url=endpoint,
            **kwargs
        ) #type: AzureDigitalTwinsAPI

    def get_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> "models.EventRoute"
        """Get an event route

        :param event_route_id: The Id of the event route
        :type event_route_id: str
        :**kwargs The operation options
        :type **kwargs: any
        :returns: The EventRoute object
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.get_by_id(event_route_id, **kwargs)

    def list_event_routes(self, max_item_count=-1, **kwargs):
        # type: (int, **Any) -> "models.EventRoute"
        """Retrieves all event routes

        :param max_item_count: The maximum number of items to retrieve per request.
        The server may choose to return less than the requested max.
        :type max_item_count: str
        :**kwargs The operation options
        :type **kwargs: any
        :returns: An iterator like instance of the EventRouteCollection
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.EventRouteCollection]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        if max_item_count != -1:
            digital_twin_models_list_options = {}
            digital_twin_models_list_options.max_item_count = max_item_count

        return self._client.event_routes.list(digital_twin_models_list_options, **kwargs)

    def upsert_event_route(self, event_route_id, event_route, **kwargs):
        # type: (str, "models.EventRoute", **Any) -> object
        """Create or update an event route

        :param event_route_id: The Id of the event route to create or update
        :type event_route_id: str
        :param event_route: The event route data.
        :type event_route: ~azure.digitaltwins.models.EventRoute
        :kwargs The operation options
        :type any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.add(event_route_id, event_route, **kwargs)

    def delete_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> object
        """Delete an event route

        :param event_route_id: The Id of the event route to delete
        :type event_route_id: str
        :kwargs The operation options
        :type any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.delete(event_route_id, **kwargs)
