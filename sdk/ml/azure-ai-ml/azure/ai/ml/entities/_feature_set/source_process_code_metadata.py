# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Any, Optional


class SourceProcessCodeMetadata(object):
    def __init__(self, *, path: str, process_class: Optional[str] = None, **kwargs: Any):
        self.path = path
        self.process_class = process_class
