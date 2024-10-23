from .cosmos_diagnostics_handler import CosmosDiagnosticsHandler
from typing import Optional


class DefaultCosmosDiagnosticsHandler(CosmosDiagnosticsHandler):
    # To customize the diagnostic handler, you can modify the conditions in the _preset_keys dictionary.
    # For example, to log if the duration is greater than 500 ms, you can set:
    # self._preset_keys['duration'] = lambda x: x > 500
    # Similarly, you can add or modify conditions for other keys as needed.
    def __init__(self) -> None:
        """
        Initializes the DefaultCosmosDiagnosticsHandler with preset keys and their corresponding conditions.
        """
        super().__init__()
        self._preset_keys = {
            'duration': lambda x: x > 1000,  # Log if duration is greater than 1000 ms
            'status code': lambda x: x != 200,  # Log if status code is not 200
            'sub status code': lambda x: x != 0,  # Log if sub status code is not 0
            'verb': None,  # No condition for verb
            'resource type': None  # No condition for resource type
        }
        for key, value in self._preset_keys.items():
            self[key] = value

    def __call__(
            self,
            duration: Optional[int] = None,
            status_code: Optional[int] = None,
            sub_status_code: Optional[int] = None,
            verb: Optional[str] = None,
            resource_type: Optional[str] = None,
            is_request: bool = False
    ) -> bool:
        """
        Checks all conditions and returns True only if all conditions are met.

        :param duration: Duration in milliseconds.
        :param status_code: HTTP status code.
        :param sub_status_code: Sub-status code.
        :param verb: HTTP verb.
        :param resource_type: Type of resource.
        :return: True if all conditions are met, False otherwise.
        """
        params = {
            'duration': duration,
            'status code': status_code,
            'sub status code': sub_status_code,
            'verb': verb,
            'resource type': resource_type
        }
        if is_request:
            return True
        for key, param in params.items():
            if param is not None and self[key] is not None:
                if not self[key](param):
                    return False
        return True
