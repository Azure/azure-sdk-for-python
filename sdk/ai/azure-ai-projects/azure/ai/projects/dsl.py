# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Python function authoring for Foundry command components and pipeline jobs."""

import ast
import inspect
import textwrap
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, get_type_hints, overload

from ._component_source import _ComponentSource, _RUNNER_NAME, _source_for_component, _stage_component_source
from .models import AssetTypes, CommandJob, Input, InputOutputModes, JobResourceConfiguration, PipelineJob
from .models import Output as _JobOutput

# Keep Input available for explicit imports without documenting the same model twice in Sphinx.
__all__ = ["Output", "component", "pipeline"]


@dataclass(frozen=True)
class Output:
    """A writable file output in a Python component signature.

    The parameter name becomes the output asset name. Outputs are read-write mounted
    unless ``mode`` is specified.
    """

    type: Union[str, AssetTypes]
    mode: Optional[Union[str, InputOutputModes]] = None


@dataclass(frozen=True)
class _Port:
    name: str
    type: str
    conversion: str
    mode: Optional[Union[str, InputOutputModes]] = None


@dataclass(frozen=True)
class _InputRef:
    owner: object
    name: str
    type: str


@dataclass(frozen=True)
class _OutputRef:
    owner: object
    node: str
    name: str
    type: str
    mode: Union[str, InputOutputModes]


_ACTIVE_PIPELINE: ContextVar[Optional["_PipelineContext"]] = ContextVar("foundry_pipeline", default=None)
_PRIMITIVES: Dict[Any, Tuple[str, str]] = {
    str: ("string", "str"),
    int: ("integer", "int"),
    float: ("number", "float"),
    bool: ("boolean", "bool"),
}


def _component_ports(func: Callable[..., Any]) -> Tuple[List[_Port], List[_Port]]:
    inputs: List[_Port] = []
    outputs: List[_Port] = []
    annotations = get_type_hints(func)
    for parameter in inspect.signature(func).parameters.values():
        if parameter.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(f"Component '{func.__name__}' supports only named parameters.")
        annotation = annotations.get(parameter.name, parameter.annotation)
        if isinstance(annotation, Output):
            if annotation.type != AssetTypes.URI_FILE:
                raise ValueError(f"Component output '{parameter.name}' must be a uri_file.")
            if parameter.default is not inspect.Parameter.empty:
                raise TypeError(f"Component output '{parameter.name}' cannot have a default.")
            outputs.append(
                _Port(
                    parameter.name,
                    AssetTypes.URI_FILE,
                    "str",
                    annotation.mode if annotation.mode is not None else InputOutputModes.READ_WRITE_MOUNT,
                )
            )
        elif isinstance(annotation, Input):
            if annotation.type != AssetTypes.URI_FILE or annotation.path or annotation.value or annotation.mode:
                raise ValueError(f"Component input '{parameter.name}' supports only Input(type='uri_file').")
            inputs.append(_Port(parameter.name, AssetTypes.URI_FILE, "str"))
        elif annotation in _PRIMITIVES:
            component_type, conversion = _PRIMITIVES[annotation]
            inputs.append(_Port(parameter.name, component_type, conversion))
        else:
            raise TypeError(f"Component parameter '{parameter.name}' needs a primitive, Input, or Output annotation.")
    return inputs, outputs


def _function_script(func: Callable[..., Any], inputs: List[_Port], outputs: List[_Port]) -> str:
    try:
        source_file = inspect.getsourcefile(func)
        if source_file is None:
            raise OSError("no source file")
        function_tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
        module_tree = ast.parse(Path(source_file).read_text(encoding="utf-8"))
    except (OSError, TypeError, SyntaxError) as error:
        raise ValueError(f"Component '{func.__name__}' must be defined in a readable Python source file.") from error

    if len(function_tree.body) != 1 or not isinstance(function_tree.body[0], ast.FunctionDef):
        raise TypeError(f"Component '{func.__name__}' must be a synchronous Python function.")
    definition = function_tree.body[0]
    if definition.name != func.__name__:
        raise ValueError(f"Component '{func.__name__}' must be defined by its original function name.")

    free_vars = inspect.getclosurevars(func)
    if free_vars.nonlocals:
        raise ValueError(
            f"Component '{func.__name__}' cannot capture enclosing variables: {sorted(free_vars.nonlocals)}."
        )
    globals_needed = set(free_vars.globals)
    imports: List[str] = []
    for statement in module_tree.body:
        if isinstance(statement, ast.Import):
            names = {alias.asname or alias.name.split(".")[0] for alias in statement.names}
        elif isinstance(statement, ast.ImportFrom):
            names = {alias.asname or alias.name for alias in statement.names}
        else:
            continue
        if names & globals_needed:
            imports.append(ast.unparse(statement))
            globals_needed -= names
    if globals_needed:
        raise ValueError(
            f"Component '{func.__name__}' uses unsupported module globals: {sorted(globals_needed)}. "
            "Import dependencies at module scope or inside the function."
        )

    definition.decorator_list = []
    definition.returns = None
    for parameter in definition.args.posonlyargs + definition.args.args + definition.args.kwonlyargs:
        parameter.annotation = None
    definition.args.defaults = []
    definition.args.kw_defaults = [None] * len(definition.args.kwonlyargs)

    arguments: List[str] = []
    for index, port in enumerate(inputs + outputs, start=1):
        value = f"sys.argv[{index}]"
        if port.conversion == "bool":
            value = f"({value} == 'True')"
        elif port.conversion != "str":
            value = f"{port.conversion}({value})"
        arguments.append(f"{port.name}={value}")

    return "\n".join(
        ["import sys", *imports, "", ast.unparse(definition), "", "if __name__ == '__main__':"]
        + [f"    {definition.name}({', '.join(arguments)})", ""]
    )


