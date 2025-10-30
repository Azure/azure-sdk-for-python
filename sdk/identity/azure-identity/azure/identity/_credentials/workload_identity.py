# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
import ssl
from typing import Any
from typing import Optional

from .client_assertion import ClientAssertionCredential
from .._constants import EnvironmentVariables
from .._internal.token_binding_transport_mixin import TokenBindingTransportMixin


WORKLOAD_CONFIG_ERROR = (
    "WorkloadIdentityCredential authentication unavailable. The workload options are not fully "
    "configured. See the troubleshooting guide for more information: "
    "https://aka.ms/azsdk/python/identity/workloadidentitycredential/troubleshoot"
)


class TokenFileMixin:

    _token_file_path: str

    def __init__(self, **_: Any) -> None:
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0

    def _get_service_account_token(self) -> str:
        now = int(time.time())
        if now - self._last_read_time > 600:
            with open(self._token_file_path, encoding="utf-8") as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class WorkloadIdentityCredential(ClientAssertionCredential, TokenFileMixin):
    """Authenticates using Microsoft Entra Workload ID.

    Workload identity authentication is a feature in Azure that allows applications running on virtual machines (VMs)
    to access other Azure resources without the need for a service principal or managed identity. With workload
    identity authentication, applications authenticate themselves using their own identity, rather than using a shared
    service principal or managed identity. Under the hood, workload identity authentication uses the concept of Service
    Account Credentials (SACs), which are automatically created by Azure and stored securely in the VM. By using
    workload identity authentication, you can avoid the need to manage and rotate service principals or managed
    identities for each application on each VM. Additionally, because SACs are created automatically and managed by
    Azure, you don't need to worry about storing and securing sensitive credentials themselves.

    The WorkloadIdentityCredential supports Azure workload identity authentication on Azure Kubernetes and acquires
    a token using the service account credentials available in the Azure Kubernetes environment. Refer
    to `this workload identity overview <https://learn.microsoft.com/azure/aks/workload-identity-overview>`__
    for more information.

    :keyword str tenant_id: ID of the application's Microsoft Entra tenant. Also called its "directory" ID.
    :keyword str client_id: The client ID of a Microsoft Entra app registration.
    :keyword str token_file_path: The path to a file containing a Kubernetes service account token that authenticates
        the identity.
    :keyword bool use_token_proxy: Whether or not to read token proxy configuration from environment variables and use
        a token proxy to acquire tokens. Defaults to False.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START workload_identity_credential]
            :end-before: [END workload_identity_credential]
            :language: python
            :dedent: 4
            :caption: Create a WorkloadIdentityCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        token_file_path: Optional[str] = None,
        use_token_proxy: bool = False,
        **kwargs: Any,
    ) -> None:
        tenant_id = tenant_id or os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        client_id = client_id or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
        token_file_path = token_file_path or os.environ.get(EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE)

        missing_args = []
        if not tenant_id:
            missing_args.append("'tenant_id'")
        if not client_id:
            missing_args.append("'client_id'")
        if not token_file_path:
            missing_args.append("'token_file_path'")

        if missing_args:
            missing_args_str = ", ".join(missing_args)
            error_message = f"{WORKLOAD_CONFIG_ERROR}. Missing required arguments: {missing_args_str}."
            raise ValueError(error_message)

        # Type assertions since we've validated these are not None
        assert tenant_id is not None
        assert client_id is not None
        assert token_file_path is not None

        self._token_file_path = token_file_path

        if use_token_proxy:
            token_proxy_endpoint = os.environ.get(EnvironmentVariables.AZURE_KUBERNETES_TOKEN_PROXY)
            if not token_proxy_endpoint:
                raise ValueError(
                    "use_token_proxy is True, but no token proxy endpoint was found. "
                    f"Ensure that the {EnvironmentVariables.AZURE_KUBERNETES_TOKEN_PROXY} environment variable is set."
                )

            sni = os.environ.get(EnvironmentVariables.AZURE_KUBERNETES_SNI_NAME)
            ca_file = os.environ.get(EnvironmentVariables.AZURE_KUBERNETES_CA_FILE)
            ca_data = os.environ.get(EnvironmentVariables.AZURE_KUBERNETES_CA_DATA)

            if ca_file and ca_data:
                raise ValueError(
                    "Both AZURE_KUBERNETES_CA_FILE and AZURE_KUBERNETES_CA_DATA are set. Only one should be set."
                )

            transport = _get_transport(
                sni=sni,
                token_proxy_endpoint=token_proxy_endpoint,
                ca_file=ca_file,
                ca_data=ca_data,
            )

            if transport:
                kwargs["transport"] = transport
            else:
                raise ValueError(
                    "Transport creation failed. Ensure that the requests package is installed to enable token "
                    "proxy usage in this credential."
                )

        super(WorkloadIdentityCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self._get_service_account_token,
            token_file_path=token_file_path,
            **kwargs,
        )


def _get_transport(sni, token_proxy_endpoint, ca_file, ca_data):
    try:
        from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
            RequestsTransport,
        )
        from requests.adapters import HTTPAdapter
        from requests import Session

        class SNIAdapter(HTTPAdapter):
            """A custom HTTPAdapter that allows setting a custom SNI hostname."""

            def __init__(self, server_hostname, ca_data, **kwargs):
                self.server_hostname = server_hostname
                self.ca_data = ca_data
                super().__init__(**kwargs)

            def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
                if self.server_hostname:
                    pool_kwargs["server_hostname"] = self.server_hostname
                pool_kwargs["ssl_context"] = ssl.create_default_context(cadata=self.ca_data)
                super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

        class CustomRequestsTransport(TokenBindingTransportMixin, RequestsTransport):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._create_session()

            def _create_session(self):
                if self.session:  # pylint: disable=access-member-before-definition
                    self.session.close()  # pylint: disable=access-member-before-definition

                self.session = Session()
                adapter = SNIAdapter(self._sni, self._ca_data)
                self.session.mount("https://", adapter)

            def send(self, request, **kwargs):
                self._update_request_url(request)

                # Check if CA file has changed and reload ca_data if needed
                if self._ca_file and self._has_ca_file_changed():
                    self._load_ca_file_to_data()
                    # If ca_data was updated, recreate SSL context with the new data
                    if self._ca_data:
                        self._create_session()
                return super().send(request, **kwargs)

        transport = CustomRequestsTransport(
            sni=sni,
            proxy_endpoint=token_proxy_endpoint,
            ca_file=ca_file,
            ca_data=ca_data,
        )

    except ImportError:
        return None
    return transport
