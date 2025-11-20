# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Mapping, Optional


class OAuthConsentRequiredError(RuntimeError):
    """Raised when the service requires end-user OAuth consent.

    This exception is raised when a tool or service operation requires explicit
    OAuth consent from the end user before the operation can proceed.

    :ivar str message: Human-readable guidance returned by the service.
    :ivar str consent_url: Link that the end user must visit to provide consent.
    :ivar dict payload: Full response payload from the service.

    :param str message: Human-readable guidance returned by the service.
    :param str consent_url: Link that the end user must visit to provide the required consent.
    :param dict payload: Full response payload supplied by the service.
    """

    def __init__(self, message: str, consent_url: Optional[str], payload: Mapping[str, Any]):
        super().__init__(message)
        self.message = message
        self.consent_url = consent_url
        self.payload = dict(payload)


class MCPToolApprovalRequiredError(RuntimeError):
    """Raised when an MCP tool invocation needs human approval.

    This exception is raised when an MCP (Model Context Protocol) tool requires
    explicit human approval before the invocation can proceed, typically for
    security or compliance reasons.

    :ivar str message: Human-readable guidance returned by the service.
    :ivar dict approval_arguments:
        Arguments that must be approved or amended before continuing.
    :ivar dict payload: Full response payload from the service.

    :param str message: Human-readable guidance returned by the service.
    :param dict approval_arguments:
        Arguments that must be approved or amended before continuing.
    :param dict payload: Full response payload supplied by the service.
    """

    def __init__(self, message: str, approval_arguments: Mapping[str, Any], payload: Mapping[str, Any]):
        super().__init__(message)
        self.message = message
        self.approval_arguments = dict(approval_arguments)
        self.payload = dict(payload)
