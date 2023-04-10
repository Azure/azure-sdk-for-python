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
    overload,
    Optional,
    Mapping
)
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import AsyncPipeline
from azure.core.async_paging import AsyncItemPaged
from ._helpers_async import AsyncTransportWrapper
from ._document_analysis_client_async import DocumentAnalysisClient
from ._async_polling import AsyncDocumentModelAdministrationLROPoller
from ._form_base_client_async import FormRecognizerClientBaseAsync
from .._api_versions import DocumentAnalysisApiVersion
from .._polling import DocumentModelAdministrationPolling
from .._models import (
    ModelBuildMode,
    DocumentClassifierDetails,
    DocumentModelDetails,
    DocumentModelSummary,
    OperationDetails,
    OperationSummary,
    ResourceDetails,
    TargetAuthorization,
)
from .._generated.models import ClassifierDocumentTypeDetails


class DocumentModelAdministrationClient(FormRecognizerClientBaseAsync):
    """DocumentModelAdministrationClient is the Form Recognizer interface to use for building
    and managing models.

    It provides methods for building models, as well as methods for viewing and deleting models,
    viewing model operations, accessing account information, copying models to another
    Form Recognizer resource, and composing a new model from a collection of existing models.

    .. note:: DocumentModelAdministrationClient should be used with API versions
        2022-08-31 and up. To use API versions <=v2.1, instantiate a FormTrainingClient.

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

    .. versionadded:: 2022-08-31
        The *DocumentModelAdministrationClient* and its client methods.

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.2/async_samples/sample_authentication_async.py
            :start-after: [START create_dt_client_with_key_async]
            :end-before: [END create_dt_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentModelAdministrationClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.2/async_samples/sample_authentication_async.py
            :start-after: [START create_dt_client_with_aad_async]
            :end-before: [END create_dt_client_with_aad_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentModelAdministrationClient with a token credential.
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        api_version = kwargs.pop("api_version", DocumentAnalysisApiVersion.V2023_02_28_PREVIEW)
        super().__init__(
            endpoint=endpoint, credential=credential, api_version=api_version, client_kind="document", **kwargs
        )

    @overload
    async def begin_build_document_model(
        self,
        build_mode: Union[str, ModelBuildMode],
        *,
        blob_container_url: str,
        prefix: Optional[str] = None,
        model_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Mapping[str, str]] = None,
        **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]:
        ...

    @overload
    async def begin_build_document_model(
        self,
        build_mode: Union[str, ModelBuildMode],
        *,
        blob_container_url: str,
        file_list: str,
        model_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Mapping[str, str]] = None,
        **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]:
        ...

    @distributed_trace_async
    async def begin_build_document_model(
        self, build_mode: Union[str, ModelBuildMode], *, blob_container_url: str, **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]:
        """Build a custom document model.

        The request must include a `blob_container_url` keyword parameter that is an
        externally accessible Azure storage blob container URI (preferably a Shared Access Signature URI). Note that
        a container URI (without SAS) is accepted only when the container is public or has a managed identity
        configured, see more about configuring managed identities to work with Form Recognizer here:
        https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/managed-identities.
        Models are built using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff', 'image/bmp', or 'image/heif'. Other types of content in the container
        is ignored.

        :param build_mode: The custom model build mode. Possible values include: "template", "neural".
            For more information about build modes, see: https://aka.ms/azsdk/formrecognizer/buildmode.
        :type build_mode: str or :class:`~azure.ai.formrecognizer.ModelBuildMode`
        :keyword str blob_container_url: An Azure Storage blob container's SAS URI. A container URI (without SAS)
            can be used if the container is public or has a managed identity configured. For more information on
            setting up a training data set, see: https://aka.ms/azsdk/formrecognizer/buildtrainingset.
        :keyword str model_id: A unique ID for your model. If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the blob container url path.
            For example, when using an Azure storage blob URI, use the prefix to restrict sub folders.
            `prefix` should end in '/' to avoid cases where filenames share the same prefix.
        :keyword str file_list: Path to a JSONL file within the container specifying a subset of
            documents for training.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :return: An instance of an AsyncDocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModelDetails`.
        :rtype: ~azure.ai.formrecognizer.aio.AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-02-28-preview
            The *file_list* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_build_model_async.py
                :start-after: [START build_model_async]
                :end-before: [END build_model_async]
                :language: python
                :dedent: 4
                :caption: Building a model from training files.
        """

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = self._deserialize(self._generated_models.DocumentModelBuildOperationDetails, raw_response)
            model_info = self._deserialize(self._generated_models.DocumentModelDetails, op_response.result)
            return DocumentModelDetails._from_generated(model_info)

        description = kwargs.pop("description", None)
        model_id = kwargs.pop("model_id", None)
        tags = kwargs.pop("tags", None)
        cls = kwargs.pop("cls", callback)
        continuation_token = kwargs.pop("continuation_token", None)
        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)
        prefix = kwargs.pop("prefix", None)
        file_list = kwargs.pop("file_list", None)

        if model_id is None:
            model_id = str(uuid.uuid4())

        azure_blob_source = None
        azure_blob_file_list_source = None
        if prefix:
            azure_blob_source = self._generated_models.AzureBlobContentSource(
                container_url=blob_container_url,
                prefix=prefix
            )
        if file_list:
            azure_blob_file_list_source = self._generated_models.AzureBlobFileListSource(
                container_url=blob_container_url,
                file_list=file_list
            )
        if not azure_blob_source and not azure_blob_file_list_source:
            azure_blob_source = self._generated_models.AzureBlobContentSource(
                container_url=blob_container_url,
            )

        model_kwargs = {}
        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.begin_build_document_model
            if file_list:
                raise ValueError(
                    "Keyword argument 'file_list' is only available for API version V2023_02_28_PREVIEW and later."
                )
        else:
            _client_op_path = self._client.document_models.begin_build_model
            model_kwargs.update({"azure_blob_file_list_source": azure_blob_file_list_source})
        return await _client_op_path(  # type: ignore
            build_request=self._generated_models.BuildDocumentModelRequest(
                model_id=model_id,
                build_mode=build_mode,
                description=description,
                tags=tags,
                azure_blob_source=azure_blob_source,
                **model_kwargs
            ),
            cls=cls,
            continuation_token=continuation_token,
            polling=AsyncLROBasePolling(
                timeout=polling_interval, lro_algorithms=[DocumentModelAdministrationPolling()], **kwargs
            ),
            **kwargs
        )

    @distributed_trace_async
    async def begin_compose_document_model(
        self, component_model_ids: List[str], **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]:
        """Creates a composed document model from a collection of existing models.

        A composed model allows multiple models to be called with a single model ID. When a document is
        submitted to be analyzed with a composed model ID, a classification step is first performed to
        route it to the correct custom model.

        :param list[str] component_model_ids: List of model IDs to use in the composed model.
        :keyword str model_id: A unique ID for your composed model.
            If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :return: An instance of an AsyncDocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModelDetails`.
        :rtype: ~azure.ai.formrecognizer.aio.AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_compose_model_async.py
                :start-after: [START composed_model_async]
                :end-before: [END composed_model_async]
                :language: python
                :dedent: 4
                :caption: Creating a composed model with existing models.
        """

        def _compose_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = self._deserialize(self._generated_models.DocumentModelComposeOperationDetails, raw_response)
            model_info = self._deserialize(self._generated_models.DocumentModelDetails, op_response.result)
            return DocumentModelDetails._from_generated(model_info)

        model_id = kwargs.pop("model_id", None)
        description = kwargs.pop("description", None)
        tags = kwargs.pop("tags", None)
        continuation_token = kwargs.pop("continuation_token", None)
        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)

        if model_id is None:
            model_id = str(uuid.uuid4())

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.begin_compose_document_model
        else:
            _client_op_path = self._client.document_models.begin_compose_model
        return await _client_op_path(  # type: ignore
            compose_request=self._generated_models.ComposeDocumentModelRequest(
                model_id=model_id,
                description=description,
                tags=tags,
                component_models=[
                    self._generated_models.ComponentDocumentModelDetails(model_id=model_id)
                    for model_id in component_model_ids
                ]
                if component_model_ids
                else [],
            ),
            cls=kwargs.pop("cls", _compose_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval, lro_algorithms=[DocumentModelAdministrationPolling()], **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def get_copy_authorization(self, **kwargs: Any) -> TargetAuthorization:
        """Generate authorization for copying a custom model into the target Form Recognizer resource.

        This should be called by the target resource (where the model will be copied to)
        and the output can be passed as the `target` parameter into :func:`~begin_copy_document_model_to()`.

        :keyword str model_id: A unique ID for your copied model.
            If not specified, a model ID will be created for you.
        :keyword str description: An optional description to add to the model.
        :keyword tags: List of user defined key-value tag attributes associated with the model.
        :paramtype tags: dict[str, str]
        :return: A dictionary with values necessary for the copy authorization.
        :rtype: ~azure.ai.formrecognizer.TargetAuthorization
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        model_id = kwargs.pop("model_id", None)
        description = kwargs.pop("description", None)
        tags = kwargs.pop("tags", None)

        if model_id is None:
            model_id = str(uuid.uuid4())

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.authorize_copy_document_model
        else:
            _client_op_path = self._client.document_models.authorize_model_copy
        response = await _client_op_path(
            authorize_copy_request=self._generated_models.AuthorizeCopyRequest(
                model_id=model_id, description=description, tags=tags
            ),
            **kwargs
        )
        target = response.serialize()  # type: ignore
        return target

    @distributed_trace_async
    async def begin_copy_document_model_to(
        self, model_id: str, target: TargetAuthorization, **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]:
        """Copy a document model stored in this resource (the source) to the user specified
        target Form Recognizer resource.

        This should be called with the source Form Recognizer resource
        (with the model that is intended to be copied). The `target` parameter should be supplied from the
        target resource's output from calling the :func:`~get_copy_authorization()` method.

        :param str model_id: Model identifier of the model to copy to target resource.
        :param ~azure.ai.formrecognizer.TargetAuthorization target:
            The copy authorization generated from the target resource's call to
            :func:`~get_copy_authorization()`.
        :return: An instance of a AsyncDocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentModelDetails`.
        :rtype: ~azure.ai.formrecognizer.aio.AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_copy_model_to_async.py
                :start-after: [START begin_copy_document_model_to_async]
                :end-before: [END begin_copy_document_model_to_async]
                :language: python
                :dedent: 4
                :caption: Copy a model from the source resource to the target resource
        """

        def _copy_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = self._deserialize(self._generated_models.DocumentModelCopyToOperationDetails, raw_response)
            model_info = self._deserialize(self._generated_models.DocumentModelDetails, op_response.result)
            return DocumentModelDetails._from_generated(model_info)

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)
        continuation_token = kwargs.pop("continuation_token", None)

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.begin_copy_document_model_to
        else:
            _client_op_path = self._client.document_models.begin_copy_model_to
        return await _client_op_path(  # type: ignore
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
            polling=AsyncLROBasePolling(
                timeout=polling_interval, lro_algorithms=[DocumentModelAdministrationPolling()], **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def delete_document_model(self, model_id: str, **kwargs: Any) -> None:
        """Delete a custom document model.

        :param model_id: Model identifier.
        :type model_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_models_async.py
                :start-after: [START delete_document_model_async]
                :end-before: [END delete_document_model_async]
                :language: python
                :dedent: 8
                :caption: Delete a model.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.delete_document_model
        else:
            _client_op_path = self._client.document_models.delete_model
        return await _client_op_path(model_id=model_id, **kwargs)

    @distributed_trace
    def list_document_models(self, **kwargs: Any) -> AsyncItemPaged[DocumentModelSummary]:
        """List information for each model, including its model ID,
        description, and when it was created.

        :return: Pageable of DocumentModelSummary.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[DocumentModelSummary]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_models_async.py
                :start-after: [START list_document_models_async]
                :end-before: [END list_document_models_async]
                :language: python
                :dedent: 8
                :caption: List all models that were built successfully under the Form Recognizer resource.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.get_document_models
        else:
            _client_op_path = self._client.document_models.list_models
        return _client_op_path(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda objs: [DocumentModelSummary._from_generated(x) for x in objs],
            ),
            **kwargs
        )

    @distributed_trace_async
    async def get_resource_details(self, **kwargs: Any) -> ResourceDetails:
        """Get information about the models under the Form Recognizer resource.

        :return: Summary of custom models under the resource - model count and limit.
        :rtype: ~azure.ai.formrecognizer.ResourceDetails
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_models_async.py
                :start-after: [START get_resource_details_async]
                :end-before: [END get_resource_details_async]
                :language: python
                :dedent: 4
                :caption: Get model counts and limits under the Form Recognizer resource.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.get_resource_details
        else:
            _client_op_path = self._client.miscellaneous.get_resource_info
        response = await _client_op_path(**kwargs)
        return ResourceDetails._from_generated(response)

    @distributed_trace_async
    async def get_document_model(self, model_id: str, **kwargs: Any) -> DocumentModelDetails:
        """Get a document model by its ID.

        :param str model_id: Model identifier.
        :return: DocumentModelDetails
        :rtype: ~azure.ai.formrecognizer.DocumentModelDetails
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_models_async.py
                :start-after: [START get_document_model_async]
                :end-before: [END get_document_model_async]
                :language: python
                :dedent: 8
                :caption: Get a model by its ID.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.get_document_model
        else:
            _client_op_path = self._client.document_models.get_model
        response = await _client_op_path(model_id=model_id, **kwargs)
        return DocumentModelDetails._from_generated(response)

    @distributed_trace
    def list_operations(self, **kwargs: Any) -> AsyncItemPaged[OperationSummary]:
        """List information for each operation.

        Lists all operations associated with the Form Recognizer resource.
        Note that operation information only persists for 24 hours. If the document model operation was successful,
        the document model can be accessed using the :func:`~get_document_model` or :func:`~list_document_models` APIs.

        :return: A pageable of OperationSummary.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[OperationSummary]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_get_operations_async.py
                :start-after: [START list_operations_async]
                :end-before: [END list_operations_async]
                :language: python
                :dedent: 4
                :caption: List all document model operations in the past 24 hours.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.get_operations
        else:
            _client_op_path = self._client.miscellaneous.list_operations
        return _client_op_path(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda objs: [OperationSummary._from_generated(x) for x in objs],
            ),
            **kwargs
        )

    @distributed_trace_async
    async def get_operation(self, operation_id: str, **kwargs: Any) -> OperationDetails:
        """Get an operation by its ID.

        Get an operation associated with the Form Recognizer resource.
        Note that operation information only persists for 24 hours. If the document model operation was successful,
        the model can be accessed using the :func:`~get_document_model` or :func:`~list_document_models` APIs.

        :param str operation_id: The operation ID.
        :return: OperationDetails
        :rtype: ~azure.ai.formrecognizer.OperationDetails
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_get_operations_async.py
                :start-after: [START get_operation_async]
                :end-before: [END get_operation_async]
                :language: python
                :dedent: 8
                :caption: Get a document model operation by its ID.
        """

        if not operation_id:
            raise ValueError("'operation_id' cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client.get_operation
        else:
            _client_op_path = self._client.miscellaneous.get_operation
        return OperationDetails._from_generated(
            await _client_op_path(operation_id, **kwargs),
            api_version=self._api_version,
        )

    @distributed_trace_async
    async def begin_build_document_classifier(
        self,
        doc_types: Mapping[str, ClassifierDocumentTypeDetails],
        *,
        classifier_id: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncDocumentModelAdministrationLROPoller[DocumentClassifierDetails]:
        """Build a document classifier. For more information on how to build and train
        a custom classifier model, see https://aka.ms/azsdk/formrecognizer/buildclassifiermodel.

        :param doc_types: Required. Mapping of document types to classify against.
        :keyword str classifier_id: Unique document classifier name.
            If not specified, a classifier ID will be created for you.
        :keyword str description: Document classifier description.
        :return: An instance of an AsyncDocumentModelAdministrationLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.DocumentClassifierDetails`.
        :rtype: ~azure.ai.formrecognizer.aio.AsyncDocumentModelAdministrationLROPoller[DocumentClassifierDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-02-28-preview
            The *begin_build_document_classifier* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_build_classifier_async.py
                :start-after: [START build_classifier_async]
                :end-before: [END build_classifier_async]
                :language: python
                :dedent: 4
                :caption: Build a document classifier.
        """
        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            op_response = \
                self._deserialize(self._generated_models.DocumentClassifierBuildOperationDetails, raw_response)
            model_info = self._deserialize(self._generated_models.DocumentClassifierDetails, op_response.result)
            return DocumentClassifierDetails._from_generated(model_info)

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'begin_build_document_classifier()' is only available for API version "
                             "V2023_02_28_PREVIEW and later")
        cls = kwargs.pop("cls", callback)
        continuation_token = kwargs.pop("continuation_token", None)
        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)
        if classifier_id is None:
            classifier_id = str(uuid.uuid4())

        return await self._client.document_classifiers.begin_build_classifier(
            build_request=self._generated_models.BuildDocumentClassifierRequest(
                classifier_id=classifier_id,
                description=description,
                doc_types=doc_types,
            ),
            cls=cls,
            continuation_token=continuation_token,
            polling=AsyncLROBasePolling(
                timeout=polling_interval, lro_algorithms=[DocumentModelAdministrationPolling()], **kwargs
            ),
            **kwargs
        )

    @distributed_trace_async
    async def get_document_classifier(self, classifier_id: str, **kwargs: Any) -> DocumentClassifierDetails:
        """Get a document classifier by its ID.

        :param str classifier_id: Classifier identifier.
        :return: DocumentClassifierDetails
        :rtype: ~azure.ai.formrecognizer.DocumentClassifierDetails
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. versionadded:: 2023-02-28-preview
            The *get_document_classifier* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_classifiers_async.py
                :start-after: [START get_document_classifier_async]
                :end-before: [END get_document_classifier_async]
                :language: python
                :dedent: 8
                :caption: Get a classifier by its ID.
        """

        if not classifier_id:
            raise ValueError("classifier_id cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'get_document_classifier()' is only available for API version "
                             "V2023_02_28_PREVIEW and later")
        response = await self._client.document_classifiers.get_classifier(classifier_id=classifier_id, **kwargs)
        return DocumentClassifierDetails._from_generated(response)

    @distributed_trace
    def list_document_classifiers(self, **kwargs: Any) -> AsyncItemPaged[DocumentClassifierDetails]:
        """List information for each document classifier, including its classifier ID,
        description, and when it was created.

        :return: Pageable of DocumentClassifierDetails.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[DocumentClassifierDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-02-28-preview
            The *list_document_classifiers* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_classifiers_async.py
                :start-after: [START list_document_classifiers_async]
                :end-before: [END list_document_classifiers_async]
                :language: python
                :dedent: 8
                :caption: List all classifiers that were built successfully under the Form Recognizer resource.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'list_document_classifiers()' is only available for API version "
                             "V2023_02_28_PREVIEW and later")
        return self._client.document_classifiers.list_classifiers(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda objs: [DocumentClassifierDetails._from_generated(x) for x in objs],
            ),
            **kwargs
        )

    @distributed_trace_async
    async def delete_document_classifier(self, classifier_id: str, **kwargs: Any) -> None:
        """Delete a document classifier.

        :param str classifier_id: Classifier identifier.
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. versionadded:: 2023-02-28-preview
            The *delete_document_classifier* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2/async_samples/sample_manage_classifiers_async.py
                :start-after: [START delete_document_classifier_async]
                :end-before: [END delete_document_classifier_async]
                :language: python
                :dedent: 8
                :caption: Delete a classifier.
        """

        if not classifier_id:
            raise ValueError("classifier_id cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'delete_document_classifier()' is only available for API version "
                             "V2023_02_28_PREVIEW and later")
        return await self._client.document_classifiers.delete_classifier(classifier_id=classifier_id, **kwargs)

    def get_document_analysis_client(self, **kwargs: Any) -> DocumentAnalysisClient:
        """Get an instance of a DocumentAnalysisClient from DocumentModelAdministrationClient.

        :rtype: ~azure.ai.formrecognizer.aio.DocumentAnalysisClient
        :return: A DocumentAnalysisClient
        """

        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._client._client._pipeline._transport),
            policies=self._client._client._pipeline._impl_policies,  # type: ignore
        )
        client = DocumentAnalysisClient(
            endpoint=self._endpoint,
            credential=self._credential,
            pipeline=_pipeline,
            api_version=self._api_version,
            **kwargs
        )
        # need to share config, but can't pass as a keyword into client
        client._client._config = self._client._config
        return client

    async def __aenter__(self) -> "DocumentModelAdministrationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.aio.DocumentModelAdministrationClient` session."""
        await self._client.__aexit__()
