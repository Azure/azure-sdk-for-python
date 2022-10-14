# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, BearerTokenCredentialPolicy

from ._client import PersonalizerClient as PersonalizerClientGenerated

__all__: List[str] = [
    "PersonalizerClient",
    "PersonalizerAdministrationClient",
]  # Add all objects you want publicly available to users at this package level

from .operations._operations import JSON


def _authentication_policy(credential, **kwargs):
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential, **kwargs
        )
    elif hasattr(credential, "get_token"):
        authentication_policy = BearerTokenCredentialPolicy(
            credential, *kwargs.pop("credential_scopes", ["https://cognitiveservices.azure.com/.default"]), **kwargs
        )
    else:
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


class PersonalizerAdministrationClient:
    """This client contains the operations that apply to Azure Personalizer. Operations allowed by the client are
    viewing and editing the properties, policy, model, running evaluations.

    :ivar service_configuration: ServiceConfigurationOperations operations
    :vartype service_configuration: azure.ai.personalizer.operations.ServiceConfigurationOperations
    :ivar policy: PolicyOperations operations
    :vartype policy: azure.ai.personalizer.operations.PolicyOperations
    :ivar evaluations: EvaluationsOperations operations
    :vartype evaluations: azure.ai.personalizer.operations.EvaluationsOperations
    :ivar feature_importances: FeatureImportancesOperations operations
    :vartype feature_importances: azure.ai.personalizer.operations.FeatureImportancesOperations
    :ivar log: LogOperations operations
    :vartype log: azure.ai.personalizer.operations.LogOperations
    :ivar model: ModelOperations operations
    :vartype model: azure.ai.personalizer.operations.ModelOperations
    :param endpoint: Supported Cognitive Services endpoint. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. Default value is "2022-09-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        self._client = PersonalizerClientGenerated(
            endpoint=endpoint.rstrip("/"),
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential, **kwargs)),
            **kwargs
        )
        self.model = self._client.model
        self.service_configuration = self._client.service_configuration
        self.policy = self._client.policy
        self.evaluations = self._client.evaluations
        self.feature_importances = self._client.feature_importances
        self.log = self._client.log
        self.model = self._client.model


class PersonalizerClient:
    """Personalizer Service is an Azure Cognitive Service that makes it easy to target content and
    experiences without complex pre-analysis or cleanup of past data. Given a context and
    featurized content, the Personalizer Service returns which content item to show to users in
    rewardActionId. As rewards are sent in response to the use of rewardActionId, the reinforcement
    learning algorithm will improve the model and improve performance of future rank calls.

    :ivar multi_slot: MultiSlotOperations operations
    :vartype multi_slot: azure.ai.personalizer.operations.MultiSlotOperations
    :ivar events: EventsOperations operations
    :vartype events: azure.ai.personalizer.operations.EventsOperations
    :ivar multi_slot_events: MultiSlotEventsOperations operations
    :vartype multi_slot_events: azure.ai.personalizer.operations.MultiSlotEventsOperations
    :param endpoint: Supported Cognitive Services endpoint. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. Default value is "2022-09-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        self._client = PersonalizerClientGenerated(
            endpoint=endpoint.rstrip("/"),
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential, **kwargs)),
            **kwargs
        )
        self.multi_slot = self._client.multi_slot
        self.events = self._client.events
        self.multi_slot_events = self._client.multi_slot_events

    def rank(self, request: JSON) -> JSON:
        """Submit a Personalizer rank request. Receives a context and a list of actions.
        Returns which of the provided actions should be used by your application, in rewardActionId.

        :param request: Request containing context and list of actions
        :type request: JSON
        """
        return self._client.rank(request)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
