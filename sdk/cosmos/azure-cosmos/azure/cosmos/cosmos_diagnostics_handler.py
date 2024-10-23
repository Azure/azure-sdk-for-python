from multidict import CIMultiDict
from typing import Optional


class CosmosDiagnosticsHandler(CIMultiDict):
    def __init__(self):
        super().__init__()
        self._preset_keys = {
            'duration': None,
            'status code': None,
            'sub status code': None,
            'verb': None,
            'resource type': None
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
            resource_type: Optional[str] = None,
            is_request: bool = False
    ) -> bool:
        params = {
            'duration': duration,
            'status code': status_code,
            'sub status code': sub_status_code,
            'verb': verb,
            'resource type': resource_type
        }
        for key, param in params.items():
            if param is not None and self[key] is not None:
                if self[key](param):
                    return True
        return False
