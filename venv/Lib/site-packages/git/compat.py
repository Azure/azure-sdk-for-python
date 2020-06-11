# -*- coding: utf-8 -*-
# config.py
# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php
"""utilities to help provide compatibility with python 3"""
# flake8: noqa

import locale
import os
import sys


from gitdb.utils.encoding import (
    force_bytes,     # @UnusedImport
    force_text       # @UnusedImport
)


is_win = (os.name == 'nt')
is_posix = (os.name == 'posix')
is_darwin = (os.name == 'darwin')
defenc = sys.getfilesystemencoding()


def safe_decode(s):
    """Safely decodes a binary string to unicode"""
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(defenc, 'surrogateescape')
    elif s is not None:
        raise TypeError('Expected bytes or text, but got %r' % (s,))


def safe_encode(s):
    """Safely decodes a binary string to unicode"""
    if isinstance(s, str):
        return s.encode(defenc)
    elif isinstance(s, bytes):
        return s
    elif s is not None:
        raise TypeError('Expected bytes or text, but got %r' % (s,))


def win_encode(s):
    """Encode unicodes for process arguments on Windows."""
    if isinstance(s, str):
        return s.encode(locale.getpreferredencoding(False))
    elif isinstance(s, bytes):
        return s
    elif s is not None:
        raise TypeError('Expected bytes or text, but got %r' % (s,))


def with_metaclass(meta, *bases):
    """copied from https://github.com/Byron/bcore/blob/master/src/python/butility/future.py#L15"""
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, nbases, d):
            if nbases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass(meta.__name__ + 'Helper', None, {})
