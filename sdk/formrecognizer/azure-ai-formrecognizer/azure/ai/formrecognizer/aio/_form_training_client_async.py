# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (  # pylint: disable=unused-import
    Optional,
    Any,
    Iterable,
    TYPE_CHECKING,
)
from azure.core.polling import async_poller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from .._generated.aio._form_recognizer_client_async import FormRecognizerClient as FormRecognizer
from .._generated.models import TrainRequest, TrainSourceFilter
from .._generated.models import Model
from .._helpers import POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from .._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
)
from .._user_agent import USER_AGENT
from .._polling import TrainingPolling
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential


class FormTrainingClient(object):
    """FormTrainingClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    """

    def __init__(
            self,
            endpoint: str,
            credential: "AzureKeyCredential",
            **kwargs: Any
    ) -> None:
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=AzureKeyCredentialPolicy(credential, COGNITIVE_KEY_HEADER),
            **kwargs
        )

    @distributed_trace_async
    async def begin_training(
            self,
            source: str,
            source_prefix_filter: Optional[str] = "",
            include_sub_folders: Optional[bool] = False,
            **kwargs: Any
    ) -> CustomModel:
        """Create and train a custom model. The request must include a source parameter that is an
        externally accessible Azure storage blob container Uri (preferably a Shared Access Signature Uri).
        Models are trained using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content in the container is ignored.

        :param str source: An Azure Storage blob container URI.
        :param str source_prefix_filter: A case-sensitive prefix string to filter documents in the source path for
            training. For example, when using a Azure storage blob Uri, use the prefix to restrict sub
            folders for training.
        :param bool include_sub_folders: A flag to indicate if sub folders within the set of prefix folders
            will also need to be included when searching for content to be preprocessed.
        :return: CustomModel
        :rtype: ~azure.ai.formrecognizer.CustomModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        cls = kwargs.pop("cls", None)
        response = await self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                )
            ),
            cls=lambda pipeline_response, _, response_headers: pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomModel._from_generated(model)

        deserialization_callback = cls if cls else callback
        return await async_poller(
            self._client._client,
            response,
            deserialization_callback,
            AsyncLROBasePolling(timeout=POLLING_INTERVAL, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace_async
    async def begin_labeled_training(
            self,
            source,
            source_prefix_filter: Optional[str] = "",
            include_sub_folders: Optional[bool] = False,
            **kwargs: Any
    ) -> CustomLabeledModel:
        """Create and train a custom model with labels. The request must include a source parameter that is an
        externally accessible Azure storage blob container Uri (preferably a Shared Access Signature Uri).
        Models are trained using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content in the container is ignored.

        :param str source: An Azure Storage blob container URI.
        :param str source_prefix_filter: A case-sensitive prefix string to filter documents in the source path for
            training. For example, when using a Azure storage blob Uri, use the prefix to restrict sub
            folders for training.
        :param bool include_sub_folders: A flag to indicate if sub folders within the set of prefix folders
            will also need to be included when searching for content to be preprocessed.
        :return: CustomLabeledModel
        :rtype: ~azure.ai.formrecognizer.CustomLabeledModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        cls = kwargs.pop("cls", None)
        response = await self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                ),
                use_label_file=True
            ),
            cls=lambda pipeline_response, _, response_headers: pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomLabeledModel._from_generated(model)

        deserialization_callback = cls if cls else callback
        return await async_poller(
            self._client._client,
            response,
            deserialization_callback,
            AsyncLROBasePolling(timeout=POLLING_INTERVAL, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace_async
    async def delete_custom_model(self, model_id: str, **kwargs: Any) -> None:
        """Mark model for deletion. Model artifacts will be permanently removed within a predetermined period.

        Delete Custom Model.

        :param model_id: Model identifier.
        :type model_id: str
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._client.delete_custom_model(
            model_id=model_id,
            **kwargs
        )

    @distributed_trace
    def list_custom_models(self, **kwargs: Any) -> Iterable[ModelInfo]:
        """List Custom Models.

        :return: AsyncItemPaged[~azure.ai.formrecognizer.ModelInfo]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.list_custom_models(
            cls=kwargs.pop("cls", lambda objs: [ModelInfo._from_generated(x) for x in objs]),
            **kwargs
        )

    @distributed_trace_async
    async def get_models_summary(self, **kwargs: Any) -> ModelsSummary:
        """Get information about all custom models.

        :return: Summary of models on account - count, limit, last updated.
        :rtype: ~azure.ai.formrecognizer.ModelsSummary
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = await self._client.get_custom_models(**kwargs)
        return ModelsSummary._from_generated(response.summary)

    @distributed_trace_async
    async def get_custom_model(self, model_id: str, **kwargs: Any) -> CustomModel:
        """Get detailed information about a custom model.

        :param str model_id: Model identifier.
        :return: CustomModel
        :rtype: ~azure.ai.formrecognizer.CustomModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = await self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        if response.keys:
            return CustomModel._from_generated(response)
        raise ValueError("Model id '{}' is a model that was trained with labels. Call get_custom_labeled_model() "
                         "with the model id.".format(model_id))

    @distributed_trace_async
    async def get_custom_labeled_model(self, model_id: str, **kwargs: Any) -> CustomLabeledModel:
        """Get detailed information about a custom labeled model.

        :param str model_id: Model identifier.
        :return: CustomLabeledModel
        :rtype: ~azure.ai.formrecognizer.CustomLabeledModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = await self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        if response.keys is None:
            return CustomLabeledModel._from_generated(response)
        raise ValueError("Model id '{}' was not trained with labels. Call get_custom_model() with the model id."
                         .format(model_id))

    async def __aenter__(self) -> "FormTrainingClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.FormTrainingClient` session.
        """
        await self._client.__aexit__()
