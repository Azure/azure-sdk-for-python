from typing import List, Optional, NamedTuple, Protocol, runtime_checkable, Union

class BreakingChange(NamedTuple):
    message: str
    change_type: str
    module: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    parameter_name: Optional[str] = None

class Suppression(NamedTuple):
    change_type: str
    module: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    parameter_or_property_name: Optional[str] = None

@runtime_checkable
class ChangesChecker(Protocol):
    name: str
    message: Union[str, dict]

    def run_check(self, diff: dict, stable_nodes: dict, current_nodes: dict, **kwargs) -> List[BreakingChange]:
        ...
