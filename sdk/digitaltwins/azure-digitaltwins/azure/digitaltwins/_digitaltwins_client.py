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

    def get_digital_twin(self, digital_twin_id, **kwargs):
        # type: (str, **Any) -> object
        """Get a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :**kwargs The operation options
        :type **kwargs: any
        :returns: The twin object
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.get_by_id(digital_twin_id, **kwargs)

    def upsert_digital_twin(self, digital_twin_id, digital_twin, **kwargs):
        # type: (str, object, **Any) -> object
        """Create or update a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param digital_twin: The twin object to create or update
        :type digital_twin: object
        :kwargs The operation options
        :type any
        :returns: The created or updated twin object
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.add(digital_twin_id, digital_twin, **kwargs)

    def update_digital_twin(self, digital_twin_id, twin_patch, etag=None, **kwargs):
        # type: (str, object, str, **Any) -> object
        """Update a digital twin using a json patch

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param twin_patch: An update specification described by JSON Patch.
        Updates to property values and $model elements may happen in the same request.
        Operations are limited to add, replace and remove
        :type twin_patch: str
        :param etag: Only perform the operation if the entity's etag matches one of
        the etags provided or * is provided
        :type str
        :kwargs The operation options
        :type any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.update(digital_twin_id, twin_patch, if_match=etag, **kwargs)

    def delete_digital_twin(self, digital_twin_id, etag=None, **kwargs):
        # type: (str, str, **Any) -> object
        """Delete a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param etag: Only perform the operation if the entity's etag matches one of
        the etags provided or * is provided
        :type str
        :kwargs The operation options
        :type any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.delete(digital_twin_id, if_match=etag, **kwargs)

    def get_component(self, digital_twin_id, component_path, **kwargs):
        # type: (str, str, **Any) -> object
        """Get a component on a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param component_path: The component being retrieved
        :type str
        :kwargs The operation options
        :type any
        :returns: The component object
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
        """Update properties of a component on a digital twin using a JSON patch

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param component_path: The component being updated
        :type str
        :param component_patch: An update specification described by JSON Patch
        :type List[object]
        :param etag: Only perform the operation if the entity's etag matches one of
        the etags provided or * is provided
        :type str
        :kwargs The operation options
        :type any
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
        """Get a relationship on a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve
        :type str
        :kwargs The operation options
        :type any
        :returns: The relationship object
        :rtype: object
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.get_relationship_by_id(digital_twin_id, relationship_id, **kwargs)

    def upsert_relationship(self, digital_twin_id, relationship_id, relationship=None, **kwargs):
        # type: (str, str, object, **Any) -> object
        """Create or update a relationship on a digital twin

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve
        :type str
        :param relationship: The relationship object
        :type object
        :kwargs The operation options
        :type any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twins.add_relationship(
            id=digital_twin_id,
            relationship_id=relationship_id,
            relationship=relationship,
            **kwargs
        )

    def update_relationship(self, digital_twin_id, relationship_id, relationship_patch=None, etag=None, **kwargs):
        # type: (str, str, List[object], str, **Any) -> object
        """Updates the properties of a relationship on a digital twin using a JSON patch

        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to retrieve
        :type str
        :param relationship_patch: JSON Patch description of the update to the relationship properties
        :type List[object]
        :param etag: Only perform the operation if the entity's etag matches one of
        the etags provided or * is provided
        :type str
        :kwargs The operation options
        :type any
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
        """Delete a digital twin
        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to delete
        :type relationship_id: str
        :param etag: Only perform the operation if the entity's etag matches one of
        the etags provided or * is provided
        :type etag: str
        :kwargs The operation options
        :type kwargs: any
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
        """Retrieve relationships for a digital twin
        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param relationship_id: The Id of the relationship to get (if None all the relationship will be retrieved)
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
        """Retrieve all incoming relationships for a digital twin
        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :return: An iterator like instance of either RelationshipCollection
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
        one or many destination endpoints (subscribers) defined under
        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param payload: The telemetry payload to be sent
        :type payload: object
        :param message_id: The message Id
        :type message_id: str
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
        one or many destination endpoints (subscribers) defined under
        :param digital_twin_id: The Id of the digital twin
        :type digital_twin_id: str
        :param component_path: The name of the DTDL component
        :type component_path: str
        :param payload: The telemetry payload to be sent
        :type payload: object
        :param message_id: The message Id
        :type message_id: str
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
