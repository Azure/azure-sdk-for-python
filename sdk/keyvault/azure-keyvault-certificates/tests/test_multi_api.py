# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from azure.keyvault.certificates import ApiVersion, CertificateClient
from azure.keyvault.certificates.aio import CertificateClient as AsyncCertificateClient
import pytest


SUPPORTED_VERSIONS = {
    "V2026_04_01": "2026-04-01",
    "V2025_07_01": "2025-07-01",
    "V7_6": "7.6",
    "V7_5": "7.5",
    "V7_4": "7.4",
    "V7_3": "7.3",
    "V7_2": "7.2",
    "V7_1": "7.1",
    "V7_0": "7.0",
    "V2016_10_01": "2016-10-01",
}


def test_api_versions():
    assert {name: version.value for name, version in ApiVersion.__members__.items()} == SUPPORTED_VERSIONS

    with pytest.raises(ValueError):
        ApiVersion("2026-03-01-preview")


@pytest.mark.parametrize("client_type", [CertificateClient, AsyncCertificateClient])
@pytest.mark.parametrize("version", SUPPORTED_VERSIONS.values())
@pytest.mark.parametrize("as_enum", [False, True])
def test_supported_version(client_type, version, as_enum):
    """Both clients should forward every supported API version as a plain string."""
    client = client_type(
        "https://localhost", credential=object(), api_version=ApiVersion(version) if as_enum else version
    )

    assert type(client.api_version) is str
    assert client.api_version == version
    assert client._client._config.api_version == version


@pytest.mark.parametrize("client_type", [CertificateClient, AsyncCertificateClient])
def test_default_version(client_type):
    client = client_type("https://localhost", credential=object())

    assert type(client.api_version) is str
    assert client.api_version == "2026-04-01"
    assert client._client._config.api_version == "2026-04-01"


@pytest.mark.parametrize("client_type", [CertificateClient, AsyncCertificateClient])
@pytest.mark.parametrize("version", ["nonsense", "2026-03-01-preview", "7.6-preview.2", "", None])
def test_unsupported_version(client_type, version):
    """The API version enum must not restrict custom version overrides."""
    client = client_type("https://localhost", credential=object(), api_version=version)

    assert client.api_version == version
    assert client._client._config.api_version == version
