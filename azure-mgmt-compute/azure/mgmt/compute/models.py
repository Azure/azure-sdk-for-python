# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings

from .v2017_03_30.models import *
from .v2017_09_01.models import *
from .v2017_12_01.models import * # Note that this line is overriding some models of 2017-03-30. See link below for details.

warnings.warn("Import models from this file is deprecated. See https://aka.ms/pysdkmodels",
              DeprecationWarning)
