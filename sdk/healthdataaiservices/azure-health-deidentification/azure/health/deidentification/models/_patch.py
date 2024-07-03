# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import TYPE_CHECKING, List, Optional, Union
from ._models import DeidentificationContent as DeidentificationContentGenerated

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import models as _models


class DeidentificationContent(DeidentificationContentGenerated):
    """Request for synchronous De-Identify operation.

    All required parameters must be populated in order to send to server.

    :ivar input_text: Input text to deidentify. Required.
    :vartype input_text: str
    :ivar operation: Operation to perform on the input. Required. Known values are: "Redact",
     "Surrogate", and "Tag".
    :vartype operation: str or ~azure.health.deidentification.models.OperationType
    :ivar data_type: Data type of the input. Required. "Plaintext"
    :vartype data_type: str or ~azure.health.deidentification.models.DocumentDataType
    :ivar redaction_format: Format of the redacted output. Only valid when OperationType is Redact.
    :vartype redaction_format: str
    """

    # This isn't a perfect solution as it still allows customers to update the stringIndexType manually without the constructor.
    def __init__(
        self,
        *,
        input_text: str,
        operation: Union[str, "_models.OperationType"],
        data_type: Union[str, "_models.DocumentDataType"],
        redaction_format: Optional[str] = None,
    ):
        super(DeidentificationContent, self).__init__(
            input_text=input_text,
            operation=operation,
            data_type=data_type,
            string_index_type=_models.StringIndexType.UNICODE_CODE_POINT,
            redaction_format=redaction_format,
        )


__all__: List[str] = [
    "DeidentificationContent"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
