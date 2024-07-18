from typing import Any, Dict, List, Union, Optional, NamedTuple, Protocol, TypedDict, runtime_checkable

class BreakingChange(NamedTuple):
    message: str
    change_type: str
    module: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    parameter_name: Optional[str] = None

@runtime_checkable
class Checker(Protocol):
    # checker: "BreakingChangesTracker"
    name: str
    message: str

    def init(self):
        pass

    def run_check(nodes: Dict, **kwargs) -> List[BreakingChange]:
        pass

class ParameterNode(TypedDict):
    param_type: str
    default: Union[str, None]

# Should be function or method node
class FunctionNode(TypedDict):
    parameters: Dict[str, ParameterNode]
    return_type: Optional[str]
    is_async: bool

class PropertyNode(TypedDict):
    type: str
    default: Union[str, None] # should this be Any?

class ClassNode(TypedDict):
    type: Optional[str]
    methods: Dict[str, FunctionNode]
    properties: Dict[str, Any] # after adding typing this should be Dict[str, Dict]

class ModuleNode(TypedDict):
    class_nodes: Dict[str, ClassNode]
    function_nodes: Dict[str, FunctionNode]

@runtime_checkable
class ModuleChangesChecker(Checker, Protocol):
    def run_check(self, module_nodes: Dict[str, ModuleNode]) -> List[BreakingChange]:
        ...

@runtime_checkable
class ClassChangesChecker(Checker, Protocol):
    def run_check(self, class_nodes: Dict[str, ClassNode]) -> List[BreakingChange]:
        ...

@runtime_checkable
class FunctionChangesChecker(Checker, Protocol):
    def run_check(self, function_nodes: Dict[str, FunctionNode]) -> List[BreakingChange]:
        ...

@runtime_checkable
class PropertyChangesChecker(Checker, Protocol):
    def run_check(self, property_nodes: Dict[str, PropertyNode]) -> List[BreakingChange]:
        ...

@runtime_checkable
class ParameterChangesChecker(Checker, Protocol):
    def run_check(self, parameter_nodes: Dict[str, ParameterNode]) -> List[BreakingChange]:
        ...
