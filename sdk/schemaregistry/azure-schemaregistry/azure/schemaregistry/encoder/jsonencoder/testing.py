from typing import Any
try:
    import jsonschema
except ImportError:
    raise ImportError("install jsonschema to use this feature") from None

class TempClient:
    def __init__(self, val: jsonschema.protocols.Validator, **kwargs: Any) -> None:
        pass
