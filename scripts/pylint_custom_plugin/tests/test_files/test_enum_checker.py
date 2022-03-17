# Test file for enum checker


class EnumPython2(CaseInsensitiveEnumMeta(str, Enum)):
    ONE = "one"
    TWO = "two"

class EnumPython3(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    ONE = "one"
    TWO = "two"

