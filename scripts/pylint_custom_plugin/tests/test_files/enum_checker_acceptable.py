# Test file for enum checker


class EnumPython2(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    ONE = "one"
    TWO = "two"
    