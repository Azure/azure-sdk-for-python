# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._template_code import template_main, pipeline_check_probe

__all__ = ["template_main", "pipeline_check_probe"]
__version__ = VERSION
