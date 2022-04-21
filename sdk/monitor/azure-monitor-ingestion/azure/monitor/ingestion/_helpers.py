from typing import Optional
from azure.core.credentials import TokenCredential
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

def get_authentication_policy(
    endpoint: str,
    credential: "TokenCredential",
    audience: Optional[str] = None
) -> BearerTokenCredentialPolicy:
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy"""
    scope = endpoint.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")
