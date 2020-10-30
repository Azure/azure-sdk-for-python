# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime
from typing import Dict
from msrest import Serializer, Deserializer
from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core import MatchConditions

from .._utils import (
    prep_if_match
)

from .._generated import models
from .._generated.aio._azure_digital_twins_api_async import AzureDigitalTwinsAPI

class DigitalTwinsClient(object): # type: ignore #pylint: disable=too-many-public-methods
    """Creates an instance of AzureDigitalTwinsAPI.

    :param str endpoint: The URL endpoint of an Azure search service
    :param ~azure.core.credentials.AzureKeyCredential credential:
        A credential to authenticate requests to the service
    """
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self.endpoint = endpoint #type: str
        self.credential = credential #type AzureKeyCredential
        self._client = AzureDigitalTwinsAPI(
            credential=credential,
            base_url=endpoint,
            **kwargs
        ) #type: AzureDigitalTwinsAPI

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "DigitalTwinsClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)

    @distributed_trace_async
    async def get_digital_twin(self, digital_twin_id, **kwargs):
        # type: (str, **Any) -> Dict[str, object]
        """Get a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :return: Dictionary containing the twin.
        :rtype: Dict[str, object]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`:
            If the digital twin doesn't exist.
        """
        return await self._client.digital_twins.get_by_id(
            digital_twin_id,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_digital_twin(self, digital_twin_id, digital_twin, **kwargs):
        # type: (str, Dict[str, object], **Any) -> Dict[str, object]
        """Create or update a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param Dict[str, object] digital_twin:
            Dictionary containing the twin to create or update.
        :return: Dictionary containing the created or updated twin.
        :rtype: Dict[str, object]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`:
            If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceExistsError`:
            If the digital twin is already exist.
        """
        return await self._client.digital_twins.add(
            digital_twin_id,
            digital_twin,
            **kwargs
        )

    @distributed_trace_async
    async def update_digital_twin(
        self,
        digital_twin_id,
        json_patch,
        **kwargs
    ):
        # type: (str, Dict[str, object], **Any) -> None
        """Update a digital twin using a json patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param Dict[str, object] json_patch: An update specification described by JSON Patch.
            Updates to property values and $model elements may happen in the same request.
            Operations are limited to add, replace and remove.
        :keyword str etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`:
            If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`:
            If there is no digital twin with the provided id.
        """
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)

        return await self._client.digital_twins.update(
            digital_twin_id,
            json_patch,
            if_match=prep_if_match(etag, match_condition),
            **kwargs
        )

    @distributed_trace_async
    async def delete_digital_twin(
        self,
        digital_twin_id,
        **kwargs
    ):
        # type: (str, **Any) -> None
        """Delete a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :keyword str etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :keyword ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`:
            If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`:
            If there is no digital twin with the provided id.
        """
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)

        return await self._client.digital_twins.delete(
            digital_twin_id,
            if_match=prep_if_match(etag, match_condition),
            **kwargs
        )

    @distributed_trace_async
    async def get_component(self, digital_twin_id, component_path, **kwargs):
        # type: (str, str, **Any) -> Dict[str, object]
        """Get a component on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str component_path: The component being retrieved.
        :return: Dictionary containing the component.
        :rtype: Dict[str, object]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin with the provided id or the component path is invalid.
        """
        return await self._client.digital_twins.get_component(
            digital_twin_id,
            component_path,
            **kwargs
        )

    @distributed_trace_async
    async def update_component(
        self,
        digital_twin_id,
        component_path,
        json_patch,
        **kwargs
    ):
        # type: (str, str, Dict[str, object], **Any) -> None
        """Update properties of a component on a digital twin using a JSON patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param str component_path: The component being updated.
        :param Dict[str, object] json_patch: An update specification described by JSON Patch.
        :keyword str etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :keyword ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin with the provided id or the component path is invalid.
        """
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)

        return await self._client.digital_twins.update_component(
            digital_twin_id,
            component_path,
            patch_document=json_patch,
            if_match=prep_if_match(etag, match_condition),
            **kwargs
        )

    @distributed_trace_async
    async def get_relationship(self, digital_twin_id, relationship_id, **kwargs):
        # type: (str, str, **Any) -> Dict[str, object]
        """Get a relationship on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :return: Dictionary containing the relationship.
        :rtype: Dict[str, object]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin or relationship with the provided id.
        """
        return await self._client.digital_twins.get_relationship_by_id(
            digital_twin_id,
            relationship_id,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_relationship(self, digital_twin_id, relationship_id, relationship=None, **kwargs):
        # type: (str, str, Optional[Dict[str, object]], **Any) -> Dict[str, object]
        """Create or update a relationship on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :param Dict[str, object] relationship: Dictionary containing the relationship.
        :return: The created or updated relationship.
        :rtype: Dict[str, object]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin, target digital twin or relationship with the provided id.
        """
        return await self._client.digital_twins.add_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            relationship=relationship,
            **kwargs
        )

    @distributed_trace_async
    async def update_relationship(
        self,
        digital_twin_id,
        relationship_id,
        json_patch=None,
        **kwargs
    ):
        # type: (str, str, Dict[str, object], **Any) -> None
        """Updates the properties of a relationship on a digital twin using a JSON patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :param Dict[str, object] json_patch: JSON Patch description of the update
            to the relationship properties.
        :keyword str etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :keyword ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin or relationship with the provided id.
        """
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)

        return await self._client.digital_twins.update_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            json_patch=json_patch,
            if_match=prep_if_match(etag, match_condition),
            **kwargs
        )

    @distributed_trace_async
    async def delete_relationship(
        self,
        digital_twin_id,
        relationship_id,
        **kwargs
    ):
        # type: (str, str, **Any) -> None
        """Delete a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to delete.
        :keyword str etag: Only perform the operation if the entity's etag matches one of
            the etags provided or * is provided.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin or relationship with the provided id.
        """
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)

        return await self._client.digital_twins.delete_relationship(
            digital_twin_id,
            relationship_id,
            if_match=prep_if_match(etag, match_condition),
            **kwargs
        )

    @distributed_trace_async
    async def list_relationships(self, digital_twin_id, relationship_id=None, **kwargs):
        # type: (str, Optional[str], **Any) -> ~AsyncItemPaged[~azure.digitaltwins.models.Relationship]
        """Retrieve relationships for a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to
            get (if None all the relationship will be retrieved).
        :return: An iterator instance of list of Relationship
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.digitaltwins.models.Relationship]
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id.
        """
        return await self._client.digital_twins.list_relationships(
            digital_twin_id,
            relationship_name=relationship_id,
            **kwargs
        )

    @distributed_trace_async
    async def list_incoming_relationships(self, digital_twin_id, **kwargs):
        # type: (str, str, **Any) -> ~azure.core.paging.AsyncItemPaged[~azure.digitaltwins.models.IncomingRelationship]
        """Retrieve all incoming relationships for a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :return: An iterator like instance of either Relationship.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.digitaltwins.models.IncomingRelationship]
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id.
        """
        return await self._client.digital_twins.list_incoming_relationships(
            digital_twin_id,
            **kwargs
        )

    @distributed_trace_async
    async def publish_telemetry(self, digital_twin_id, payload, message_id=None, **kwargs):
        # type: (str, object, Optional[str], **Any) -> None
        """Publish telemetry from a digital twin, which is then consumed by
           one or many destination endpoints (subscribers) defined under.

        :param str digital_twin_id: The Id of the digital twin
        :param object payload: The telemetry payload to be sent
        :param str message_id: The message Id
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id.
        """
        if not message_id:
            message_id = uuid.UUID
        timestamp = datetime.now

        return await self._client.digital_twins.send_telemetry(
            digital_twin_id,
            message_id,
            telemetry=payload,
            dt_timestamp=timestamp,
            **kwargs
        )

    @distributed_trace_async
    async def publish_component_telemetry(
        self,
        digital_twin_id,
        component_path,
        payload,
        message_id=None,
        **kwargs
    ):
        # type: (str, str, object, Optional[str], **Any) -> None
        """Publish telemetry from a digital twin's component, which is then consumed by
            one or many destination endpoints (subscribers) defined under.

        :param str digital_twin_id: The Id of the digital twin.
        :param str component_path: The name of the DTDL component.
        :param object payload: The telemetry payload to be sent.
        :param str message_id: The message Id.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id or the component path is invalid.
        """
        if not message_id:
            message_id = uuid.UUID
        timestamp = datetime.now

        return await self._client.digital_twins.send_component_telemetry(
            digital_twin_id,
            component_path,
            dt_id=message_id,
            telemetry=payload,
            dt_timestamp=timestamp,
            **kwargs
        )

    @distributed_trace_async
    async def get_model(self, model_id, **kwargs):
        # type: (str, **Any) -> ~azure.digitaltwins.models.ModelData
        """Get a model, including the model metadata and the model definition.

        :param str model_id: The Id of the model.
        :keyword bool include_model_definition: When true the model definition
            will be returned as part of the result.
        :return: The ModelDate object.
        :rtype: ~azure.digitaltwins.models.ModelData
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            model with the provided id.
        """
        include_model_definition = kwargs.get("include_model_definition", False)

        return await self._client.digital_twin_models.get_by_id(
            model_id,
            include_model_definition,
            **kwargs
        )

    @distributed_trace_async
    async def list_models(self, dependencies_for, **kwargs):
        # type: (str, bool, int, **Any) -> ~azure.core.paging.AsyncItemPaged[~azure.digitaltwins.models.ModelData]
        """Get the list of models.

        :param List[str] dependencies_for: The model Ids to have dependencies retrieved.
            If omitted, all models are retrieved.
        :keyword bool include_model_definition: When true the model definition
            will be returned as part of the result.
        :keyword int results_per_page: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of list of ModelData.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        """
        include_model_definition = kwargs.pop('include_model_definition', False)

        results_per_page = kwargs.pop('results_per_page', None)
        digital_twin_models_list_options = None
        if results_per_page is not None:
            digital_twin_models_list_options = {'max_item_count': results_per_page}

        return await self._client.digital_twin_models.list(
            dependencies_for=dependencies_for,
            include_model_definition=include_model_definition,
            digital_twin_models_list_options=digital_twin_models_list_options,
            **kwargs
        )

    @distributed_trace_async
    async def create_models(self, model_list=None, **kwargs):
        # type: (Optional[List[object]], **Any) -> List[~azure.digitaltwins.models.ModelData]
        """Create one or more models. When any error occurs, no models are uploaded.

        :param List[object] model_list: The set of models to create. Each string corresponds to exactly one model.
        :return: The list of ModelData
        :rtype: List[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: One or more of
            the provided models already exist.
        """
        return await self._client.digital_twin_models.add(
            model_list,
            **kwargs
        )

    @distributed_trace_async
    async def decommission_model(self, model_id, **kwargs):
        # type: (str, **Any) -> None
        """Decommissions a model.

        :param str model_id: The id for the model. The id is globally unique and case sensitive.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no model
            with the provided id.
        """
        json_patch = "{ 'op': 'replace', 'path': '/decommissioned', 'value': true }"

        return await self._client.digital_twin_models.update(
            model_id,
            json_patch,
            **kwargs
        )

    @distributed_trace_async
    async def delete_model(self, model_id, **kwargs):
        # type: (str, **Any) -> None
        """Decommission a model using a json patch.

        :param str model_id: The Id of the model to decommission.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no model
            with the provided id.
        :raises :class: `~azure.core.exceptions.ResourceExistsError`: There are dependencies
            on the model that prevent it from being deleted.
        """
        return await self._client.digital_twin_models.delete(
            model_id,
            **kwargs
        )

    @distributed_trace_async
    async def get_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> ~azure.digitaltwins.models.EventRoute
        """Get an event route.

        :param str event_route_id: The Id of the event route.
        :return: The EventRoute object.
        :rtype: ~azure.digitaltwins.models.EventRoute
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no
            event route with the provided id.
        """
        return await self._client.event_routes.get_by_id(
            event_route_id,
            **kwargs
        )

    @distributed_trace_async
    async def list_event_routes(self, **kwargs):
        # type: (**Any) -> ~azure.core.paging.AsyncItemPaged[~azure.digitaltwins.models.EventRoute]
        """Retrieves all event routes.

        :keyword int results_per_page: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of list of EventRoute.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.digitaltwins.models.EventRoute]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: The request is invalid.
        """
        event_routes_list_options = None
        results_per_page = kwargs.pop('results_per_page', None)
        if results_per_page is not None:
            event_routes_list_options = {'max_item_count': results_per_page}

        return await self._client.event_routes.list(
            event_routes_list_options=event_routes_list_options,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_event_route(self, event_route_id, event_route, **kwargs):
        # type: (str, "models.EventRoute", **Any) -> None
        """Create or update an event route.

        :param str event_route_id: The Id of the event route to create or update.
        :param ~azure.digitaltwins.models.EventRoute event_route: The event route data.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: The request is invalid.
        """
        return await self._client.event_routes.add(
            event_route_id, event_route,
            **kwargs
        )

    @distributed_trace_async
    async def delete_event_route(self, event_route_id, **kwargs):
        # type: (str, **Any) -> None
        """Delete an event route.

        :param str event_route_id: The Id of the event route to delete.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no
            event route with the provided id.
        """
        return await self._client.event_routes.delete(
            event_route_id,
            **kwargs
        )

    @distributed_trace_async
    async def query_twins(self, query_expression, **kwargs):
        # type: (str, **Any) -> ~azure.core.async_paging.AsyncItemPaged[Dict[str, object]]
        """Query for digital twins.

        :param str query_expression: The query expression to execute.
        :return: The QueryResult object.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[Dict[str, object]]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        def extract_data(pipeline_response):
            deserialized = self._deserialize('QueryResult', pipeline_response)
            list_of_elem = deserialized.value
            return deserialized.continuation_token or None, iter(list_of_elem)

        async def get_next(continuation_token=None):
            query_spec = self._serialize.serialize_dict(
                {'query': query_expression, 'continuation_token': continuation_token},
                'QuerySpecification'
            )
            pipeline_response = await self._client.query.query_twins(query_spec, **kwargs)
            return pipeline_response

        return AsyncItemPaged(
            get_next,
            extract_data
        )
