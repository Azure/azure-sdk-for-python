from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class MyGoodEnum2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"

class MyBadEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"
