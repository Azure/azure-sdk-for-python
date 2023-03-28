# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from typing import Any
from typing import Optional

from .client_assertion import ClientAssertionCredential
from .._constants import EnvironmentVariables


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

    :keyword str tenant_id: ID of the application's Azure Active Directory tenant. Also called its "directory" ID.
    :keyword str client_id: The client ID of an Azure AD app registration.
    :keyword str file: The path to a file containing a Kubernetes service account token that authenticates the identity.
    """

    def __init__(
            self,
            *,
            tenant_id: Optional[str] = None,
            client_id: Optional[str] = None,
            file: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        tenant_id = tenant_id or os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        client_id = client_id or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
        file = file or os.environ.get(EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE)
        if not tenant_id:
            raise ValueError(
            "'tenant_id' is required. Please pass it in or set the "
            f"{EnvironmentVariables.AZURE_TENANT_ID} environment variable"
        )
        if not client_id:
            "'client_id' is required. Please pass it in or set the "
            f"{EnvironmentVariables.AZURE_CLIENT_ID} environment variable"
        if not file:
            "'file' is required. Please pass it in or set the "
            f"{EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE} environment variable"
        super(WorkloadIdentityCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self.get_service_account_token,
            file=file,
            **kwargs
        )
