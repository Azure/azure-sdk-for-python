# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class Described:
    def __new__(cls, value, descriptor=None):
        obj = super().__new__(cls, value)
        obj.descriptor = descriptor
        return obj


class DescribedInt(Described, int):
    pass


class DescribedFloat(Described, float):
        pass


class DescribedStr(Described, str):
    pass


class DescribedBytes(Described, bytes):
    pass


class DescribedList(Described, list):
    pass


class DescribedDict(Described, dict):
    pass
