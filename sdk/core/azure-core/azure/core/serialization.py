# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

__all__ = ["NULL"]

class _Null(object):
    """To create a Falsy object
    """
    def __bool__(self):
        return False

    __nonzero__ = __bool__ # Python2 compatibility


NULL = _Null()
