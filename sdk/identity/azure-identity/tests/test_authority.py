# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import patch

from azure.identity._constants import EnvironmentVariables, KnownAuthorities
from azure.identity._internal import get_default_authority, normalize_authority
from azure.identity._internal.utils import get_regional_authority
import pytest


def test_get_default_authority():
    """get_default_authority should return public cloud or the value of $AZURE_AUTHORITY_HOST, with 'https' scheme"""

    # default scheme is https
    for authority in ("localhost", "https://localhost"):
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
            assert get_default_authority() == "https://localhost"

    # default to public cloud
    for environ in ({}, {EnvironmentVariables.AZURE_AUTHORITY_HOST: KnownAuthorities.AZURE_PUBLIC_CLOUD}):
        with patch.dict("os.environ", environ, clear=True):
            assert get_default_authority() == "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD

    # require https
    with pytest.raises(ValueError):
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: "http://localhost"}, clear=True):
            get_default_authority()


def test_normalize_authority():
    """normalize_authority should return a URI with a scheme and no trailing spaces or forward slashes"""

    localhost = "localhost"
    localhost_tls = "https://" + localhost

    # accept https if specified, default to it when no scheme specified
    for uri in (localhost, localhost_tls):
        assert normalize_authority(uri) == localhost_tls

        # remove trailing characters
        for string in ("/", " ", "/ ", " /"):
            assert normalize_authority(uri + string) == localhost_tls

    # raise for other schemes
    for scheme in ("http", "file"):
        with pytest.raises(ValueError):
            normalize_authority(scheme + "://localhost")


def test_get_regional_authority():
    """get_regional_authority should return the regional authority or None based on environment variable"""

    # Test with no regional authority environment variable set
    with patch.dict("os.environ", {}, clear=True):
        assert get_regional_authority("https://login.microsoftonline.com") is None
        assert get_regional_authority("https://custom.authority.com") is None

    # Test with empty regional authority environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: ""}, clear=True):
        assert get_regional_authority("https://login.microsoftonline.com") is None
        assert get_regional_authority("https://custom.authority.com") is None

    # Test with known Microsoft authority hosts - should use login.microsoft.com as regional host
    test_region = "eastus"
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: test_region}, clear=True):
        # Test login.microsoftonline.com
        result = get_regional_authority("https://login.microsoftonline.com")
        assert result == f"https://{test_region}.login.microsoft.com"

        # Test login.microsoft.com
        result = get_regional_authority("https://login.microsoft.com")
        assert result == f"https://{test_region}.login.microsoft.com"

        # Test login.windows.net
        result = get_regional_authority("https://login.windows.net")
        assert result == f"https://{test_region}.login.microsoft.com"

        # Test sts.windows.net
        result = get_regional_authority("https://sts.windows.net")
        assert result == f"https://{test_region}.login.microsoft.com"

    # Test with custom authority hosts - should use the original host
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: test_region}, clear=True):
        result = get_regional_authority("https://custom.authority.com")
        assert result == f"https://{test_region}.custom.authority.com"

        result = get_regional_authority("https://login.chinacloudapi.cn")
        assert result == f"https://{test_region}.login.chinacloudapi.cn"

        result = get_regional_authority("https://login.microsoftonline.us")
        assert result == f"https://{test_region}.login.microsoftonline.us"

    # Test edge cases with different regional authority values
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: "westus2"}, clear=True):
        result = get_regional_authority("https://login.microsoftonline.com")
        assert result == "https://westus2.login.microsoft.com"

        result = get_regional_authority("https://example.com")
        assert result == "https://westus2.example.com"

    # Test a string central authority
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: "centralus"}, clear=True):
        assert get_regional_authority("localhost") is None

    # Test with "tryautodetect" value for regional authority
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: "tryautodetect"}, clear=True):
        result = get_regional_authority("https://login.microsoftonline.com")
        assert result is None