class _PipelineContext:
    def __init__(self, compute_id: str, image: str, identity: str, instance_type: str) -> None:
        self.compute_id = compute_id
        self.image = image
        self.identity = identity
        self.instance_type = instance_type
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.code_dirs: List[TemporaryDirectory] = []
        self.code_dirs_by_root: Dict[Path, TemporaryDirectory] = {}

    def add(
        self,
        func: Callable[..., Any],
        inputs: List[_Port],
        outputs: List[_Port],
        arguments: Dict[str, Any],
        source: Optional[_ComponentSource],
    ) -> SimpleNamespace:
        name = func.__name__
        suffix = 2
        while name in self.jobs:
            name = f"{func.__name__}_{suffix}"
            suffix += 1

        bound_inputs: Dict[str, Input] = {}
        for port in inputs:
            value = arguments[port.name]
            if isinstance(value, _InputRef):
                if value.owner is not self or value.type != port.type:
                    raise ValueError(f"Component input '{port.name}' has an incompatible pipeline input.")
                serialized = f"${{{{parent.inputs.{value.name}}}}}"
            elif isinstance(value, _OutputRef):
                if value.owner is not self or value.type != port.type:
                    raise ValueError(f"Component input '{port.name}' has an incompatible node output.")
                serialized = f"${{{{parent.jobs.{value.node}.outputs.{value.name}}}}}"
            elif port.type == AssetTypes.URI_FILE:
                raise TypeError(f"Component input '{port.name}' needs a pipeline input or node file output.")
            elif (
                (port.conversion == "int" and type(value) is int)
                or (port.conversion == "float" and type(value) is float)
                or (port.conversion == "bool" and type(value) is bool)
                or (port.conversion == "str" and type(value) is str)
            ):
                serialized = str(value)
            else:
                raise TypeError(f"Component input '{port.name}' has an incompatible primitive value.")
            input_type = AssetTypes.URI_FILE if port.type == AssetTypes.URI_FILE else AssetTypes.LITERAL
            bound_inputs[port.name] = Input(type=input_type, value=serialized)

        arguments_in_command = " ".join(
            [f'"${{{{inputs.{port.name}}}}}"' for port in inputs]
            + [f'"${{{{outputs.{port.name}}}}}"' for port in outputs]
        )
        if source is None:
            code_dir = TemporaryDirectory(prefix="foundry-component-")
            self.code_dirs.append(code_dir)
            (Path(code_dir.name) / "component.py").write_text(_function_script(func, inputs, outputs), encoding="utf-8")
            command = "python component.py " + arguments_in_command
        else:
            shared_code_dir = self.code_dirs_by_root.get(source.root)
            if shared_code_dir is None:
                code_dir = TemporaryDirectory(prefix="foundry-component-source-")
                self.code_dirs.append(code_dir)
                self.code_dirs_by_root[source.root] = code_dir
                _stage_component_source(source.root, Path(code_dir.name))
            else:
                code_dir = shared_code_dir
            if not (Path(code_dir.name) / source.relative_file).is_file():
                raise ValueError(f"Component '{func.__name__}' source file is excluded by its code ignore rules.")
            port_spec = ",".join(f"{port.name}:{port.conversion}" for port in inputs + outputs) or "-"
            command = f"python {_RUNNER_NAME} {source.module} {func.__name__} {port_spec}"
            if arguments_in_command:
                command += " " + arguments_in_command

        job = CommandJob(
            command=command,
            code=code_dir.name,
            environment_image_reference=self.image,
            compute=self.compute_id,
            user_assigned_identity_id=self.identity,
            resources=JobResourceConfiguration(
                {
                    "instanceCount": 1,
                    "instanceType": self.instance_type,
                    "properties": {"AISuperComputer": {"SLATier": "Premium"}},
                }
            ),
            inputs=bound_inputs,
            outputs={port.name: _JobOutput(type=port.type, asset_name=port.name, mode=port.mode) for port in outputs},
        )
        node = PipelineJob._command_node(name, job, self.compute_id)
        for port in inputs:
            if port.type != AssetTypes.URI_FILE:
                node["component"]["inputs"][port.name]["type"] = port.type
        self.jobs[name] = node
        return SimpleNamespace(
            outputs=SimpleNamespace(
                **{
                    port.name: _OutputRef(
                        self, name, port.name, port.type, port.mode or InputOutputModes.READ_WRITE_MOUNT
                    )
                    for port in outputs
                }
            )
        )


