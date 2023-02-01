# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any

from .client_assertion import ClientAssertionCredential


class TokenFileMixin:
    def __init__(
            self,
            file: str,
            **_: Any
    ) -> None:
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0
        self._file = file

    def get_service_account_token(self) -> str:
        now = int(time.time())
        if now - self._last_read_time > 600:
            with open(self._file) as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class WorkloadIdentityCredential(ClientAssertionCredential, TokenFileMixin):
    """WorkloadIdentityCredential supports Azure workload identity on Kubernetes.
    See the `workload identity overview <https://learn.microsoft.com/azure/aks/workload-identity-overview>`_
    for more information.

    :param str tenant_id: ID of the application's Azure Active Directory tenant. Also called its "directory" ID.
    :param str client_id: The client ID of an Azure AD app registration.
    :param str file: The path to a file containing a Kubernetes service account token that authenticates the identity.
    """

    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            file: str,
            **kwargs: Any
    ) -> None:
        super(WorkloadIdentityCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self.get_service_account_token,
            file=file,
            **kwargs
        )
