# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


class ApiVersion(str, Enum):
    """Text Analytics API versions supported by this package"""

    #: this is the default version
    V3_1_PREVIEW_1 = "v3.1-preview.1"
    V3_0 = "v3.0"


def load_generated_api(api_version, aio=False):
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

    if api_version == ApiVersion.V3_1_PREVIEW_1:
        if aio:
            from ._generated.v3_1_preview_1.aio import TextAnalyticsClient
        else:
            from ._generated.v3_1_preview_1 import TextAnalyticsClient  # type: ignore
    elif api_version == ApiVersion.V3_0:
        if aio:
            from ._generated.v3_0.aio import TextAnalyticsClient  # type: ignore
        else:
            from ._generated.v3_0 import TextAnalyticsClient  # type: ignore
    return TextAnalyticsClient
