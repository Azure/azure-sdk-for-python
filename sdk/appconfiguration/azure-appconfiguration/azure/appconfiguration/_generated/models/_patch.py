# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import Any, Dict, List, Mapping, Optional, overload

from .. import _model_base
from .._model_base import rest_field


class KeyValue(_model_base.Model):
    """A key-value pair representing application settings.

    Readonly variables are only populated by the server, and will be ignored when sending a request.


    :ivar key: The key of the key-value.
    :vartype key: str
    :ivar label: The label the key-value belongs to.
    :vartype label: str
    :ivar content_type: The content type of the value stored within the key-value.
    :vartype content_type: str
    :ivar value: The value of the key-value.
    :vartype value: str
    :ivar last_modified: A date representing the last time the key-value was modified.
    :vartype last_modified: ~datetime.datetime
    :ivar tags: The tags of the key-value.
    :vartype tags: dict[str, str]
    :ivar locked: Indicates whether the key-value is locked.
    :vartype locked: bool
    :ivar etag: A value representing the current state of the resource.
    :vartype etag: str
    """

    key: str = rest_field()
    """The key of the key-value."""
    label: Optional[str] = rest_field()
    """The label the key-value belongs to."""
    content_type: Optional[str] = rest_field()
    """The content type of the value stored within the key-value."""
    value: Optional[str] = rest_field()
    """The value of the key-value."""
    last_modified: Optional[datetime.datetime] = rest_field(format="rfc3339")
    """A date representing the last time the key-value was modified."""
    tags: Optional[Dict[str, str]] = rest_field()
    """The tags of the key-value."""
    locked: Optional[bool] = rest_field()
    """Indicates whether the key-value is locked."""
    etag: Optional[str] = rest_field()
    """A value representing the current state of the resource."""

    @overload
    def __init__(
        self,
        *,
        key: Optional[str] = None,
        label: Optional[str] = None,
        content_type: Optional[str] = None,
        value: Optional[str] = None,
        last_modified: Optional[datetime.datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        locked: Optional[bool] = None,
        etag: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


__all__: List[str] = ["KeyValue"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
