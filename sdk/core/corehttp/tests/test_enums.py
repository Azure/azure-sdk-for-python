# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from enum import Enum

from corehttp.utils import CaseInsensitiveEnumMeta


class MyCustomEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    FOO = "foo"
    BAR = "bar"


def test_case_insensitive_enums():
    assert MyCustomEnum.foo.value == "foo"
    assert MyCustomEnum.FOO.value == "foo"
    assert MyCustomEnum("bar").value == "bar"
    assert "bar" == MyCustomEnum.BAR
    assert "bar" == MyCustomEnum.bar
    assert MyCustomEnum["foo"] == "foo"
    assert MyCustomEnum["FOO"] == "foo"
    assert isinstance(MyCustomEnum.BAR, str)
