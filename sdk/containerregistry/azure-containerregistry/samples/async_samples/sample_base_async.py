# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_base_async.py

DESCRIPTION:
    This is the base class for async samples. It imports some images that could be used in samples.
"""
from samples.sample_base import SampleBase

class SampleBaseAsync(SampleBase):
    def __init__(self):
        super().__init__(is_async=True)
        
