# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple
from enum import Enum
from typing import TYPE_CHECKING

from .._generated.v7_1_preview.version import VERSION as V7_1_PREVIEW_VERSION
from .._generated.v7_0.version import VERSION as V7_0_VERSION
from .._generated.v2016_10_01.version import VERSION as V2016_10_01_VERSION

if TYPE_CHECKING:
    from typing import Union


class ApiVersion(Enum):
    """Key Vault API versions supported by this package"""

    #: this is the default version
    V7_1_preview = V7_1_PREVIEW_VERSION
    V7_0 = V7_0_VERSION
    V2016_10_01 = V2016_10_01_VERSION


DEFAULT_VERSION = ApiVersion.V7_1_preview

GeneratedApi = namedtuple("GeneratedApi", ("models", "client_cls", "config_cls"))


def load_generated_api(api_version, aio=False):
    # type: (Union[ApiVersion, str], bool) -> GeneratedApi
    api_version = api_version or DEFAULT_VERSION
    try:
        # api_version could be a string; map it to an instance of ApiVersion
        # (this is a no-op if it's already an instance of ApiVersion)
        api_version = ApiVersion(api_version)
    except ValueError:
        # api_version is unknown to ApiVersion
        raise NotImplementedError(
            "This package doesn't support API version '{}'. ".format(api_version)
            + "Supported versions: {}".format(", ".join(v.value for v in ApiVersion))
        )

    if api_version == ApiVersion.V7_1_preview:
        from .._generated.v7_1_preview import models

        if aio:
            from .._generated.v7_1_preview.aio import KeyVaultClient
            from .._generated.v7_1_preview.aio._configuration_async import KeyVaultClientConfiguration
        else:
            from .._generated.v7_1_preview import KeyVaultClient  # type: ignore
            from .._generated.v7_1_preview._configuration import KeyVaultClientConfiguration  # type: ignore
    elif api_version == ApiVersion.V7_0:
        from .._generated.v7_0 import models  # type: ignore

        if aio:
            from ._configuration_async._generated.v7_0.aio import KeyVaultClient  # type: ignore
            from .._generated.v7_0.aio._configuration_async import KeyVaultClientConfiguration  # type: ignore
        else:
            from .._generated.v7_0 import KeyVaultClient  # type: ignore
            from .._generated.v7_0._configuration import KeyVaultClientConfiguration  # type: ignore
    elif api_version == ApiVersion.V2016_10_01:
        from .._generated.v2016_10_01 import models  # type: ignore

        if aio:
            from .._generated.v2016_10_01.aio import KeyVaultClient  # type: ignore
            from .._generated.v2016_10_01.aio._configuration_async import KeyVaultClientConfiguration  # type: ignore
        else:
            from .._generated.v2016_10_01 import KeyVaultClient  # type: ignore
            from .._generated.v2016_10_01._configuration import KeyVaultClientConfiguration  # type: ignore

    return GeneratedApi(models=models, client_cls=KeyVaultClient, config_cls=KeyVaultClientConfiguration)
