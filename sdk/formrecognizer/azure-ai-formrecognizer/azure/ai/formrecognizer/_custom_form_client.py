# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (  # pylint: disable=unused-import
    Optional,
    Any,
    IO,
    Iterable,
    TYPE_CHECKING,
)
import six
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._generated.models import AnalyzeOperationResult, Model
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter
from ._response_handlers import (
    prepare_unlabeled_result,
    prepare_labeled_result,
)
from ._helpers import get_content_type, POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from ._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
)
from ._training_polling import TrainingPolling
from ._user_agent import USER_AGENT
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential


class CustomFormClient(object):
    """CustomFormClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, Any) -> None
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=AzureKeyCredentialPolicy(credential, COGNITIVE_KEY_HEADER),
            **kwargs
        )

    @distributed_trace
    def begin_training(self, source, source_prefix_filter="", include_sub_folders=False, **kwargs):
        # type: (str, Optional[str], Optional[bool], Any) -> LROPoller
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
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.formrecognizer.CustomModel]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        cls = kwargs.pop("cls", None)
        response = self._client.train_custom_model_async(
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
        return LROPoller(
            self._client._client,
            response,
            deserialization_callback,
            LROBasePolling(timeout=POLLING_INTERVAL, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace
    def begin_labeled_training(self, source, source_prefix_filter="", include_sub_folders=False, **kwargs):
        # type: (str, Optional[str], Optional[bool], Any) -> LROPoller
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
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.formrecognizer.CustomLabeledModel]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        cls = kwargs.pop("cls", None)
        response = self._client.train_custom_model_async(
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
        return LROPoller(
            self._client._client,
            response,
            deserialization_callback,
            LROBasePolling(timeout=POLLING_INTERVAL, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace
    def begin_extract_form_pages(self, stream, model_id, **kwargs):
        # type: (IO[bytes], str, Any) -> LROPoller
        """Analyze Form.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedPage]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if isinstance(stream, six.string_types):
            raise TypeError("Call begin_extract_form_pages_from_url() to analyze a document from a url.")

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)
        if content_type is None:
            content_type = get_content_type(stream)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if extracted_form.analyze_result.document_results:
                raise ValueError("Cannot call begin_extract_form_pages() with the ID of a model trained with labels. "
                                 "Please call begin_extract_labeled_forms() instead.")
            return prepare_unlabeled_result(extracted_form)

        return self._client.begin_analyze_with_custom_model(
            file_stream=stream,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=kwargs.pop("cls", callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_form_pages_from_url(self, url, model_id, **kwargs):
        # type: (str, str, Any) -> LROPoller
        """Analyze Form.

        :param url: The url of the document.
        :type url: str
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedPage]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not isinstance(url, six.string_types):
            raise TypeError("Call begin_extract_form_pages() to analyze a document from a stream.")

        include_text_details = kwargs.pop("include_text_details", False)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if extracted_form.analyze_result.document_results:
                raise ValueError("Cannot call begin_extract_form_pages_from_url() with the ID of a model trained "
                                 "with labels. Please call begin_extract_labeled_forms_from_url() instead.")
            return prepare_unlabeled_result(extracted_form)

        return self._client.begin_analyze_with_custom_model(
            file_stream={"source": url},
            model_id=model_id,
            include_text_details=include_text_details,
            cls=kwargs.pop("cls", callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_labeled_forms(self, stream, model_id, **kwargs):
        # type: (IO[bytes], str, Any) -> LROPoller
        """Analyze Form.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedLabeledForm]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if isinstance(stream, six.string_types):
            raise TypeError("Call begin_extract_labeled_forms_from_url() to analyze a document from a url.")

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)
        if content_type is None:
            content_type = get_content_type(stream)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if not extracted_form.analyze_result.document_results:
                raise ValueError("Cannot call begin_extract_labeled_forms() with the ID of a model trained "
                                 "without labels. Please call begin_extract_form_pages() instead.")
            return prepare_labeled_result(extracted_form)

        return self._client.begin_analyze_with_custom_model(
            file_stream=stream,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=kwargs.pop("cls", callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_labeled_forms_from_url(self, url, model_id, **kwargs):
        # type: (str, str, Any) -> LROPoller
        """Analyze Form.

        :param url: The url of the document.
        :type url: str
        :param str model_id: Model identifier.
        :keyword bool include_text_details: Include text lines and element references in the result.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedLabeledForm]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not isinstance(url, six.string_types):
            raise TypeError("Call begin_extract_labeled_forms() to analyze a document from a stream.")

        include_text_details = kwargs.pop("include_text_details", False)

        def callback(raw_response, _, headers):  # pylint: disable=unused-argument
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            if not extracted_form.analyze_result.document_results:
                raise ValueError("Cannot call begin_extract_labeled_forms_from_url() with the ID of a model trained "
                                 "without labels. Please call begin_extract_form_pages_from_url() instead.")
            return prepare_labeled_result(extracted_form)

        return self._client.begin_analyze_with_custom_model(
            file_stream={"source": url},
            model_id=model_id,
            include_text_details=include_text_details,
            cls=kwargs.pop("cls", callback),
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
            cls=kwargs.pop("cls", lambda objs: [ModelInfo._from_generated(x) for x in objs]),
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
        raise ValueError("Model id '{}' is a model that was trained with labels. Call get_custom_labeled_model() "
                         "with the model id.".format(model_id))

    @distributed_trace
    def get_custom_labeled_model(self, model_id, **kwargs):
        # type: (str, Any) -> CustomLabeledModel
        """Get detailed information about a custom labeled model.

        :param str model_id: Model identifier.
        :return: CustomLabeledModel
        :rtype: ~azure.ai.formrecognizer.CustomLabeledModel
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        if response.keys is None:
            return CustomLabeledModel._from_generated(response)
        raise ValueError("Model id '{}' was not trained with labels. Call get_custom_model() with the model id."
                         .format(model_id))

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.formrecognizer.CustomFormClient` session.
        """
        return self._client.close()

    def __enter__(self):
        # type: () -> CustomFormClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
