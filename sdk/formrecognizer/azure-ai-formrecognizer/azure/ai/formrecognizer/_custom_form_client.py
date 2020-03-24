# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    Dict,
    IO,
    Iterable,
    TYPE_CHECKING,
)

from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.exceptions import HttpResponseError
from ._generated.models import AnalyzeOperationResult, Model
from azure.core.polling.base_polling import LROBasePolling

from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter
from ._base_client import FormRecognizerClientBase
from ._response_handlers import (
    prepare_unlabeled_result,
    prepare_labeled_result,
)
from ._helpers import get_pipeline_response, get_content_type, POLLING_INTERVAL
from ._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
)
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._credential import FormRecognizerApiKeyCredential


class CustomFormClient(FormRecognizerClientBase):
    """CustomFormClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of FormRecognizerApiKeyCredential if using an API key
        or a token credential from azure.identity.
    :type credential: ~azure.ai.formrecognizer.FormRecognizerApiKeyCredential
        or ~azure.core.credentials.TokenCredential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[FormRecognizerApiKeyCredential, TokenCredential], Any) -> None
        super(CustomFormClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credential=credential, pipeline=self._pipeline
        )

    @distributed_trace
    def begin_training(self, source, source_prefix_filter="", include_sub_folders=False, **kwargs):
        # type: (str, str, bool, Any) -> LROPoller
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
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        content_type = kwargs.pop("content_type", "application/json")

        response = self._client.train_custom_model_async(
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

        # FIXME: https://github.com/Azure/azure-sdk-for-python/issues/10417
        response.http_response.headers["Location"] = response.http_response.headers["Location"] + "?includeKeys=true"
        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=POLLING_INTERVAL, **kwargs))

    @distributed_trace
    def begin_labeled_training(self, source, source_prefix_filter="", include_sub_folders=False, **kwargs):
        # type: (str, str, bool, Any) -> LROPoller
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
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        content_type = kwargs.pop("content_type", "application/json")

        response = self._client.train_custom_model_async(
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

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=POLLING_INTERVAL, **kwargs))

    @distributed_trace
    def begin_extract_form_pages(self, form, model_id, **kwargs):
        # type: (Union[str, IO[bytes]], str, Any) -> LROPoller
        """Analyze Form.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or file stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if extracted_form.analyze_result.document_results:
                raise HttpResponseError("Cannot call begin_extract_forms() with the ID of a model trained with "
                                        "labels. Please call begin_extract_labeled_forms() instead.")
            form_result = prepare_unlabeled_result(extracted_form, include_text_details)
            return form_result

        return self._client.begin_analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=callback,
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_labeled_forms(self, form, model_id, **kwargs):
        # type: (Union[str, IO[bytes]], str, Any) -> LROPoller
        """Analyze Form.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or file stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if not extracted_form.analyze_result.document_results:
                raise HttpResponseError("Cannot call begin_extract_labeled_forms() with the ID of a model trained "
                                        "without labels. Please call begin_extract_forms() instead.")
            form_result = prepare_labeled_result(extracted_form, include_text_details)
            return form_result

        return self._client.begin_analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=callback,
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def delete_custom_model(self, model_id, **kwargs):
        # type: (str, Any) -> None
        """Mark model for deletion. Model artifacts will be permanently removed within a predetermined period.

        Delete Custom Model.

        :param model_id: Model identifier.
        :type model_id: str
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        self._client.delete_custom_model(
            model_id=model_id,
            **kwargs
        )

    @distributed_trace
    def list_custom_models(self, **kwargs):
        # type: (Any) -> Iterable[ModelInfo]
        """List Custom Models.

        :return: ItemPaged[~azure.ai.formrecognizer.ModelInfo]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.list_custom_models(
            cls=lambda objs: [ModelInfo._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def get_models_summary(self, **kwargs):
        # type: (Any) -> ModelsSummary
        """Get information about all custom models.

        :return: Summary of models on account - count, limit, last updated.
        :rtype: ~azure.ai.formrecognizer.ModelsSummary
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = self._client.get_custom_models(**kwargs)
        return ModelsSummary._from_generated(response.summary)

    @distributed_trace
    def get_custom_model(self, model_id, **kwargs):
        # type: (str, Any) -> CustomModel
        """Get detailed information about a custom model.

        :param str model_id: Model identifier.
        :return: CustomModel
        :rtype: ~azure.ai.formrecognizer.CustomModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        if response.keys:
            return CustomModel._from_generated(response)
        raise HttpResponseError(message="Model id '{}' is a model that was trained with labels. "
                                        "Call get_custom_labeled_model() with the model id.".format(model_id))

    @distributed_trace
    def get_custom_labeled_model(self, model_id, **kwargs):
        # type: (str, Any) -> CustomLabeledModel
        """Get detailed information about a custom labeled model.

        :param str model_id: Model identifier.
        :return: CustomLabeledModel
        :rtype: ~azure.ai.formrecognizer.CustomLabeledModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = self._client.get_custom_model(model_id=model_id, **kwargs)
        if response.keys is None:
            return CustomLabeledModel._from_generated(response)
        raise HttpResponseError(message="Model id '{}' was not trained with labels. Call get_custom_model() "
                                        "with the model id.".format(model_id))
