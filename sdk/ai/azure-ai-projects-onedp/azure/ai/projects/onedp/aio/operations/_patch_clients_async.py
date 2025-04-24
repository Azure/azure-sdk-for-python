# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from azure.core.tracing.decorator import distributed_trace


class ClientsOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.onedp.aio.AIProjectClient`'s
        :attr:`clients` attribute.
    """

    # TODO: Merge all code related to handling user-agent, into a single place.
    def __init__(self, outer_instance: "azure.ai.projects.onedp.aio.AIProjectClient") -> None:  # type: ignore[name-defined]

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
    def get_agents_client(self, **kwargs) -> "AgentsClient":  # type: ignore[name-defined]
        """Get an authenticated asynchronous AgentsClient (from the package azure-ai-agents) to use with
        your AI Foundry Project. Keyword arguments are passed to the constructor of
        AgentsClient.

        .. note:: The package `azure-ai-agents` must be installed prior to calling this method.

        :return: An authenticated Agents Client.
        :rtype: ~azure.ai.agents.AgentsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-agents` package
         is not installed.
        """

        try:
            from azure.ai.agents.aio import AgentsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Agents SDK is not installed. Please install it using 'pip install azure-ai-agents'"
            ) from e

        client = AgentsClient(
            endpoint=self._outer_instance._config.endpoint,  # pylint: disable=protected-access
            credential=self._outer_instance._config.credential,  # pylint: disable=protected-access
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client
