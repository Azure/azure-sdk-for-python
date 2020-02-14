# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

from ._generated.v7_0.version import VERSION as V7_0_VERSION
from ._generated.v2016_10_01.version import VERSION as V2016_10_01_VERSION

SUPPORTED_VERSIONS = (V7_0_VERSION, V2016_10_01_VERSION)
DEFAULT_VERSION = V7_0_VERSION

GeneratedApi = namedtuple("GeneratedApi", ("models", "client_cls", "config_cls"))


def load_generated_api(api_version, aio=False):
    # type: (str, bool) -> GeneratedApi
    api_version = api_version or DEFAULT_VERSION
    if api_version == V7_0_VERSION:
        from ._generated.v7_0 import models

        if aio:
            from ._generated.v7_0.aio import KeyVaultClient
            from ._generated.v7_0.aio._configuration_async import KeyVaultClientConfiguration
        else:
            from ._generated.v7_0 import KeyVaultClient  # type: ignore
            from ._generated.v7_0._configuration import KeyVaultClientConfiguration  # type: ignore
    elif api_version == V2016_10_01_VERSION:
        from ._generated.v2016_10_01 import models  # type: ignore

        if aio:
            from ._generated.v2016_10_01.aio import KeyVaultClient  # type: ignore
            from ._generated.v2016_10_01.aio._configuration_async import KeyVaultClientConfiguration  # type: ignore
        else:
            from ._generated.v2016_10_01 import KeyVaultClient  # type: ignore
            from ._generated.v2016_10_01._configuration import KeyVaultClientConfiguration  # type: ignore
    else:
        raise NotImplementedError(
            "This package doesn't support API version '{}'. ".format(api_version)
            + "Supported versions: {}".format(", ".join(SUPPORTED_VERSIONS))
        )

    return GeneratedApi(models=models, client_cls=KeyVaultClient, config_cls=KeyVaultClientConfiguration)
