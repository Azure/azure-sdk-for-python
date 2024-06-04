# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import pytest
from azure.keyvault.keys import ApiVersion, KeyClient


@pytest.mark.parametrize("version", ApiVersion)
def test_supported_version(version):
    """The client should be able to load generated code for every supported API version"""

    KeyClient("https://localhost", credential=object(), api_version=version)


def test_unsupported_version():
    """When given an unsupported API version, the client should _not_ raise an error"""

    KeyClient("https://localhost", credential=object(), api_version="nonsense")
