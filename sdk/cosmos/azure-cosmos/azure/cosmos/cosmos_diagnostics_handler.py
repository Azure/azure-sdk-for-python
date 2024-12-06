from multidict import CIMultiDict
from typing import Optional


class CosmosDiagnosticsHandler(CIMultiDict):
    # To customize the diagnostic handler, you can modify the conditions in the _preset_keys dictionary.
    # For example, to log if the duration is greater than 500 ms, you can set:
    # self._preset_keys['duration'] = lambda x: x > 500
    # Similarly, you can add or modify conditions for other keys as needed.
    def __init__(self) -> None:
        """
        Initializes the CosmosDiagnosticsHandler with preset keys and their corresponding conditions.
        To customize the diagnostic handler, you can modify the conditions in the _preset_keys dictionary.
        For example, to log if the duration is greater than 500 ms, you can set:
        self._preset_keys['duration'] = lambda x: x > 500
        or
        def check_duration(duration: int) -> bool:
            return duration > 500
        self._preset_keys['duration'] = check_duration
        Similarly, you can add or modify conditions for other keys as needed.
        When Using this as an instance, you can modify the values of the keys in the dictionary.
        Example:
            handler = CosmosDiagnosticsHandler()
            handler['duration'] = lambda x: x > 500
            or with a function.
            def check_duration(duration: int) -> bool:
                return duration > 500
            handler['duration'] = check_duration
        """
        super().__init__()
        self._preset_keys = {
            'duration': None,  # Log if duration is greater than 1000 ms
            'status code': (lambda x: (
                    isinstance(x, (list, tuple)) and x[0] >= 500 and (x[1] is None or x[1] != 0)
            ) if isinstance(x, (list, tuple)) else x >= 500),  # Log if status code is not 200
            'verb': None  # No condition for verb
        }
        for key, value in self._preset_keys.items():
            self[key] = value

    def __setitem__(self, key, value):
        if key.lower() in self._preset_keys:
            super().__setitem__(key, value)
        else:
            raise KeyError(f"Cannot add new key: {key}")

    def __delitem__(self, key):
        raise KeyError(f"Cannot delete key: {key}")

    def __call__(
            self,
            duration: Optional[int] = None,
            status_code: Optional[int] = None,
            sub_status_code: Optional[int] = None,
            verb: Optional[str] = None,
            is_request: bool = False
    ) -> bool:
        params = {
            'duration': duration,
            'status code': (status_code, sub_status_code) if status_code else None,
            'verb': verb
        }
        for key, param in params.items():
            if param is not None and self[key] is not None:
                if self[key](param):
                    return True
        return False

    def get_preset_keys(self):
        return self._preset_keys.keys()
