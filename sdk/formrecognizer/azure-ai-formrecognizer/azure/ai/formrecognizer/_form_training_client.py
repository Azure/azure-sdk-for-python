# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (
    Optional,
    Any,
    Iterable,
    Union,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from ._generated.models import Model
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter
from ._helpers import error_map, get_authentication_policy, POLLING_INTERVAL
from ._models import (
    CustomFormModelInfo,
    AccountProperties,
    CustomFormModel
)
from ._polling import TrainingPolling
from ._user_agent import USER_AGENT
from ._form_recognizer_client import FormRecognizerClient
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential, TokenCredential
    from azure.core.pipeline.transport import HttpResponse
    PipelineResponseType = HttpResponse


class FormTrainingClient(object):
    """FormTrainingClient is the Form Recognizer interface to use for creating,
    and managing custom models. It provides methods for training models on forms
    you provide and methods for viewing and deleting models, as well as
    accessing account properties.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ft_client_with_key]
            :end-before: [END create_ft_client_with_key]
            :language: python
            :dedent: 8
            :caption: Creating the FormTrainingClient with an endpoint and API key.

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ft_client_with_aad]
            :end-before: [END create_ft_client_with_aad]
            :language: python
            :dedent: 8
            :caption: Creating the FormTrainingClient with a token credential.
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
        self._endpoint = endpoint
        self._credential = credential
        authentication_policy = get_authentication_policy(credential)
        self._client = FormRecognizer(
            endpoint=self._endpoint,
            credential=self._credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            **kwargs
        )

    @distributed_trace
    def begin_train_model(self, training_files_url, use_training_labels=False, **kwargs):
        # type: (str, Optional[bool], Any) -> LROPoller
        """Create and train a custom model. The request must include a `training_files_url` parameter that is an
        externally accessible Azure storage blob container Uri (preferably a Shared Access Signature Uri).
        Models are trained using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff'. Other type of content in the container is ignored.

        :param str training_files_url: An Azure Storage blob container's SAS URI.
        :param bool use_training_labels: Whether to train with labels or not. Corresponding labeled files must
            exist in the blob container.
        :keyword str prefix: A case-sensitive prefix string to filter documents for training.
            Use `prefix` to filter documents themselves, or to restrict sub folders for training
            when `include_sub_folders` is set to True. Not supported if training with labels.
        :keyword bool include_sub_folders: A flag to indicate if sub folders
            will also need to be included when searching for content to be preprocessed.
            Use with `prefix` to filter for only certain sub folders. Not supported if training with labels.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.CustomFormModel`.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.formrecognizer.CustomFormModel]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_train_model_without_labels.py
                :start-after: [START training]
                :end-before: [END training]
                :language: python
                :dedent: 8
                :caption: Training a model with your custom forms.
        """

        cls = kwargs.pop("cls", None)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        response = self._client.train_custom_model_async(  # type: ignore
            train_request=TrainRequest(
                source=training_files_url,
                use_label_file=use_training_labels,
                source_filter=TrainSourceFilter(
                    prefix=kwargs.pop("prefix", ""),
                    include_sub_folders=kwargs.pop("include_sub_folders", False),
                )
            ),
            cls=lambda pipeline_response, _, response_headers: pipeline_response,
            error_map=error_map,
            **kwargs
        )  # type: PipelineResponseType

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomFormModel._from_generated(model)

        deserialization_callback = cls if cls else callback
        return LROPoller(
            self._client._client,
            response,
            deserialization_callback,
            LROBasePolling(timeout=polling_interval, lro_algorithms=[TrainingPolling()], **kwargs)
        )

    @distributed_trace
    def delete_model(self, model_id, **kwargs):
        # type: (str, Any) -> None
        """Mark model for deletion. Model artifacts will be permanently
        removed within a predetermined period.

        :param model_id: Model identifier.
        :type model_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_manage_custom_models.py
                :start-after: [START delete_model]
                :end-before: [END delete_model]
                :language: python
                :dedent: 8
                :caption: Delete a custom model.
        """

        self._client.delete_custom_model(
            model_id=model_id,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace
    def list_custom_models(self, **kwargs):
        # type: (Any) -> Iterable[CustomFormModelInfo]
        """List information for each model, including model id,
        model status, and when it was created and last modified.

        :return: ItemPaged[:class:`~azure.ai.formrecognizer.CustomFormModelInfo`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_manage_custom_models.py
                :start-after: [START list_custom_models]
                :end-before: [END list_custom_models]
                :language: python
                :dedent: 8
                :caption: List model information for each model on the account.
        """
        return self._client.list_custom_models(
            cls=kwargs.pop("cls", lambda objs: [CustomFormModelInfo._from_generated(x) for x in objs]),
            error_map=error_map,
            **kwargs
        )

    @distributed_trace
    def get_account_properties(self, **kwargs):
        # type: (Any) -> AccountProperties
        """Get information about the models on the form recognizer account.

        :return: Summary of models on account - custom model count,
            custom model limit.
        :rtype: ~azure.ai.formrecognizer.AccountProperties
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_manage_custom_models.py
                :start-after: [START get_account_properties]
                :end-before: [END get_account_properties]
                :language: python
                :dedent: 8
                :caption: Get properties for the form recognizer account.
        """
        response = self._client.get_custom_models(error_map=error_map, **kwargs)
        return AccountProperties._from_generated(response.summary)

    @distributed_trace
    def get_custom_model(self, model_id, **kwargs):
        # type: (str, Any) -> CustomFormModel
        """Get a description of a custom model, including the types of forms
        it can recognize, and the fields it will extract for each form type.

        :param str model_id: Model identifier.
        :return: CustomFormModel
        :rtype: ~azure.ai.formrecognizer.CustomFormModel
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_manage_custom_models.py
                :start-after: [START get_custom_model]
                :end-before: [END get_custom_model]
                :language: python
                :dedent: 8
                :caption: Get a custom model with a model ID.
        """
        response = self._client.get_custom_model(model_id=model_id, include_keys=True, error_map=error_map, **kwargs)
        return CustomFormModel._from_generated(response)

    def get_form_recognizer_client(self, **kwargs):
        # type: (Any) -> FormRecognizerClient
        """Get an instance of a FormRecognizerClient from FormTrainingClient.

        :rtype: ~azure.ai.formrecognizer.FormRecognizerClient
        :return: A FormRecognizerClient
        """
        return FormRecognizerClient(
            endpoint=self._endpoint,
            credential=self._credential,
            **kwargs
        )

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
