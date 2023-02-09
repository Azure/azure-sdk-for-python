import os.path

from devtools_testutils import fake_credentials_async

try:
    from inspect import getfullargspec as get_arg_spec
except ImportError:
    from inspect import getargspec as get_arg_spec



def _is_autorest_v3(client_class):
    """Is this client a autorest v3/track2 one?

    Could be refined later if necessary.
    """
    args = get_arg_spec(client_class.__init__).args
    return "credential" in args


def get_credential(self, client_class, **kwargs):
    username = os.environ.get("Username", getattr(self._real_settings, "Username", None))
    password = os.environ.get("Password", getattr(self._real_settings, "Password", None))
    client_id = os.environ.get("AZURE_CLIENT_ID", getattr(self._real_settings, "CLIENT_ID", None))
    tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(self._real_settings, "TENANT_ID", None))
    is_async = kwargs.pop("is_async", False)

    if username and client_id and password and self.is_live:
        if _is_autorest_v3(client_class):
            # Create azure-identity class
            from azure.identity import UsernamePasswordCredential

            if is_async:
                pass
            return UsernamePasswordCredential(client_id, username, password, tenant_id=tenant_id)
        else:
            # Create msrestazure class
            from msrestazure.azure_active_directory import (
                ServicePrincipalCredentials,
            )

            return ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=secret)
    else:
        if _is_autorest_v3(client_class):
            if is_async:
                if self.is_live:
                    raise ValueError(
                        "Async live doesn't support mgmt_setting_real, please set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
                    )
                return fake_credentials_async.AsyncFakeCredential()
            else:
                return self.settings.get_azure_core_credentials()
        else:
            return self.settings.get_credentials()