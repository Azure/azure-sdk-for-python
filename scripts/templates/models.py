# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
{%- for api_version_module in api_version_modules %}
from .{{ api_version_module }}.models import *
{%- endfor %}
