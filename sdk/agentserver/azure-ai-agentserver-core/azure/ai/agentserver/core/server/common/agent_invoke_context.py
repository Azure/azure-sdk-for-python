# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class AgentInvokeContext:
    """Context object passed to :py:meth:`~azure.ai.agentserver.core.FoundryCBAgent.agent_invoke`.

    Encapsulates the HTTP request headers and parsed JSON payload received by the ``/invoke``
    endpoint so that implementations can access them through a stable, typed interface.

    :param headers: The HTTP request headers forwarded by the ``/invoke`` endpoint,
        as a plain :class:`dict` keyed by header name.
    :type headers: dict
    :param payload: The parsed JSON body of the ``/invoke`` request.
    :type payload: dict
    """

    def __init__(self, headers: dict, payload: dict) -> None:
        self._headers = headers
        self._payload = payload

    @property
    def headers(self) -> dict:
        """The HTTP request headers forwarded by the ``/invoke`` endpoint.

        :return: A plain :class:`dict` containing the request headers.
        :rtype: dict
        """
        return self._headers

    @property
    def payload(self) -> dict:
        """The parsed JSON body received by the ``/invoke`` endpoint.

        :return: A plain :class:`dict` containing the deserialized request body.
        :rtype: dict
        """
        return self._payload
