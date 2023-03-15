# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Optional


class FeatureTransformationCodeMetadata(object):
    def __init__(self, *, path: str, transformer_class: Optional[str] = None, **kwargs):
        self.path = path
        self.transformer_class = transformer_class
