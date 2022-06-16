# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

import uuid
from typing import (
    Any,
    Union,
    List,
    Dict,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling.base_polling import LROBasePolling
from azure.core.pipeline import Pipeline
from azure.core.paging import ItemPaged
from ._helpers import TransportWrapper
from ._api_versions import DocumentAnalysisApiVersion
from ._polling import (
    DocumentModelAdministrationPolling,
    DocumentModelAdministrationLROPoller,
)
from ._form_base_client import FormRecognizerClientBase
from ._document_analysis_client import DocumentAnalysisClient
from ._models import (
    DocumentBuildMode,
    DocumentModel,
    DocumentModelInfo,
    ModelOperation,
    ModelOperationInfo,
    AccountInfo,
)

if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential, TokenCredential


class DocumentModelAdministrationClient(FormRecognizerClientBase):
    """DocumentModelAdministrationClient is the Form Recognizer interface to use for building
    and managing models.

    It provides methods for building models, as well as methods for viewing and deleting models,
    viewing document model operations, accessing account information, copying models
    to another Form Recognizer resource, and composing a new model from a collection of existing models.

    .. note:: DocumentModelAdministrationClient should be used with API versions
        2021-09-30-preview and up. To use API versions <=v2.1, instantiate a FormTrainingClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility. To use API versions
        <=v2.1, instantiate a FormTrainingClient.
    :paramtype api_version: str or ~azure.ai.formrecognizer.DocumentAnalysisApiVersion

    .. versionadded:: 2021-09-30-preview
        The *DocumentModelAdministrationClient* and its client methods.

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.2-beta/sample_authentication.py
            :start-after: [START create_dt_client_with_key]
            :end-before: [END create_dt_client_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentModelAdministrationClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.2-beta/sample_authentication.py
            :start-after: [START create_dt_client_with_aad]
            :end-before: [END create_dt_client_with_aad]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentModelAdministrationClient with a token credential.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        api_version = kwargs.pop(
            "api_version", DocumentAnalysisApiVersion.V2022_06_30_PREVIEW
        )
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            api_version=api_version,
            client_kind="document",
            **kwargs
        )

    @distributed_trace
    def begin_build_model(self, source: str, build_mode: Union[str, DocumentBuildMode], **kwargs: Any) -> DocumentModelAdministrationLROPoller[DocumentModel]:
        """Build a custom model.

        The request must include a `source` parameter that is an
        externally accessible Azure storage blob container URI (preferably a Shared Access Signature URI). Note that
        a container URI (without SAS) is accepted only when the container is public or has a managed identity
        configured, see more about configuring managed identities to work with Form Recognizer here:
        https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/managed-identities.
        Models are built using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff', or 'image/bmp'. Other types of content in the container is ignored.

        :param str source: An Azure Storage blob container's SAS URI. A container URI (without SAS)
            can be used if the container is public or has a managed identity configured. For more information on
            setting up a training data set, see: https://aka.ms/azsdk/formrecognizer/buildtrainingset.
        :param build_mode: The custom model build mode. Possible values include: "template", "neural".
            For more information about build modes, see: https://aka.ms/azsdk/formrecognizer/buildmode.
        :type build_mode: str or :class:`~azure.ai.formrecognizer.DocumentBuildMode`
        :keyword str model_id: A unique ID for your model. If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path.
            For example, when using an Azure storage blob URI, use the prefix to restrict sub folders.
            `prefix` should end in '/' to avoid cases where filenames share the same prefix.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an DocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModel`.
        :rtype: ~azure.ai.formrecognizer.DocumentModelAdministrationLROPoller[DocumentModel]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2022-01-30-preview
            The required *build_mode* parameter and *tags* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_build_model.py
                :start-after: [START build_model]
                :end-before: [END build_model]
                :language: python
                :dedent: 4
                :caption: Building a model from training files.
        """

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = self._deserialize(
                self._generated_models.GetOperationResponse, raw_response
            )
            model_info = self._deserialize(
                self._generated_models.ModelInfo, op_response.result
            )
            return DocumentModel._from_generated(model_info)

        description = kwargs.pop("description", None)
        model_id = kwargs.pop("model_id", None)
        tags = kwargs.pop("tags", None)
        cls = kwargs.pop("cls", callback)
        continuation_token = kwargs.pop("continuation_token", None)
        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval
        )

        if model_id is None:
            model_id = str(uuid.uuid4())

        return self._client.begin_build_document_model(  # type: ignore
            build_request=self._generated_models.BuildDocumentModelRequest(
                model_id=model_id,
                build_mode=build_mode,
                description=description,
                tags=tags,
                azure_blob_source=self._generated_models.AzureBlobContentSource(
                    container_url=source,
                    prefix=kwargs.pop("prefix", None),
                ),
            ),
            cls=cls,
            continuation_token=continuation_token,
            polling=LROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[DocumentModelAdministrationPolling()],
                **kwargs
            ),
            **kwargs
        )

    @distributed_trace
    def begin_create_composed_model(self, component_model_ids: List[str], **kwargs: Any) -> DocumentModelAdministrationLROPoller[DocumentModel]:
        """Creates a composed model from a collection of existing models.

        A composed model allows multiple models to be called with a single model ID. When a document is
        submitted to be analyzed with a composed model ID, a classification step is first performed to
        route it to the correct custom model.

        :param list[str] component_model_ids: List of model IDs to use in the composed model.
        :keyword str model_id: A unique ID for your composed model.
            If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an DocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModel`.
        :rtype: ~azure.ai.formrecognizer.DocumentModelAdministrationLROPoller[DocumentModel]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2022-01-30-preview
            The *tags* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_create_composed_model.py
                :start-after: [START composed_model]
                :end-before: [END composed_model]
                :language: python
                :dedent: 4
                :caption: Creating a composed model with existing models.
        """

        def _compose_callback(
            raw_response, _, headers
        ):  # pylint: disable=unused-argument
            op_response = self._deserialize(
                self._generated_models.GetOperationResponse, raw_response
            )
            model_info = self._deserialize(
                self._generated_models.ModelInfo, op_response.result
            )
            return DocumentModel._from_generated(model_info)

        model_id = kwargs.pop("model_id", None)
        description = kwargs.pop("description", None)
        tags = kwargs.pop("tags", None)
        continuation_token = kwargs.pop("continuation_token", None)
        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval
        )

        if model_id is None:
            model_id = str(uuid.uuid4())

        return self._client.begin_compose_document_model(  # type: ignore
            compose_request=self._generated_models.ComposeDocumentModelRequest(
                model_id=model_id,
                description=description,
                tags=tags,
                component_models=[
                    self._generated_models.ComponentModelInfo(model_id=model_id)
                    for model_id in component_model_ids
                ]
                if component_model_ids
                else [],
            ),
            cls=kwargs.pop("cls", _compose_callback),
            polling=LROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[DocumentModelAdministrationPolling()],
                **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def get_copy_authorization(self, **kwargs: Any) -> dict[str, str]:
        """Generate authorization for copying a custom model into the target Form Recognizer resource.

        This should be called by the target resource (where the model will be copied to)
        and the output can be passed as the `target` parameter into :func:`~begin_copy_model_to()`.

        :keyword str model_id: A unique ID for your copied model.
            If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :return: A dictionary with values necessary for the copy authorization.
        :rtype: Dict[str, str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2022-01-30-preview
            The *tags* keyword argument
        """

        model_id = kwargs.pop("model_id", None)
        description = kwargs.pop("description", None)
        tags = kwargs.pop("tags", None)

        if model_id is None:
            model_id = str(uuid.uuid4())

        response = self._client.authorize_copy_document_model(
            authorize_copy_request=self._generated_models.AuthorizeCopyRequest(
                model_id=model_id, description=description, tags=tags
            ),
            **kwargs
        )
        target = response.serialize()  # type: ignore
        return target

    @distributed_trace
    def begin_copy_model_to(
        self,
        model_id: str,
        target: dict,
        **kwargs: Any
    ) -> DocumentModelAdministrationLROPoller[DocumentModel]:
        """Copy a model stored in this resource (the source) to the user specified
        target Form Recognizer resource.

        This should be called with the source Form Recognizer resource
        (with the model that is intended to be copied). The `target` parameter should be supplied from the
        target resource's output from calling the :func:`~get_copy_authorization()` method.

        :param str model_id: Model identifier of the model to copy to target resource.
        :param dict target:
            The copy authorization generated from the target resource's call to
            :func:`~get_copy_authorization()`.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of a DocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModel`.
        :rtype: ~azure.ai.formrecognizer.DocumentModelAdministrationLROPoller[DocumentModel]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_copy_model.py
                :start-after: [START begin_copy_model_to]
                :end-before: [END begin_copy_model_to]
                :language: python
                :dedent: 4
                :caption: Copy a model from the source resource to the target resource
        """

        def _copy_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = self._deserialize(
                self._generated_models.GetOperationResponse, raw_response
            )
            model_info = self._deserialize(
                self._generated_models.ModelInfo, op_response.result
            )
            return DocumentModel._from_generated(model_info)

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval
        )
        continuation_token = kwargs.pop("continuation_token", None)

        return self._client.begin_copy_document_model_to(  # type: ignore
            model_id=model_id,
            copy_to_request=self._generated_models.CopyAuthorization(
                target_resource_id=target["targetResourceId"],
                target_resource_region=target["targetResourceRegion"],
                target_model_id=target["targetModelId"],
                access_token=target["accessToken"],
                expiration_date_time=target["expirationDateTime"],
                target_model_location=target["targetModelLocation"],
            )
            if target
            else None,
            cls=kwargs.pop("cls", _copy_callback),
            polling=LROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[DocumentModelAdministrationPolling()],
                **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def delete_model(self, model_id: str, **kwargs: Any) -> None:
        """Delete a custom model.

        :param model_id: Model identifier.
        :type model_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_manage_models.py
                :start-after: [START delete_model]
                :end-before: [END delete_model]
                :language: python
                :dedent: 4
                :caption: Delete a model.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        return self._client.delete_model(model_id=model_id, **kwargs)

    @distributed_trace
    def list_models(self, **kwargs: Any) -> ItemPaged[DocumentModelInfo]:
        """List information for each model, including its model ID,
        description, and when it was created.

        :return: Pageable of DocumentModelInfo.
        :rtype: ~azure.core.paging.ItemPaged[DocumentModelInfo]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_manage_models.py
                :start-after: [START list_models]
                :end-before: [END list_models]
                :language: python
                :dedent: 4
                :caption: List all models that were built successfully under the Form Recognizer resource.
        """

        return self._client.get_models(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda objs: [DocumentModelInfo._from_generated(x) for x in objs],
            ),
            **kwargs
        )

    @distributed_trace
    def get_account_info(self, **kwargs: Any) -> AccountInfo:
        """Get information about the models under the Form Recognizer resource.

        :return: Summary of models under the resource - model count and limit.
        :rtype: ~azure.ai.formrecognizer.AccountInfo
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_manage_models.py
                :start-after: [START get_account_info]
                :end-before: [END get_account_info]
                :language: python
                :dedent: 4
                :caption: Get model counts and limits under the Form Recognizer resource.
        """

        response = self._client.get_info(**kwargs)
        return AccountInfo._from_generated(response.custom_document_models)

    @distributed_trace
    def get_model(self, model_id: str, **kwargs: Any) -> DocumentModel:
        """Get a model by its ID.

        :param str model_id: Model identifier.
        :return: DocumentModel
        :rtype: ~azure.ai.formrecognizer.DocumentModel
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_manage_models.py
                :start-after: [START get_model]
                :end-before: [END get_model]
                :language: python
                :dedent: 4
                :caption: Get a model by its ID.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        response = self._client.get_model(model_id=model_id, **kwargs)
        return DocumentModel._from_generated(response)

    @distributed_trace
    def list_operations(self, **kwargs: Any) -> ItemPaged[ModelOperationInfo]:
        """List information for each document model operation.

        Lists all document model operations associated with the Form Recognizer resource.
        Note that operation information only persists for 24 hours. If the operation was successful,
        the document model can be accessed using the :func:`~get_model` or :func:`~list_models` APIs.

        :return: A pageable of ModelOperationInfo.
        :rtype: ~azure.core.paging.ItemPaged[ModelOperationInfo]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_get_operations.py
                :start-after: [START list_operations]
                :end-before: [END list_operations]
                :language: python
                :dedent: 4
                :caption: List all document model operations in the past 24 hours.
        """

        return self._client.get_operations(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda objs: [ModelOperationInfo._from_generated(x) for x in objs],
            ),
            **kwargs
        )

    @distributed_trace
    def get_operation(self, operation_id: str, **kwargs: Any) -> ModelOperation:
        """Get a document model operation by its ID.

        Get a document model operation associated with the Form Recognizer resource.
        Note that operation information only persists for 24 hours. If the operation was successful,
        the document model can be accessed using the :func:`~get_model` or :func:`~list_models` APIs.

        :param str operation_id: The operation ID.
        :return: ModelOperation
        :rtype: ~azure.ai.formrecognizer.ModelOperation
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/sample_get_operations.py
                :start-after: [START get_operation]
                :end-before: [END get_operation]
                :language: python
                :dedent: 4
                :caption: Get a document model operation by its ID.
        """

        if not operation_id:
            raise ValueError("'operation_id' cannot be None or empty.")

        return ModelOperation._from_generated(
            self._client.get_operation(operation_id, **kwargs),
            api_version=self._api_version,
        )

    def get_document_analysis_client(self, **kwargs: Any) -> DocumentAnalysisClient:
        """Get an instance of a DocumentAnalysisClient from DocumentModelAdministrationClient.

        :rtype: ~azure.ai.formrecognizer.DocumentAnalysisClient
        :return: A DocumentAnalysisClient
        """

        _pipeline = Pipeline(
            transport=TransportWrapper(self._client._client._pipeline._transport),
            policies=self._client._client._pipeline._impl_policies,
        )  # type: Pipeline
        client = DocumentAnalysisClient(
            endpoint=self._endpoint,
            credential=self._credential,
            pipeline=_pipeline,
            api_version=self._api_version,
            **kwargs
        )
        # need to share config, but can't pass as a keyword into client
        client._client._config = self._client._client._config
        return client

    def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.DocumentModelAdministrationClient` session."""
        return self._client.close()

    def __enter__(self) -> "DocumentModelAdministrationClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member
