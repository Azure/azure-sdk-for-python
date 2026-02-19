# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class GenericTestProxyParametrize1:
    def __call__(self, fn):
        def _wrapper(test_class, a, **kwargs):
            fn(test_class, a, **kwargs)
        return _wrapper


class GenericTestProxyParametrize2:
    def __call__(self, fn):
        def _wrapper(test_class, a, b, **kwargs):
            fn(test_class, a, b, **kwargs)
        return _wrapper
