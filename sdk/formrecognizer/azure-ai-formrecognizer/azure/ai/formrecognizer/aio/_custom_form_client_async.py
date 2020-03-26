# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    IO,
    Iterable,
    TYPE_CHECKING,
)
import six
from azure.core.polling import async_poller
from azure.core.polling.async_base_polling import AsyncLROBasePolling  # pylint: disable=no-name-in-module,import-error
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._generated.aio._form_recognizer_client_async import FormRecognizerClient as FormRecognizer
from .._generated.models import TrainRequest, TrainSourceFilter
from .._policies import CognitiveServicesCredentialPolicy
from .._response_handlers import (
    prepare_unlabeled_result,
    prepare_labeled_result,
)
from .._generated.models import AnalyzeOperationResult, Model
from .._helpers import get_pipeline_response, get_content_type, POLLING_INTERVAL
from .._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
)
if TYPE_CHECKING:
    from .._credential import FormRecognizerApiKeyCredential
    from .._models import (
        ExtractedPage,
        ExtractedLabeledForm
    )


class CustomFormClient(object):
    """CustomFormClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of FormRecognizerApiKeyCredential if using an API key.
    :type credential: ~azure.ai.formrecognizer.FormRecognizerApiKeyCredential
    """

    def __init__(
            self,
            endpoint: str,
            credential: "FormRecognizerApiKeyCredential",
            **kwargs: Any
    ) -> None:
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,
            authentication_policy=CognitiveServicesCredentialPolicy(credential),  # TODO: replace with core policy
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
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content is ignored.

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

        content_type = kwargs.pop("content_type", "application/json")

        response = await self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                )
            ),
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomModel._from_generated(model)

        return await async_poller(
            self._client._client,
            response,
            callback,
            AsyncLROBasePolling(**kwargs)
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
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content is ignored.

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

        content_type = kwargs.pop("content_type", "application/json")

        response = await self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                ),
                use_label_file=True
            ),
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomLabeledModel._from_generated(model)

        return await async_poller(
            self._client._client,
            response,
            callback,
            AsyncLROBasePolling(**kwargs)
        )

    @distributed_trace_async
    async def begin_extract_form_pages(
            self,
            form: Union[str, IO[bytes]],
            model_id: str,
            **kwargs: Any
    ) -> List["ExtractedPage"]:
        """Analyze Form.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: List[ExtractedPage]
        :rtype: list[~azure.ai.formrecognizer.ExtractedPage]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if extracted_form.analyze_result.document_results:
                raise HttpResponseError("Cannot call begin_extract_forms() with the ID of a model trained with "
                                        "labels. Please call begin_extract_labeled_forms() instead.")
            form_result = prepare_unlabeled_result(extracted_form, include_text_details)
            return form_result

        return await self._client.analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=callback,
            polling=AsyncLROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace_async
    async def begin_extract_labeled_forms(
            self,
            form: Union[str, IO[bytes]],
            model_id: str,
            **kwargs: Any
    ) -> List["ExtractedLabeledForm"]:
        """Analyze Form.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: List[ExtractedLabeledForm]
        :rtype: list[~azure.ai.formrecognizer.ExtractedLabeledForm]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if not extracted_form.analyze_result.document_results:
                raise HttpResponseError("Cannot call begin_extract_labeled_forms() with the ID of a model trained "
                                        "without labels. Please call begin_extract_forms() instead.")
            form_result = prepare_labeled_result(extracted_form, include_text_details)
            return form_result

        return await self._client.analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=callback,
            polling=AsyncLROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
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
            cls=lambda objs: [ModelInfo._from_generated(x) for x in objs],
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
        raise HttpResponseError(message="Model id '{}' is a model that was trained with labels. "
                                        "Call get_custom_labeled_model() with the model id.".format(model_id))

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
        raise HttpResponseError(message="Model id '{}' was not trained with labels. Call get_custom_model() "
                                        "with the model id.".format(model_id))
