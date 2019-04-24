# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings

from .v2017_09_01.models import *
from .v2018_09_30.models import *
from .v2018_10_01.models import *
from .v2019_03_01.models import * # Note that this line is overriding some models of 2018-09-01. See link below for details.

warnings.warn("Import models from this file is deprecated. See https://aka.ms/pysdkmodels",
              DeprecationWarning)
