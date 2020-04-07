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
    CustomFormModelInfo,
    AccountProperties,
    CustomFormModel
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
            training_files: str,
            use_labels: Optional[bool] = False,
            files_prefix: Optional[str] = "",
            include_sub_folders: Optional[bool] = False,
            **kwargs: Any
    ) -> CustomFormModel:
        """Create and train a custom model. The request must include a source parameter that is an
        externally accessible Azure storage blob container Uri (preferably a Shared Access Signature Uri).
        Models are trained using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content in the container is ignored.

        :param str training_files: An Azure Storage blob container URI.
        :param bool use_labels: Whether to train with labels or not. Corresponding labeled files must
            exist in the blob container.
        :param str files_prefix: A case-sensitive prefix string to filter documents in the source path for
            training. For example, when using a Azure storage blob Uri, use the prefix to restrict sub
            folders for training.
        :param bool include_sub_folders: A flag to indicate if sub folders within the set of prefix folders
            will also need to be included when searching for content to be preprocessed.
        :return: CustomFormModel
        :rtype: ~azure.ai.formrecognizer.CustomFormModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        cls = kwargs.pop("cls", None)
        response = await self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=training_files,
                use_label_file=use_labels,
                source_filter=TrainSourceFilter(
                    prefix=files_prefix,
                    include_sub_folders=include_sub_folders
                )
            ),
            cls=lambda pipeline_response, _, response_headers: pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomFormModel._from_generated(model)

        deserialization_callback = cls if cls else callback
        return await async_poller(
            self._client._client,
            response,
            deserialization_callback,
            AsyncLROBasePolling(timeout=POLLING_INTERVAL, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace_async
    async def delete_model(self, model_id: str, **kwargs: Any) -> None:
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
    def list_model_infos(self, **kwargs: Any) -> Iterable[CustomFormModelInfo]:
        """List information for each model, including model id,
        status, and when it was created and last updated.

        :return: AsyncItemPaged[~azure.ai.formrecognizer.CustomFormModelInfo]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.list_custom_models(
            cls=kwargs.pop("cls", lambda objs: [CustomFormModelInfo._from_generated(x) for x in objs]),
            **kwargs
        )

    @distributed_trace_async
    async def get_account_properties(self, **kwargs: Any) -> AccountProperties:
        """Get information about the models on the form recognizer account.

        :return: Summary of models on account - count, limit.
        :rtype: ~azure.ai.formrecognizer.AccountProperties
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = await self._client.get_custom_models(**kwargs)
        return AccountProperties._from_generated(response.summary)

    @distributed_trace_async
    async def get_custom_model(self, model_id: str, **kwargs: Any) -> CustomFormModel:
        """Get detailed information about a custom model.

        :param str model_id: Model identifier.
        :return: CustomFormModel
        :rtype: ~azure.ai.formrecognizer.CustomFormModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = await self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        return CustomFormModel._from_generated(response)

    async def __aenter__(self) -> "FormTrainingClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.FormTrainingClient` session.
        """
        await self._client.__aexit__()
