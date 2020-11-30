# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from msrest import Serializer

from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core import MatchConditions
from .._version import SDK_MONIKER

from .._utils import (
    prep_if_match,
    prep_if_none_match
)
from .._generated.aio import AzureDigitalTwinsAPI
from .._generated.models import (
    QuerySpecification,
    DigitalTwinsAddOptions,
    DigitalTwinsDeleteOptions,
    DigitalTwinsUpdateOptions,
    DigitalTwinsUpdateComponentOptions,
    DigitalTwinsDeleteRelationshipOptions,
    DigitalTwinsUpdateRelationshipOptions,
    DigitalTwinsAddRelationshipOptions,
    DigitalTwinsModelData
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from .._generated.models import (
        IncomingRelationship,
        DigitalTwinsEventRoute
    )


class DigitalTwinsClient(object): # pylint: disable=too-many-public-methods
    """Creates an instance of the Digital Twins client.

    :param str endpoint: The URL endpoint of an Azure search service
    :param ~azure.core.credentials_async.AsyncTokenCredential credential:
        A credential to authenticate requests to the service.
    """
    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs) -> None:
        if not endpoint.startswith('http'):
            endpoint = 'https://' + endpoint
        self._client = AzureDigitalTwinsAPI(
            credential=credential,
            base_url=endpoint,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "DigitalTwinsClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)

    @distributed_trace_async
    async def get_digital_twin(self, digital_twin_id: str, **kwargs) -> Dict[str, object]:
        """Get a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :return: Dictionary containing the twin.
        :rtype: Dict[str, object]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
            If the digital twin doesn't exist.
        """
        return await self._client.digital_twins.get_by_id(
            digital_twin_id,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_digital_twin(
        self,
        digital_twin_id: str,
        digital_twin: Dict[str, object],
        **kwargs
    ) -> Dict[str, object]:
        """Create or update a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param Dict[str,object] digital_twin:
            Dictionary containing the twin to create or update.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: Dictionary containing the created or updated twin.
        :rtype: Dict[str, object]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceExistsError:
            If the digital twin already exists.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_none_match, error_map = prep_if_none_match(etag, match_condition)
        if if_none_match:
            options = DigitalTwinsAddOptions(if_none_match=if_none_match)
        return await self._client.digital_twins.add(
            digital_twin_id,
            digital_twin,
            digital_twins_add_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def update_digital_twin(
        self,
        digital_twin_id: str,
        json_patch: List[Dict[str, object]],
        **kwargs
    ) -> None:
        """Update a digital twin using a JSON patch.

        :param str digital_twin_id: The ID of the digital twin.
        :param List[Dict[str,object]] json_patch: An update specification described by JSON Patch.
            Updates to property values and $model elements may happen in the same request.
            Operations are limited to add, replace and remove.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
            If there is no digital twin with the provided ID.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_match, error_map = prep_if_match(etag, match_condition)
        if if_match:
            options = DigitalTwinsUpdateOptions(if_match=if_match)
        return await self._client.digital_twins.update(
            digital_twin_id,
            json_patch,
            digital_twins_update_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def delete_digital_twin(
        self,
        digital_twin_id: str,
        **kwargs
    ) -> None:
        """Delete a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
            If there is no digital twin with the provided ID.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_match, error_map = prep_if_match(etag, match_condition)
        if if_match:
            options = DigitalTwinsDeleteOptions(if_match=if_match)
        return await self._client.digital_twins.delete(
            digital_twin_id,
            digital_twins_delete_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def get_component(self, digital_twin_id: str, component_name: str, **kwargs) -> Dict[str, object]:
        """Get a component on a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param str component_name: The component being retrieved.
        :return: Dictionary containing the component.
        :rtype: Dict[str, object]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin with the provided ID or the component name is invalid.
        """
        return await self._client.digital_twins.get_component(
            digital_twin_id,
            component_name,
            **kwargs
        )

    @distributed_trace_async
    async def update_component(
        self,
        digital_twin_id: str,
        component_name: str,
        json_patch: List[Dict[str, object]],
        **kwargs
    ) -> None:
        """Update properties of a component on a digital twin using a JSON patch.

        :param str digital_twin_id: The ID of the digital twin.
        :param str component_name: The component being updated.
        :param List[Dict[str,object]] json_patch: An update specification described by JSON Patch.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin with the provided ID or the component name is invalid.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_match, error_map = prep_if_match(etag, match_condition)
        if if_match:
            options = DigitalTwinsUpdateComponentOptions(if_match=if_match)
        return await self._client.digital_twins.update_component(
            digital_twin_id,
            component_name,
            patch_document=json_patch,
            digital_twins_update_component_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def get_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        **kwargs
    ) -> Dict[str, object]:
        """Get a relationship on a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param str relationship_id: The ID of the relationship to retrieve.
        :return: Dictionary containing the relationship.
        :rtype: Dict[str, object]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin or relationship with the provided ID.
        """
        return await self._client.digital_twins.get_relationship_by_id(
            digital_twin_id,
            relationship_id,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        relationship: Dict[str, object],
        **kwargs
    ) -> Dict[str, object]:
        """Create or update a relationship on a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param str relationship_id: The ID of the relationship to retrieve.
        :param Dict[str,object] relationship: Dictionary containing the relationship.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: The created or updated relationship.
        :rtype: Dict[str, object]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin, target digital twin or relationship with the provided ID.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_none_match, error_map = prep_if_none_match(etag, match_condition)
        if if_none_match:
            options = DigitalTwinsAddRelationshipOptions(if_none_match=if_none_match)
        return await self._client.digital_twins.add_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            relationship=relationship,
            digital_twins_add_relationship_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def update_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        json_patch: List[Dict[str, object]],
        **kwargs
    ) -> None:
        """Updates the properties of a relationship on a digital twin using a JSON patch.

        :param str digital_twin_id: The ID of the digital twin.
        :param str relationship_id: The ID of the relationship to retrieve.
        :param List[Dict[str,object]] json_patch: JSON Patch description of the update
            to the relationship properties.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin or relationship with the provided ID.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_match, error_map = prep_if_match(etag, match_condition)
        if if_match:
            options = DigitalTwinsUpdateRelationshipOptions(if_match=if_match)
        return await self._client.digital_twins.update_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            patch_document=json_patch,
            digital_twins_update_relationship_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def delete_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        **kwargs
    ) -> None:
        """Delete a relationship on a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param str relationship_id: The ID of the relationship to delete.
        :keyword ~azure.core.MatchConditions match_condition:
            The condition under which to perform the operation.
        :keyword str etag:
            Only perform the operation if the entity's etag matches the value provided
            according to the `match_condition`.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is either no
            digital twin or relationship with the provided ID.
        """
        options = None
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if_match, error_map = prep_if_match(etag, match_condition)
        if if_match:
            options = DigitalTwinsDeleteRelationshipOptions(if_match=if_match)
        return await self._client.digital_twins.delete_relationship(
            digital_twin_id,
            relationship_id,
            digital_twins_delete_relationship_options=options,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace
    def list_relationships(
        self,
        digital_twin_id: str,
        relationship_id: Optional[str] = None,
        **kwargs
    ) -> AsyncItemPaged[Dict[str, object]]:
        """Retrieve relationships for a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :param str relationship_id: The ID of the relationship to
            get (if None all the relationship will be retrieved).
        :return: An iterator instance of list of relationships.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[Dict[str,object]]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is no
            digital twin with the provided ID.
        """
        return self._client.digital_twins.list_relationships(
            digital_twin_id,
            relationship_name=relationship_id,
            **kwargs
        )

    @distributed_trace
    def list_incoming_relationships(
        self,
        digital_twin_id: str,
        **kwargs
    ) -> AsyncItemPaged['IncomingRelationship']:
        """Retrieve all incoming relationships for a digital twin.

        :param str digital_twin_id: The ID of the digital twin.
        :return: An iterator instance of list of incoming relationships.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.digitaltwins.core.IncomingRelationship]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is no
            digital twin with the provided ID.
        """
        return self._client.digital_twins.list_incoming_relationships(
            digital_twin_id,
            **kwargs
        )

    @distributed_trace_async
    async def publish_telemetry(
        self,
        digital_twin_id: str,
        telemetry: object,
        **kwargs
    ) -> None:
        """Publish telemetry from a digital twin, which is then consumed by
        one or many destination endpoints (subscribers) defined under.

        :param str digital_twin_id: The ID of the digital twin
        :param object telemetry: The telemetry data to be sent
        :keyword str message_id: The message ID. If not specified, a UUID will be generated.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is no
            digital twin with the provided ID.
        """
        message_id = kwargs.pop('message_id', None) or str(uuid.uuid4())
        timestamp = Serializer.serialize_iso(datetime.utcnow())
        return await self._client.digital_twins.send_telemetry(
            digital_twin_id,
            message_id=message_id,
            telemetry=telemetry,
            telemetry_source_time=timestamp,
            **kwargs
        )

    @distributed_trace_async
    async def publish_component_telemetry(
        self,
        digital_twin_id: str,
        component_name: str,
        telemetry: object,
        **kwargs
    ) -> None:
        """Publish telemetry from a digital twin's component, which is then consumed
        by one or many destination endpoints (subscribers) defined under.

        :param str digital_twin_id: The ID of the digital twin.
        :param str component_name: The name of the DTDL component.
        :param object telemetry: The telemetry data to be sent.
        :keyword str message_id: The message ID. If not specified, a UUID will be generated.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is no
            digital twin with the provided ID or the component name is invalid.
        """
        message_id = kwargs.pop('message_id', None) or str(uuid.uuid4())
        timestamp = Serializer.serialize_iso(datetime.utcnow())
        return await self._client.digital_twins.send_component_telemetry(
            digital_twin_id,
            component_name,
            message_id=message_id,
            telemetry=telemetry,
            telemetry_source_time=timestamp,
            **kwargs
        )

    @distributed_trace_async
    async def get_model(self, model_id: str, **kwargs) -> DigitalTwinsModelData:
        """Get a model, including the model metadata and the model definition.

        :param str model_id: The ID of the model.
        :keyword bool include_model_definition: Include the model definition
            as part of the result. The default value is False.
        :return: The model data.
        :rtype: ~azure.digitaltwins.core.DigitalTwinsModelData
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: If there is no
            model with the provided ID.
        """
        include_model_definition = kwargs.pop("include_model_definition", False)
        return await self._client.digital_twin_models.get_by_id(
            model_id,
            include_model_definition=include_model_definition,
            **kwargs
        )

    @distributed_trace
    def list_models(
        self,
        dependencies_for: Optional[List[str]] = None,
        **kwargs
    ) -> AsyncItemPaged[DigitalTwinsModelData]:
        """Get the list of models.

        :param List[str] dependencies_for: The model IDs to have dependencies retrieved.
            If omitted, all models are retrieved.
        :keyword bool include_model_definition: Include the model definition
            as part of the results. The default value is False.
        :keyword int results_per_page: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of list of model data.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.digitaltwins.core.DigitalTwinsModelData]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        include_model_definition = kwargs.pop('include_model_definition', False)
        results_per_page = kwargs.pop('results_per_page', None)
        digital_twin_models_list_options = None
        if results_per_page is not None:
            digital_twin_models_list_options = {'max_item_count': results_per_page}

        return self._client.digital_twin_models.list(
            dependencies_for=dependencies_for,
            include_model_definition=include_model_definition,
            digital_twin_models_list_options=digital_twin_models_list_options,
            **kwargs
        )

    @distributed_trace_async
    async def create_models(self, dtdl_models: List[object], **kwargs) -> List[DigitalTwinsModelData]:
        """Create one or more models. When any error occurs, no models are uploaded.

        :param List[object] model_list: The set of models to create.
            Each dict corresponds to exactly one model.
        :return: The list of created models
        :rtype: List[~azure.digitaltwins.core.DigitalTwinsModelData]
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceExistsError: One or more of
            the provided models already exist.
        """
        return await self._client.digital_twin_models.add(
            dtdl_models,
            **kwargs
        )

    @distributed_trace_async
    async def decommission_model(self, model_id: str, **kwargs) -> None:
        """Decommissions a model.

        :param str model_id: The ID for the model. The ID is globally unique and case sensitive.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: There is no model
            with the provided ID.
        """
        json_patch = [{'op': 'replace', 'path': '/decommissioned', 'value': True}]
        return await self._client.digital_twin_models.update(
            model_id,
            json_patch,
            **kwargs
        )

    @distributed_trace_async
    async def delete_model(self, model_id: str, **kwargs) -> None:
        """Delete a model.

        :param str model_id: The ID of the model to delete.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: There is no model
            with the provided ID.
        :raises ~azure.core.exceptions.ResourceExistsError: There are dependencies
            on the model that prevent it from being deleted.
        """
        return await self._client.digital_twin_models.delete(
            model_id,
            **kwargs
        )

    @distributed_trace_async
    async def get_event_route(self, event_route_id: str, **kwargs) -> 'DigitalTwinsEventRoute':
        """Get an event route.

        :param str event_route_id: The ID of the event route.
        :return: The event route object.
        :rtype: ~azure.digitaltwins.core.DigitalTwinsEventRoute
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: There is no
            event route with the provided ID.
        """
        return await self._client.event_routes.get_by_id(
            event_route_id,
            **kwargs
        )

    @distributed_trace
    def list_event_routes(self, **kwargs) -> AsyncItemPaged['DigitalTwinsEventRoute']:
        """Retrieves all event routes.

        :keyword int results_per_page: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of event routes.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.digitaltwins.core.DigitalTwinsEventRoute]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        event_routes_list_options = None
        results_per_page = kwargs.pop('results_per_page', None)
        if results_per_page is not None:
            event_routes_list_options = {'max_item_count': results_per_page}

        return self._client.event_routes.list(
            event_routes_list_options=event_routes_list_options,
            **kwargs
        )

    @distributed_trace_async
    async def upsert_event_route(
        self,
        event_route_id: str,
        event_route: 'DigitalTwinsEventRoute',
        **kwargs
    ) -> None:
        """Create or update an event route.

        :param str event_route_id: The ID of the event route to create or update.
        :param ~azure.digitaltwins.core.DigitalTwinsEventRoute event_route: The event route data.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._client.event_routes.add(
            event_route_id,
            event_route=event_route,
            **kwargs
        )

    @distributed_trace_async
    async def delete_event_route(self, event_route_id: str, **kwargs) -> None:
        """Delete an event route.

        :param str event_route_id: The ID of the event route to delete.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError: There is no
            event route with the provided ID.
        """
        return await self._client.event_routes.delete(
            event_route_id,
            **kwargs
        )

    @distributed_trace
    def query_twins(self, query_expression: str, **kwargs) -> AsyncItemPaged[Dict[str, object]]:
        """Query for digital twins.

        Note: that there may be a delay between before changes in your instance are reflected in queries.
        For more details on query limitations, see
        https://docs.microsoft.com/azure/digital-twins/how-to-query-graph#query-limitations

        :param str query_expression: The query expression to execute.
        :return: An iterable of query results.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[Dict[str, object]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        async def extract_data(deserialized):
            list_of_elem = deserialized.value
            return deserialized.continuation_token or None, iter(list_of_elem)

        async def get_next(continuation_token=None):
            query_spec = QuerySpecification(
                query=query_expression,
                continuation_token=continuation_token)
            return await self._client.query.query_twins(query_spec, **kwargs)

        return AsyncItemPaged(
            get_next,
            extract_data
        )
