# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from azure.core.tracing.decorator import distributed_trace


class AssistantsOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.onedp.aio.AIProjectClient`'s
        :attr:`assistants` attribute.
    """

    # TODO: Merge all code related to handling user-agent, into a single place.
    def __init__(self, outer_instance: "azure.ai.projects.onedp.aio.AIProjectClient") -> None:

        # All returned inference clients will have this application id set on their user-agent.
        # For more info on user-agent HTTP header, see:
        # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
        USER_AGENT_APP_ID = "AIProjectClient"

        if hasattr(outer_instance, "_user_agent") and outer_instance._user_agent:
            # If the calling application has set "user_agent" when constructing the AIProjectClient,
            # take that value and prepend it to USER_AGENT_APP_ID.
            self._user_agent = f"{outer_instance._user_agent}-{USER_AGENT_APP_ID}"
        else:
            self._user_agent = USER_AGENT_APP_ID

        self._outer_instance = outer_instance

    @distributed_trace
    def get_client(self, **kwargs) -> "AssistantClient":
        """Get an authenticated asynchronous AssistantClient (from the package azure-ai-assistants) to use with
        your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        .. note:: The package `azure-ai-assistants` must be installed prior to calling this method.

        :return: An authenticated Assistant Client.
        :rtype: ~azure.ai.assistants.AssistantClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-assistants` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.assistants.aio import AssistantClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Assistant SDK is not installed. Please install it using 'pip install azure-ai-assistants'"
            ) from e

        client = AssistantClient(
            endpoint=self._outer_instance._config.endpoint,
            credential=self._outer_instance._config.cedential,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client
