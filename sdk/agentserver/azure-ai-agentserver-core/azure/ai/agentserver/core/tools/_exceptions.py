# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core.tools._models import ResolvedFoundryTool


class ToolInvocationError(RuntimeError):
    """Raised when a tool invocation fails.

    :ivar ResolvedFoundryTool tool: The tool that failed during invocation.

    :param str message: Human-readable message describing the error.
    :param ResolvedFoundryTool tool: The tool that failed during invocation.

    This exception is raised when an error occurs during the invocation of a tool,
    providing details about the failure.
    """

    def __init__(self, message: str, tool: ResolvedFoundryTool):
        super().__init__(message)
        self.tool = tool


class OAuthConsentRequiredError(RuntimeError):
    """Raised when the service requires end-user OAuth consent.

    This exception is raised when a tool or service operation requires explicit
    OAuth consent from the end user before the operation can proceed.

    :ivar str message: Human-readable guidance returned by the service.
    :ivar str consent_url: Link that the end user must visit to provide consent.
    :ivar str project_connection_id: The project connection ID related to the consent request.

    :param str message: Human-readable guidance returned by the service.
    :param str consent_url: Link that the end user must visit to provide the required consent.
    :param str project_connection_id: The project connection ID related to the consent request.
    """

    def __init__(self, message: str, consent_url: str, project_connection_id: str):
        super().__init__(message)
        self.message = message
        self.consent_url = consent_url
        self.project_connection_id = project_connection_id
