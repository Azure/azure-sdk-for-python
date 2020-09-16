# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._generated import AzureDigitalTwinsAPI

class DigitalTwinModelsClient(object):
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

    def get_model(self, model_id, include_model_definition=False, **kwargs):
        # type: (str, bool, **Any) -> "models.ModelData"
        """Get a model, including the model metadata and the model definition

        :param model_id: The Id of the model
        :type model_id: str
        :param include_model_definition: When true the model definition
        will be returned as part of the result
        :type include_model_definition: bool
        :**kwargs The operation options
        :type **kwargs: any
        :returns: The ModelDate object
        :rtype: ~azure.digitaltwins.models.ModelData
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.get_by_id(model_id, include_model_definition, **kwargs)

    def list_models(self, dependencies_for, include_model_definition=False, max_item_count=-1, **kwargs):
        # type: (str, bool, int, **Any) -> Iterable["models.PagedModelDataCollection"]
        """Get the list of models

        :param dependencies_for: The model Ids to have dependencies retrieved.
        If omitted, all models are retrieved
        :type dependencies_for: str
        :param include_model_definition: When true the model definition
        will be returned as part of the result
        :type include_model_definition: bool
        :param max_item_count: The maximum number of items to retrieve per request.
        The server may choose to return less than the requested max.
        :type max_item_count: int
        :**kwargs The operation options
        :type **kwargs: any
        :returns: An iterator like instance of either PagedModelDataCollection
        :rtype: ~azure.core.paging.ItemPaged[~azure.digitaltwins.models.PagedModelDataCollection]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        if max_item_count != -1:
            digital_twin_models_list_options = {}
            digital_twin_models_list_options.max_item_count = max_item_count
        return self._client.digital_twin_models.list(
            dependencies_for=dependencies_for,
            include_model_definition=include_model_definition,
            digital_twin_models_list_options=digital_twin_models_list_options, **kwargs
        )

    def create_models(self, models=None, **kwargs):
        # type: (List[object], **Any) -> List["models.ModelData"]
        """Create one or more models. When any error occurs, no models are uploaded.

        :param models: The set of models to create. Each string corresponds to exactly one model.
        :type models: List[object]
        :type **kwargs: any
        :returns: The list of ModelData
        :rtype: List[~azure.digitaltwins.models.ModelData]
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.add(models, **kwargs)

    def decommission_model(self, model_id, model_patch, **kwargs):
        # type: (str, List[object], **Any) -> List["models.ModelData"]
        """Updates the metadata for a model

        :param model_id: The id for the model. The id is globally unique and case sensitive.
        :type model_id: str
        :param update_model: An update specification described by JSON Patch. Only the decommissioned
        property can be replaced.
        :type update_model: List[object]
        :type **kwargs: any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.update(model_id, model_patch, **kwargs)

    def delete_model(self, model_id, **kwargs):
        # type: (str, **Any) -> None
        """Decommission a model using a json patch

        :param model_id: The Id of the model to decommission
        :type model_id: str
        :**kwargs The operation options
        :type **kwargs: any
        :returns: None
        :rtype: None
        :raises :class: `~azure.core.exceptions.HttpResponseError`
        """
        return self._client.digital_twin_models.delete(model_id, **kwargs)
