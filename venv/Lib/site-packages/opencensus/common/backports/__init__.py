# Copyright 2019, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import six
import weakref


class WeakMethod(weakref.ref):  # pragma: NO COVER
    """
    A custom `weakref.ref` subclass which simulates a weak reference to
    a bound method, working around the lifetime problem of bound methods.

    This is a copy of the WeakMethod class that ships with weakref in the
    python 3.7 standard library, adapted to work in 2.6. See:
    https://github.com/python/cpython/blob/a31f4cc881992e84d351957bd9ac1a92f882fa39/Lib/weakref.py#L36-L87
    """  # noqa

    __slots__ = "_func_ref", "_meth_type", "_alive", "__weakref__"

    def __new__(cls, meth, callback=None):
        try:
            obj = meth.__self__
            func = meth.__func__
        except AttributeError:
            error = TypeError("argument should be a bound method, not {}"
                              .format(type(meth)))
            six.raise_from(error, None)

        def _cb(arg):
            # The self-weakref trick is needed to avoid creating a reference
            # cycle.
            self = self_wr()
            if self._alive:
                self._alive = False
                if callback is not None:
                    callback(self)
        self = weakref.ref.__new__(cls, obj, _cb)
        self._func_ref = weakref.ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = True
        self_wr = weakref.ref(self)
        return self

    def __call__(self):
        obj = super(WeakMethod, self).__call__()
        func = self._func_ref()
        if obj is None or func is None:
            return None
        return self._meth_type(func, obj)

    def __eq__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is other
            return (weakref.ref.__eq__(self, other)
                    and self._func_ref == other._func_ref)
        return False

    def __ne__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is not other
            return (weakref.ref.__ne__(self, other)
                    or self._func_ref != other._func_ref)
        return True

    __hash__ = weakref.ref.__hash__
