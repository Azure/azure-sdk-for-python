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
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._generated.models import Model
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter
from ._helpers import POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from ._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
)
from ._polling import TrainingPolling
from ._user_agent import USER_AGENT
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
        """Close the :class:`~azure.ai.formrecognizer.FormTrainingClient` session.
        """
        return self._client.close()

    def __enter__(self):
        # type: () -> FormTrainingClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
