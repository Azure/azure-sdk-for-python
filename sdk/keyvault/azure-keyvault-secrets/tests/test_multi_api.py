# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from azure.keyvault.secrets import ApiVersion, SecretClient
import pytest


@pytest.mark.parametrize("version", ApiVersion)
def test_supported_version(version):
    """The client should be able to load generated code for every supported API version"""

    SecretClient("https://localhost", credential=object(), api_version=version)


def test_unsupported_version():
    """When given an unsupported API version, the client should raise an error listing supported versions"""

    with pytest.raises(NotImplementedError) as ex:
        client = SecretClient("https://localhost", credential=object(), api_version="nonsense")
    assert all(version.value in str(ex.value) for version in ApiVersion)
