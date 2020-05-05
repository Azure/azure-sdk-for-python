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
    TYPE_CHECKING,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter, CopyRequest, Model, CopyOperationResult
from ._helpers import error_map, POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from ._models import (
    CustomFormModelInfo,
    AccountProperties,
    CustomFormModel,
)
from ._polling import TrainingPolling
from ._user_agent import USER_AGENT
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.pipeline.transport import HttpResponse
    from ._generated.models import CopyAuthorizationResult
    PipelineResponseType = HttpResponse


class FormTrainingClient(object):
    """FormTrainingClient is the Form Recognizer interface to use for creating,
    and managing custom models. It provides methods for training models on forms
    you provide and methods for viewing and deleting models, as well as
    accessing account properties.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key.
    :type credential: ~azure.core.credentials.AzureKeyCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_train_model_with_labels.py
            :start-after: [START create_form_training_client]
            :end-before: [END create_form_training_client]
            :language: python
            :dedent: 8
            :caption: Creating the FormTrainingClient with an endpoint and API key.
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

    @distributed_trace
    def _generate_model_copy_authorization(self, **kwargs):
        # type: (Any) -> CopyAuthorizationResult
        """Generate authorization to copy a model into the target Form Recognizer resource.

        :return: CopyAuthorizationResult
        :rtype: ~azure.ai.formrecognizer.CopyAuthorizationResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        return self._client.generate_model_copy_authorization(  # type: ignore
            cls=lambda pipeline_response, deserialized, response_headers: deserialized,
            error_map=error_map,
            **kwargs
        )

    @distributed_trace
    def begin_copy_model(
        self,
        source_model_id,  # type: str
        target_resource_id,  # type: str
        target_resource_region,  # type: str
        target_endpoint,  # type: str
        target_credential,  # type: AzureKeyCredential
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller
        """Copy custom model stored in this resource (the source) to user specified target Form Recognizer resource.

        Copy Custom Model.

        :param source_model_id: Model identifier.
        :type source_model_id: str
        :param str target_resource_id: Azure Resource Id of the target Form Recognizer resource
            where the model is copied to.
        :param str target_resource_region: Location of the target Azure resource. A valid Azure
            region name supported by Cognitive Services.
        :param str target_endpoint: The target endpoint to transfer the copied model.
        :param ~azure.core.credentials.AzureKeyCredential target_credential:
            The credential for the target resource.
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if
            no Retry-After header is present.
        :return: An instance of LROPoller
        :rtype: ~azure.core.polling.LROPoller[CustomFormModelInfo]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        target_client = self._get_form_training_client(target_endpoint, target_credential)
        copy_authorization = target_client._generate_model_copy_authorization()

        def _copy_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            copy_result = self._client._deserialize(CopyOperationResult, raw_response)
            return CustomFormModelInfo._from_generated_copy(copy_result, copy_authorization.model_id)

        return self._client.begin_copy_custom_model(  # type: ignore
            model_id=source_model_id,
            copy_request=CopyRequest(
                target_resource_id=target_resource_id,
                target_resource_region=target_resource_region,
                copy_authorization=copy_authorization
            ),
            cls=kwargs.pop("cls", _copy_callback),
            polling=LROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            **kwargs
        )

    @classmethod
    def _get_form_training_client(cls, endpoint, credential):
        return cls(endpoint, credential)

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
