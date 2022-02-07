# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum


class DocumentAnalysisApiVersion(str, Enum):
    """Form Recognizer API versions supported by DocumentAnalysisClient and DocumentModelAdministrationClient."""

    #: This is the default version
    V2022_01_30_PREVIEW = "2022-01-30-preview"


class FormRecognizerApiVersion(str, Enum):
    """Form Recognizer API versions supported by FormRecognizerClient and FormTrainingClient."""

    #: This is the default version
    V2_1 = "2.1"
    V2_0 = "2.0"


def validate_api_version(api_version, client_kind):
    # type: (str, str) -> None
    """Raise ValueError if api_version is invalid """

    if client_kind == "form":
        try:
            api_version = FormRecognizerApiVersion(api_version)
        except ValueError:
            err_message = "Unsupported API version '{}'. Please select from: {}".format(
                api_version, ", ".join(v.value for v in FormRecognizerApiVersion)
            )
            try:
                api_version = DocumentAnalysisApiVersion(api_version)
                err_message += (
                    "\nAPI version '{}' is only available for "
                    "DocumentAnalysisClient and DocumentModelAdministrationClient.".format(
                        api_version
                    )
                )
            except ValueError:
                pass
            raise ValueError(err_message)
    else:
        try:
            api_version = DocumentAnalysisApiVersion(api_version)
        except ValueError:
            err_message = "Unsupported API version '{}'. Please select from: {}".format(
                api_version, ", ".join(v.value for v in DocumentAnalysisApiVersion)
            )
            try:
                api_version = FormRecognizerApiVersion(api_version)
                err_message += (
                    "\nAPI version '{}' is only available for "
                    "FormRecognizerClient and FormTrainingClient.".format(api_version)
                )
            except ValueError:
                pass
            raise ValueError(err_message)
