# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime
from msrest import Serializer, Deserializer
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core import MatchConditions

from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError
)

from ._utils import (
    prep_if_match,
)

from ._generated import models
from ._generated import AzureDigitalTwinsAPI

class DigitalTwinsClient(object):
    """Creates an instance of AzureDigitalTwinsAPI.

    :param str endpoint: The URL endpoint of an Azure search service
    :param ~azure.core.credentials.AzureKeyCredential credential:
        A credential to authenticate requests to the service
    """
    def __init__(self, endpoint, credential, **kwargs: any):
        # type: (str, AzureKeyCredential, dict) -> None

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

    @distributed_trace
    def get_digital_twin(self, digital_twin_id, **kwargs):
        # type: (str, dict) -> dict
        """Get a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :return: Dictionary containing the twin.
        :rtype: dict
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`:
            If the digital twin doesn't exist.
        """
        error_map = {
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.get_by_id(
                digital_twin_id,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def upsert_digital_twin(self, digital_twin_id, digital_twin, **kwargs):
        # type: (str, dict, dict) -> dict
        """Create or update a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param dict digital_twin: Dictionary of the twin to create or update.
        :return: Dictionary containing the created or updated twin.
        :rtype: dict
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`:
            If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceExistsError`:
            If the digital twin is already exist.
        """
        error_map = {
            400: ServiceRequestError,
            412: ResourceExistsError
        }

        try:
            return self._client.digital_twins.add(
                digital_twin_id,
                digital_twin,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceExistsError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def update_digital_twin(
        self,
        digital_twin_id,
        json_patch,
        **kwargs
    ):
        # type: (str, dict, dict) -> None
        """Update a digital twin using a json patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param dict json_patch: An update specification described by JSON Patch.
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            return self._client.digital_twins.update(
                digital_twin_id,
                json_patch,
                if_match=prep_if_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def delete_digital_twin(
        self,
        digital_twin_id,
        **kwargs
    ):
        # type: (str, dict) -> None
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            return self._client.digital_twins.delete(
                digital_twin_id,
                if_match=prep_if_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def get_component(self, digital_twin_id, component_path, **kwargs):
        # type: (str, str, dict) -> dict
        """Get a component on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str component_path: The component being retrieved.
        :return: Dictionary containing the component.
        :rtype: dict
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin with the provided id or the component path is invalid.
        """
        error_map = {
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.get_component(
                digital_twin_id,
                component_path,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def update_component(
        self,
        digital_twin_id,
        component_path,
        json_patch,
        **kwargs
    ):
        # type: (str, str, dict, dict) -> None
        """Update properties of a component on a digital twin using a JSON patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param str component_path: The component being updated.
        :param dict json_patch: An update specification described by JSON Patch.
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            return self._client.digital_twins.update_component(
                digital_twin_id,
                component_path,
                patch_document=json_patch,
                if_match=prep_if_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def get_relationship(self, digital_twin_id, relationship_id, **kwargs):
        # type: (str, str, dict) -> dict
        """Get a relationship on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :return: Dictionary containing the relationship.
        :rtype: dict
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin or relationship with the provided id.
        """
        error_map = {
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.get_relationship_by_id(
                digital_twin_id,
                relationship_id,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def upsert_relationship(self, digital_twin_id, relationship_id, relationship=None, **kwargs):
        # type: (str, str, Optional[dict], dict) -> dict
        """Create or update a relationship on a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :param dict relationship: Dictionary containing the relationship.
        :return: The created or updated relationship.
        :rtype: dict
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is either no
            digital twin, target digital twin or relationship with the provided id.
        """
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.add_relationship(
                id=digital_twin_id,
                relationship_id=relationship_id,
                relationship=relationship,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def update_relationship(
        self,
        digital_twin_id,
        relationship_id,
        json_patch=None,
        **kwargs
    ):
        # type: (str, str, dict, dict) -> None
        """Updates the properties of a relationship on a digital twin using a JSON patch.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to retrieve.
        :param dict json_patch: JSON Patch description of the update
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            return self._client.digital_twins.update_relationship(
                id=digital_twin_id,
                relationship_id=relationship_id,
                json_patch=json_patch,
                if_match=prep_if_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def delete_relationship(
        self,
        digital_twin_id,
        relationship_id,
        **kwargs
    ):
        # type: (str, str, dict) -> None
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
        error_map = {
            404: ResourceNotFoundError
        }
        etag = kwargs.get("etag", None)
        match_condition = kwargs.get("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            return self._client.digital_twins.delete_relationship(
                digital_twin_id,
                relationship_id,
                if_match=prep_if_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def list_relationships(self, digital_twin_id, relationship_id=None, **kwargs):
        # type: (str, Optional[str], dict) -> ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.Relationship]
        """Retrieve relationships for a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :param str relationship_id: The Id of the relationship to
            get (if None all the relationship will be retrieved).
        :return: An iterator instance of list of Relationship
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.Relationship]
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id.
        """
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.list_relationships(
                digital_twin_id,
                relationship_name=relationship_id,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def list_incoming_relationships(self, digital_twin_id, **kwargs):
        # type: (str, str, dict) -> ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.IncomingRelationship]
        """Retrieve all incoming relationships for a digital twin.

        :param str digital_twin_id: The Id of the digital twin.
        :return: An iterator like instance of either Relationship.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.IncomingRelationship]
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: If there is no
            digital twin with the provided id.
        """
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twins.list_incoming_relationships(
                digital_twin_id,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def publish_telemetry(self, digital_twin_id, payload, message_id=None, **kwargs):
        # type: (str, object, Optional[str], dict) -> None
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            if not message_id:
                message_id = uuid.UUID
            timestamp = datetime.now
            return self._client.digital_twins.send_telemetry(
                digital_twin_id,
                message_id,
                telemetry=payload,
                dt_timestamp=timestamp,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def publish_component_telemetry(
        self,
        digital_twin_id,
        component_path,
        payload,
        message_id=None,
        **kwargs
    ):
        # type: (str, str, object, Optional[str], dict) -> None
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            if not message_id:
                message_id = uuid.UUID
            timestamp = datetime.now

            return self._client.digital_twins.send_component_telemetry(
                digital_twin_id,
                component_path,
                dt_id=message_id,
                telemetry=payload,
                dt_timestamp=timestamp,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def get_model(self, model_id, **kwargs):
        # type: (str, dict) -> ~azure.digitaltwins.models.ModelData
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
        error_map = {
            404: ResourceNotFoundError
        }

        try:

            return self._client.digital_twin_models.get_by_id(
                model_id, include_model_definition,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def list_models(self, dependencies_for, **kwargs):
        # type: (str, bool, int, dict) -> ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.ModelData]
        """Get the list of models.

        :param List[str] dependencies_for: The model Ids to have dependencies retrieved.
            If omitted, all models are retrieved.
        :keyword bool include_model_definition: When true the model definition
            will be returned as part of the result.
        :keyword int max_item_count: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of list of ModelData.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        """
        error_map = {
            400: ServiceRequestError
        }
        include_model_definition = kwargs.pop('include_model_definition', False)
        max_item_count = kwargs.pop('max_item_count', -1)
        digital_twin_models_list_options = {'max_item_count': -1}
        if max_item_count != -1:
            digital_twin_models_list_options= {'max_item_count': max_item_count}

        try:
            return self._client.digital_twin_models.list(
                dependencies_for=dependencies_for,
                include_model_definition=include_model_definition,
                digital_twin_models_list_options=digital_twin_models_list_options,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def create_models(self, model_list=None, **kwargs):
        # type: (Optional[List[object]], dict) -> List[~azure.digitaltwins.models.ModelData]
        """Create one or more models. When any error occurs, no models are uploaded.

        :param List[object] model_list: The set of models to create. Each string corresponds to exactly one model.
        :return: The list of ModelData
        :rtype: List[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: If the request is invalid.
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: One or more of
            the provided models already exist.
        """
        error_map = {
            400: ServiceRequestError,
            409: ResourceExistsError
        }

        try:
            return self._client.digital_twin_models.add(
                model_list,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceExistsError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def decommission_model(self, model_id, **kwargs):
        # type: (str, dict) -> None
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError
        }

        try:
            return self._client.digital_twin_models.update(
                model_id,
                json_patch ,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def delete_model(self, model_id, **kwargs):
        # type: (str, dict) -> None
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
        error_map = {
            400: ServiceRequestError,
            404: ResourceNotFoundError,
            409: ResourceExistsError
        }

        try:
            return self._client.digital_twin_models.delete(
                model_id,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except ResourceNotFoundError:
            return None
        except ResourceExistsError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def get_event_route(self, event_route_id, **kwargs):
        # type: (str, dict) -> ~azure.digitaltwins.models.EventRoute
        """Get an event route.

        :param str event_route_id: The Id of the event route.
        :return: The EventRoute object.
        :rtype: ~azure.digitaltwins.models.EventRoute
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no
            event route with the provided id.
        """
        error_map = {
            404: ResourceNotFoundError,
        }

        try:
            return self._client.event_routes.get_by_id(
                event_route_id,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def list_event_routes(self, max_item_count=-1, **kwargs):
        # type: (int, dict) -> ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.EventRoute]
        """Retrieves all event routes.

        :param str max_item_count: The maximum number of items to retrieve per request.
            The server may choose to return less than the requested max.
        :return: An iterator instance of list of EventRoute.
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.EventRoute]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: The request is invalid.
        """
        error_map = {
            400: ServiceRequestError,
        }

        try:
            digital_twin_models_list_options = {'max_item_count': -1}
            if max_item_count != -1:
                digital_twin_models_list_options= {'max_item_count': max_item_count}

            return self._client.event_routes.list(
                digital_twin_models_list_options,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def upsert_event_route(self, event_route_id, event_route, **kwargs):
        # type: (str, "models.EventRoute", dict) -> None
        """Create or update an event route.

        :param str event_route_id: The Id of the event route to create or update.
        :param ~azure.digitaltwins.models.EventRoute event_route: The event route data.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ServiceRequestError`: The request is invalid.
        """
        error_map = {
            400: ServiceRequestError,
        }

        try:
            return self._client.event_routes.add(
                event_route_id, event_route,
                error_map=error_map,
                **kwargs
            )
        except ServiceRequestError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def delete_event_route(self, event_route_id, **kwargs):
        # type: (str, dict) -> None
        """Delete an event route.

        :param str event_route_id: The Id of the event route to delete.
        :return: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        :raises :class: `~azure.core.exceptions.ResourceNotFoundError`: There is no
            event route with the provided id.
        """
        error_map = {
            404: ResourceNotFoundError,
        }

        try:
            return self._client.event_routes.delete(
                event_route_id,
                error_map=error_map,
                **kwargs
            )
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None

    @distributed_trace
    def query_twins(self, query_expression, **kwargs):
        # type: (str, dict) -> ~azure.core.async_paging.ItemPaged[~azure.digitaltwins.models.QueryResult]
        """Query for digital twins.

        :param str query_expression: The query expression to execute.
        :return: The QueryResult object.
        :rtype: ~azure.core.async_paging.ItemPaged[~azure.digitaltwins.models.QueryResult]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        def extract_data(pipeline_response):
            deserialized = self._deserialize('QueryResult', pipeline_response)
            list_of_elem = deserialized.items
            return deserialized.continuation_token or None, iter(list_of_elem)

        def get_next(continuation_token=None):
            query_spec = self._serialize.serialize_dict(
                {'query': query_expression, 'continuation_token': continuation_token},
                'QuerySpecification'
            )
            pipeline_response = self._client.query.query_twins(query_spec, **kwargs)
            return pipeline_response

        return ItemPaged(
            get_next,
            extract_data
        )
