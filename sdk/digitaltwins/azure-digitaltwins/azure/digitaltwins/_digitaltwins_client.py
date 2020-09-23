# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime
from ._generated import AzureDigitalTwinsAPI

class DigitalTwinsClient(object):
    """Creates an instance of AzureDigitalTwinsAPI.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authenticate requests to the service
    :type credential: ~azure.core.credentials.AzureKeyCredential
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

    def get_digital_twin(self, digital_twin_id, **kwargs):
        # type: (str, **Any) -> object
        """Get a digital twin.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :returns: The twin object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.get_by_id(digital_twin_id, **kwargs)

    def upsert_digital_twin(self, digital_twin_id, digital_twin, **kwargs):
        # type: (str, object, **Any) -> object
        """Create or update a digital twin.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        412 (Precondition Failed): The model is decommissioned.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param digital_twin: The twin object to create or update.
        :type digital_twin: object
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: The created or updated twin object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.add(digital_twin_id, digital_twin, if_none_match="", **kwargs)

    def update_digital_twin(self, digital_twin_id, twin_patch, etag=None, **kwargs):
        # type: (str, object, str, **Any) -> object
        """Update a digital twin using a json patch.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no digital twin with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param twin_patch: An update specification described by JSON Patch.
            Updates to property values and $model elements may happen in the same request.
            Operations are limited to add, replace and remove.
        :type twin_patch: str
        :param etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :type str
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.update(digital_twin_id, twin_patch, if_match=etag, **kwargs)

    def delete_digital_twin(self, digital_twin_id, etag=None, **kwargs):
        # type: (str, str, **Any) -> object
        """Delete a digital twin.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no digital twin with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :type str
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.delete(digital_twin_id, if_match=etag, **kwargs)

    def get_component(self, digital_twin_id, component_path, **kwargs):
        # type: (str, str, **Any) -> object
        """Get a component on a digital twin.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is either no digital twin with the provided id or the component path is
        invalid.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param component_path: The component being retrieved.
        :type str
        :returns: The component object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.get_component(digital_twin_id, component_path, **kwargs)

    def update_component(
        self,
        digital_twin_id,
        component_path,
        component_patch,
        etag=None,
        **kwargs
    ):
        # type: (str, str, List[object],  str, **Any) -> object
        """Update properties of a component on a digital twin using a JSON patch.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is either no digital twin with the provided id or the component path is
        invalid.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param component_path: The component being updated.
        :type str
        :param component_patch: An update specification described by JSON Patch.
        :type List[object]
        :param etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :type str
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.update_component(
            digital_twin_id,
            component_path,
            patch_document=component_patch,
            if_match=etag,
            **kwargs
            )

    def get_relationship(self, digital_twin_id, relationship_id, **kwargs):
        # type: (str, str, **Any) -> object
        """Get a relationship on a digital twin.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is either no digital twin or relationship with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve.
        :type str
        :returns: The relationship object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.get_relationship_by_id(digital_twin_id, relationship_id, **kwargs)

    def upsert_relationship(self, digital_twin_id, relationship_id, relationship=None, **kwargs):
        # type: (str, str, object, **Any) -> object
        """Create or update a relationship on a digital twin.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is either no digital twin, target digital twin, or relationship with the
        provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve.
        :type str
        :param relationship: The relationship object.
        :type object
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: The created or updated relationship object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.add_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            if_none_match="",
            relationship=relationship,
            **kwargs
        )

    def update_relationship(self, digital_twin_id, relationship_id, relationship_patch=None, etag=None, **kwargs):
        # type: (str, str, List[object], str, **Any) -> object
        """Updates the properties of a relationship on a digital twin using a JSON patch.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is either no digital twin or relationship with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve.
        :type str
        :param relationship_patch: JSON Patch description of the update to the relationship properties.
        :type List[object]
        :param etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :type str
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.update_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            relationship_patch=relationship_patch,
            if_match=etag,
            **kwargs
        )

    def delete_relationship(self, digital_twin_id, relationship_id, etag=None, **kwargs):
        # type: (str, str, str, **Any) -> object
        """Delete a digital twin.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is either no digital twin or relationship with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to delete.
        :type relationship_id: str
        :param etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :type etag: str
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.delete_relationship(
            digital_twin_id, 
            relationship_id, 
            if_match=etag, 
            **kwargs
        )

    def list_relationships(self, digital_twin_id, relationship_id=None, **kwargs):
        # type: (str, str, **Any) -> Iterable["models.RelationshipCollection"]
        """Retrieve relationships for a digital twin.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no digital twin with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to get (if None all the relationship will be retrieved).
        :type relationship_id: str
        :return: An iterator like instance of either RelationshipCollection
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.RelationshipCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.digital_twins.list_relationships(
            digital_twin_id, 
            relationship_name=relationship_id,
            **kwargs
        )

    def list_incoming_relationships(self, digital_twin_id, **kwargs):
        # type: (str, str, **Any) -> Iterable["models.IncomingRelationshipCollection"]
        """Retrieve all incoming relationships for a digital twin.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no digital twin with the provided id.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :return: An iterator like instance of either RelationshipCollection.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.IncomingRelationshipCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.digital_twins.list_incoming_relationships(
            digital_twin_id, 
            **kwargs
        )

    def publish_telemetry(self, digital_twin_id, payload, message_id=None, **kwargs):
        # type: (str, object, str, **Any) -> None
        """Publish telemetry from a digital twin, which is then consumed by
           one or many destination endpoints (subscribers) defined under.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no digital twin with the provided id.

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param payload: The telemetry payload to be sent
        :type payload: object
        :param message_id: The message Id
        :type message_id: str
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not message_id:
            message_id = uuid.UUID
        timestamp = datetime.now
        return self._client.digital_twins.send_telemetry(
            digital_twin_id,
            message_id,
            telemetry=payload,
            dt_timestamp=timestamp,
            **kwargs
        )

    def publish_component_telemetry(self, digital_twin_id, component_path, payload, message_id=None, **kwargs):
        # type: (str, str, object, str, **Any) -> None
        """Publish telemetry from a digital twin's component, which is then consumed by
            one or many destination endpoints (subscribers) defined under.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is either no digital twin with the provided id or the component path is
        invalid.

        :param digital_twin_id: The Id of the digital twin.
        :type digital_twin_id: str
        :param component_path: The name of the DTDL component.
        :type component_path: str
        :param payload: The telemetry payload to be sent.
        :type payload: object
        :param message_id: The message Id.
        :type message_id: str
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not message_id:
            message_id = uuid.UUID
        timestamp = datetime.now
           
        return self._client.digital_twins.send_component_telemetry(
            digital_twin_id,
            component_path,
            dt_id=message_id,
            telemetry=payload,
            dt_timestamp=timestamp,
            **kwargs
        )

    def get_model(self, model_id, include_model_definition=False, **kwargs):
        # type: (str, bool, **Any) -> "models.ModelData"
        """Get a model, including the model metadata and the model definition.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is no model with the provided id.

        :param model_id: The Id of the model.
        :type model_id: str
        :param include_model_definition: When true the model definition
            will be returned as part of the result.
        :type include_model_definition: bool
        :returns: The ModelDate object.
        :rtype: ~azure.digitaltwins.models.ModelData
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.get_by_id(model_id, include_model_definition, **kwargs)

    def list_models(self, dependencies_for, **kwargs):
        # type: (str, bool, int, **Any) -> Iterable["models.PagedModelDataCollection"]
        """Get the list of models.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.

        :param dependencies_for: The model Ids to have dependencies retrieved.
            If omitted, all models are retrieved.
        :type dependencies_for: list[str]
        :keyword bool include_model_definition: When true the model definition
            will be returned as part of the result.
        :keyword int max_item_count: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :returns: An iterator like instance of either PagedModelDataCollection.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.PagedModelDataCollection]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        include_model_definition = kwargs.pop('include_model_definition', False)
        max_item_count = kwargs.pop('max_item_count', -1)

        digital_twin_models_list_options = {'max_item_count': -1}
        if max_item_count != -1:
            digital_twin_models_list_options= {'max_item_count': max_item_count}
        return self._client.digital_twin_models.list(
            dependencies_for=dependencies_for,
            include_model_definition=include_model_definition,
            digital_twin_models_list_options=digital_twin_models_list_options, **kwargs
        )

    def create_models(self, models=None, **kwargs):
        # type: (List[object], **Any) -> List["models.ModelData"]
        """Create one or more models. When any error occurs, no models are uploaded.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        409 (Conflict): One or more of the provided models already exist.

        :param models: The set of models to create. Each string corresponds to exactly one model.
        :type models: List[object]
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: The list of ModelData
        :rtype: List[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.add(models, **kwargs)

    def decommission_model(self, model_id, **kwargs):
        # type: (str, List[object], **Any) -> List["models.ModelData"]
        """Decommissions a model.
        200 (OK): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no model with the provided id.

        :param model_id: The id for the model. The id is globally unique and case sensitive.
        :type model_id: str
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        decommission_patch = "{ 'op': 'replace', 'path': '/decommissioned', 'value': true }"
        return self._client.digital_twin_models.update(model_id, decommission_patch , **kwargs)

    def delete_model(self, model_id, **kwargs):
        # type: (str, **Any) -> None
        """Decommission a model using a json patch.
        Status codes:
        204 (No Content): Success.
        400 (Bad Request): The request is invalid.
        404 (Not Found): There is no model with the provided id.
        409 (Conflict): There are dependencies on the model that prevent it from being deleted.

        :param model_id: The Id of the model to decommission.
        :type model_id: str
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.delete(model_id, **kwargs)

    def get_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> "models.EventRoute"
        """Get an event route.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is no event route with the provided id.

        :param event_route_id: The Id of the event route.
        :type event_route_id: str
        :returns: The EventRoute object.
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.get_by_id(event_route_id, **kwargs)

    def list_event_routes(self, max_item_count=-1, **kwargs):
        # type: (int, **Any) -> "models.EventRoute"
        """Retrieves all event routes.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.

        :param max_item_count: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :type max_item_count: str
        :returns: An iterator like instance of the EventRouteCollection.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.EventRouteCollection]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        digital_twin_models_list_options = {'max_item_count': -1}
        if max_item_count != -1:
            digital_twin_models_list_options= {'max_item_count': max_item_count}

        return self._client.event_routes.list(digital_twin_models_list_options, **kwargs)

    def upsert_event_route(self, event_route_id, event_route, **kwargs):
        # type: (str, "models.EventRoute", **Any) -> object
        """Create or update an event route.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.

        :param event_route_id: The Id of the event route to create or update.
        :type event_route_id: str
        :param event_route: The event route data.
        :type event_route: ~azure.digitaltwins.models.EventRoute
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.add(event_route_id, event_route, **kwargs)

    def delete_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> object
        """Delete an event route.
        Status codes:
        200 (OK): Success.
        404 (Not Found): There is no event route with the provided id.

        :param event_route_id: The Id of the event route to delete.
        :type event_route_id: str
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.event_routes.delete(event_route_id, **kwargs)

    def query_twins(self, query_specification, **kwargs):
        # type: ("models.QuerySpecification", **Any) -> "models.QueryResult"
        """Query for digital twins.
        Status codes:
        200 (OK): Success.
        400 (Bad Request): The request is invalid.

        :param query_specification: The query specification to execute.
        :type query_specification: ~azure.digitaltwins.models.QuerySpecification.
        :keyword str content_type: Content type to set in the HTTP header. Default to "application/json".
        :returns: The QueryResult object.
        :rtype: ~azure.digitaltwins.models.QueryResult
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.query.query_twins(query_specification, **kwargs)
