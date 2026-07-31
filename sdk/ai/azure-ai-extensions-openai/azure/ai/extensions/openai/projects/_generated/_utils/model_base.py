# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Minimal model_base compatibility for TypedDict generation."""

from datetime import date, datetime
from json import JSONEncoder
from typing import Any


class Model(dict[str, Any]):
    """Dictionary-backed model marker used by generated multipart helpers."""


class SdkJSONEncoder(JSONEncoder):
    """JSON encoder compatible with generated multipart helpers."""

    def __init__(self, *args: Any, exclude_readonly: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.exclude_readonly = exclude_readonly

    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        enum_value = getattr(o, "value", None)
        if enum_value is not None:
            return enum_value
        if isinstance(o, set):
            return list(o)
        return super().default(o)
