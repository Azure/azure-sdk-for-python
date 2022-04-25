# Test file for enum checker
from enum import Enum
from six import with_metaclass
from azure.core import CaseInsensitiveEnumMeta

class EnumPython2(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    ONE = "one"
    TWO = "two"
