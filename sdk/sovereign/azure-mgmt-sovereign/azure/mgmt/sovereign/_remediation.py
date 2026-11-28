# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from collections.abc import Mapping
from typing import Optional

from azure.core.exceptions import DeserializationError

from .models import SovereignViewRemediateResult


def _normalize_remediation_result(result: Optional[SovereignViewRemediateResult]) -> SovereignViewRemediateResult:
    if result is None:
        raise DeserializationError("The remediation response is missing its required remediationId.")
    identifier = result.get("remediationId")
    if identifier is None:
        properties = result.get("properties")
        if isinstance(properties, Mapping):
            identifier = properties.get("remediationId")
    if not isinstance(identifier, str) or not identifier.strip():
        raise DeserializationError("The remediation response is missing a valid required remediationId.")
    result.remediation_id = identifier
    return result
