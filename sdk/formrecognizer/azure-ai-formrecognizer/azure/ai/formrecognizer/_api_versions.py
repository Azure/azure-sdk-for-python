# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum


class FormRecognizerApiVersion(str, Enum):
    """Form Recognizer service API versions supported by this package"""

    V2_0 = "v2.0"


def validate_api_version(api_version):
    # type: (str) -> None
    """Raise ValueError if api_version is invalid """
    if not api_version:
        return

    try:
        api_version = FormRecognizerApiVersion(api_version)
    except ValueError:
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, ", ".join(v.value for v in FormRecognizerApiVersion))
        )
