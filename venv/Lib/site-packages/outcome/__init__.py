# coding: utf-8
"""Top-level package for outcome."""
from __future__ import absolute_import, division, print_function

import sys

from ._util import AlreadyUsedError, fixup_module_metadata
from ._version import __version__

if sys.version_info >= (3, 5):
    from ._async import Error, Outcome, Value, acapture, capture
    __all__ = (
        'Error', 'Outcome', 'Value', 'acapture', 'capture', 'AlreadyUsedError'
    )
else:
    from ._sync import Error, Outcome, Value, capture
    __all__ = ('Error', 'Outcome', 'Value', 'capture', 'AlreadyUsedError')

fixup_module_metadata(__name__, globals())
del fixup_module_metadata
