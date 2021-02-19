# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
from enum import Enum
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta

class MyCustomEnum(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    FOO = 'foo'
    BAR = 'bar'


def test_case_insensitive_enums():
    assert MyCustomEnum.foo.value == 'foo'
    assert MyCustomEnum.FOO.value == 'foo'
    assert MyCustomEnum('bar').value == 'bar'
    assert 'bar' == MyCustomEnum.BAR
    assert 'bar' == MyCustomEnum.bar
    assert MyCustomEnum['foo'] == 'foo'
    assert MyCustomEnum['FOO'] == 'foo'
    assert isinstance(MyCustomEnum.BAR, str)