@overload
def component(
    func: Callable[..., Any], *, code: Optional[Union[str, PathLike[str]]] = None
) -> Callable[..., SimpleNamespace]: ...


@overload
def component(
    func: None = None, *, code: Optional[Union[str, PathLike[str]]] = None
) -> Callable[[Callable[..., Any]], Callable[..., SimpleNamespace]]: ...


def component(
    func: Optional[Callable[..., Any]] = None, *, code: Optional[Union[str, PathLike[str]]] = None
) -> Union[Callable[..., SimpleNamespace], Callable[[Callable[..., Any]], Callable[..., SimpleNamespace]]]:
    """Decorate a Python function to create a command node when invoked inside a pipeline.

    With ``code``, snapshot that directory and import the original module at runtime.
    Otherwise, package the function body as a standalone script. Code-backed components
    require the authoring SDK and their other imports in the container image.
    """

    def decorate(source_func: Callable[..., Any]) -> Callable[..., SimpleNamespace]:
        inputs, outputs = _component_ports(source_func)
        source = _source_for_component(source_func, code) if code is not None else None
        input_names = {port.name for port in inputs}
        input_signature = inspect.Signature(
            [
                parameter
                for parameter in inspect.signature(source_func).parameters.values()
                if parameter.name in input_names
            ]
        )

        @wraps(source_func)
        def invoke(**kwargs: Any) -> SimpleNamespace:
            context = _ACTIVE_PIPELINE.get()
            if context is None:
                raise RuntimeError(f"Component '{source_func.__name__}' must be called inside a @pipeline function.")
            bound = input_signature.bind(**kwargs)
            bound.apply_defaults()
            return context.add(source_func, inputs, outputs, dict(bound.arguments), source)

        return invoke

    return decorate(func) if func is not None else decorate


command_component = component


def pipeline(
    *,
    compute_id: str,
    environment_image_reference: str,
    user_assigned_identity_id: str,
    instance_type: str,
) -> Callable[[Callable[..., Any]], Callable[..., PipelineJob]]:
    """Decorate a pipeline builder; calling it returns a native Foundry PipelineJob.

    Compute, image, identity, and instance type are inherited by each command node.
    """

    def decorate(func: Callable[..., Any]) -> Callable[..., PipelineJob]:
        signature = inspect.signature(func)
        annotations = get_type_hints(func)

        @wraps(func)
        def build(*args: Any, **kwargs: Any) -> PipelineJob:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            context = _PipelineContext(
                compute_id, environment_image_reference, user_assigned_identity_id, instance_type
            )
            job_inputs: Dict[str, Input] = {}
            references: Dict[str, _InputRef] = {}
            for name, value in bound.arguments.items():
                annotation = annotations.get(name, signature.parameters[name].annotation)
                if isinstance(annotation, Input):
                    if (
                        annotation.type != AssetTypes.URI_FILE
                        or not isinstance(value, Input)
                        or value.type != AssetTypes.URI_FILE
                    ):
                        raise TypeError(f"Pipeline input '{name}' requires Input(type='uri_file', path=...).")
                    if not value.path or "://" not in value.path:
                        raise ValueError(
                            f"Pipeline input '{name}' requires a remote URI; local files are not supported."
                        )
                    job_inputs[name] = value
                    port_type: str = AssetTypes.URI_FILE
                elif annotation in _PRIMITIVES and type(value) is annotation:
                    job_inputs[name] = Input(type=AssetTypes.LITERAL, value=str(value))
                    port_type = _PRIMITIVES[annotation][0]
                else:
                    raise TypeError(f"Pipeline input '{name}' needs a matching primitive or uri_file Input value.")
                references[name] = _InputRef(context, name, port_type)

            token = _ACTIVE_PIPELINE.set(context)
            job: Optional[PipelineJob] = None
            try:
                try:
                    result = func(**references)
                finally:
                    _ACTIVE_PIPELINE.reset(token)
                job_outputs: Dict[str, Dict[str, Any]] = {}
                if result is not None:
                    if not isinstance(result, dict):
                        raise TypeError("Pipeline outputs must be returned as a dictionary of node outputs.")
                    for name, value in result.items():
                        if not isinstance(value, _OutputRef) or value.owner is not context:
                            raise TypeError(f"Pipeline output '{name}' must reference an output from this pipeline.")
                        node_output = context.jobs[value.node]["outputs"][value.name]
                        if "path" in node_output:
                            raise ValueError(
                                f"Node output '{value.node}.{value.name}' cannot bind to multiple pipeline outputs."
                            )
                        node_output["path"] = f"${{{{parent.outputs.{name}}}}}"
                        job_outputs[name] = {"jobOutputType": value.type, "mode": value.mode}

                job = PipelineJob(
                    display_name=func.__name__,
                    compute_id=compute_id,
                    settings={"default_compute": compute_id, "force_rerun": True},
                    inputs=job_inputs,
                    outputs=job_outputs,
                    jobs=context.jobs,
                )
                job._component_code_dirs = context.code_dirs
                return job
            finally:
                if job is None:
                    for directory in context.code_dirs:
                        directory.cleanup()

        return build

    return decorate
