# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List
from typing import Any, List, Mapping, Optional, TYPE_CHECKING, Union, overload

from ._models import (
    DocumentStatus as GeneratedDocumentStatus,
    TranslationStatus as GeneratedTranslationStatus,
)


def convert_status(status, ll=False):
    if ll is False:
        if status == "Cancelled":
            return "Canceled"
        if status == "Cancelling":
            return "Canceling"
    elif ll is True:
        if status == "Canceled":
            return "Cancelled"
        if status == "Canceling":
            return "Cancelling"
    return status


class DocumentStatus(GeneratedDocumentStatus):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        doc_status = kwargs.get("mapping")
        if not doc_status:
            doc_status = args[0]
        try:
            doc_status["status"] = convert_status(doc_status["status"])
        except KeyError:
            kwargs["status"] = convert_status(kwargs["status"])
        super().__init__(*args, **kwargs)


class TranslationStatus(GeneratedTranslationStatus):
    def __getattr__(self, name: str) -> Any:
        backcompat_attrs = [
            "documents_total_count",
            "documents_failed_count",
            "documents_in_progress_count",
            "documents_succeeded_count",
            "documents_not_started_count",
            "documents_canceled_count",
        ]
        if name in backcompat_attrs:
            return self.summary[name.split("documents_")[1].split("_count")[0]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        translation_status = kwargs.get("mapping")
        if not translation_status:
            translation_status = args[0]
        try:
            translation_status["status"] = convert_status(translation_status["status"])
        except KeyError:
            kwargs["status"] = convert_status(kwargs["status"])
        super().__init__(*args, **kwargs)


__all__: List[str] = [
    "DocumentStatus",
    "TranslationStatus",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
