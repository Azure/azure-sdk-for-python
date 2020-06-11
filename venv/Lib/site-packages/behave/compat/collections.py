# -*- coding: utf-8 -*-
"""
Compatibility of :module:`collections` between different Python versions.
"""

from __future__ import absolute_import
import warnings
# pylint: disable=unused-import
try:
    # -- SINCE: Python2.7
    from collections import OrderedDict
except ImportError:     # pragma: no cover
    try:
        # -- BACK-PORTED FOR: Python 2.4 .. 2.6
        from ordereddict import OrderedDict
    except ImportError:
        message = "collections.OrderedDict is missing: Install 'ordereddict'."
        warnings.warn(message)
        # -- BACKWARD-COMPATIBLE: Better than nothing (for behave use case).
        OrderedDict = dict
