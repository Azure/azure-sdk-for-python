# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
{%- for mod_api_version in default_models %}
from .{{ mod_api_version }}.models import *
{%- endfor %}
