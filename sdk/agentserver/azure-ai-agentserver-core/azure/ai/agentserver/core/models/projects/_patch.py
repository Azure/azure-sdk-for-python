# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Dict
from ._patch_evaluations import EvaluatorIds
from ._models import CustomCredential as CustomCredentialGenerated


class CustomCredential(CustomCredentialGenerated):
    """Custom credential definition.

    :ivar type: The credential type. Always equals CredentialType.CUSTOM. Required.
    :vartype type: str or ~azure.ai.projects.models.CredentialType
    :ivar credential_keys: The secret custom credential keys. Required.
    :vartype credential_keys: dict[str, str]
    """

    credential_keys: Dict[str, str] = {}
    """The secret custom credential keys. Required."""


__all__: List[str] = [
    "EvaluatorIds",
    "CustomCredential",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
