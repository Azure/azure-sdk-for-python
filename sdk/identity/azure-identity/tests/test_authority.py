# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.identity._constants import EnvironmentVariables, KnownAuthorities
from azure.identity._internal import get_default_authority, normalize_authority
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
