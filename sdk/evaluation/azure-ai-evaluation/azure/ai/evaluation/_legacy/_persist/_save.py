# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import inspect

from enum import Enum
from os import PathLike
from ruamel.yaml import YAML
from pathlib import Path
import shutil
from typing import (
    Final,
    Mapping,
    Optional,
    Type,
    Union,
    Dict,
    Any,
    Callable,
    cast
)
from azure.ai.evaluation._constants import DefaultOpenEncoding
from azure.ai.evaluation._legacy._common._type_helpers import TypeMetadata, ValueType, extract_type_metadata
from azure.ai.evaluation._legacy._persist._callable_metadata import CallableMetadata, CallableArgMetadata
from azure.ai.evaluation._legacy._persist._exceptions import EvaluationSaveError, EvaluationLoadError
from azure.ai.evaluation._legacy._persist._loaded_evaluator import LoadedEvaluator


NOT_CALLABLE_ERR_MSG: Final[str] = "evaluator must be a function or a callable class"
YAML_FILE_NAME: Final[str] = "flow.flex.yaml"



def _to_arg_meta(type_meta: TypeMetadata, include_default: bool = True) -> CallableArgMetadata:
    val_type = type_meta["value_type"]
    if val_type is None:
        raise EvaluationSaveError(
            f"Unsupported type {type_meta['type']!r} for value type conversion. Supported types are: "
            f"{ValueType.__members__.keys()}",
        )

    meta: CallableArgMetadata = {
        "type": val_type.value
    }

    if include_default:
        if isinstance(type_meta["default"], Enum):
            meta["default"] = str(type_meta["default"].value)
        elif type_meta["default"] not in [inspect.Parameter.empty, None]:
            meta["default"] = str(type_meta["default"])

    return meta


def save_evaluator(
    evaluator: Callable,
    path: Union[str, PathLike],
    *,
    python_requirements_txt: Optional[str] = None,
    image: Optional[str] = None
) -> None:
    """Saves an evaluator to the specified directory
    
    :param Callable evaluator: The evaluator to save.
    :param Union[str, PathLike] path: The directory to save the evaluator to.
    :param Optional[str] python_requirements_txt: The path to the Python requirements file.
    :param Optional[str] image: The image to use for the evaluator.
    """

    func: Callable
    cls: Optional[Type]
    include_output: bool
    if inspect.isfunction(evaluator):
        func = evaluator
        cls = None
        include_output = True
    elif inspect.isclass(evaluator):
        if not hasattr(evaluator, "__call__"):
            raise EvaluationSaveError(NOT_CALLABLE_ERR_MSG)
        func = evaluator.__call__
        cls = evaluator
        include_output = False
    else:
        raise EvaluationSaveError(NOT_CALLABLE_ERR_MSG)

    source = Path(inspect.getfile(func))
    code_dir: Path = source.parent

    # Generate metadata about the callable to be saved
    meta: CallableMetadata = {
        "entry": f"{source.stem}:{evaluator.__name__}",
    }

    arg_metadata: Mapping[str, TypeMetadata] = extract_type_metadata(func)
    inputs: Mapping[str, CallableArgMetadata] = {
        k: _to_arg_meta(v)
        for k,v in arg_metadata.items()
        if k != "return"
    }
    if inputs:
        meta["inputs"] = inputs

    if include_output and "return" in arg_metadata:
        out_val_type: Type = ValueType.resolve_type(arg_metadata["return"]["type"])
        expanded_type: Mapping[str, TypeMetadata] = extract_type_metadata(out_val_type)
        if expanded_type:
            meta["outputs"] = {
                k: _to_arg_meta(v, False)
                for k, v in expanded_type.items()
            }
        else:
            meta["outputs"] = { "output": _to_arg_meta(arg_metadata["return"], False) }

    if cls:
        init_metadata = extract_type_metadata(cls.__init__)
        init = {k: _to_arg_meta(v) for k,v in init_metadata.items() if k != "return" and v}
        if init:
            meta["init"] = init

    if python_requirements_txt:
        filename: str = Path(python_requirements_txt).name
        if (code_dir / filename).exists():
            python_requirements_txt = filename
    elif (code_dir / "requirements.txt").exists():
        python_requirements_txt = "requirements.txt"

    if python_requirements_txt:
        env: Dict[str, Any] = meta.setdefault("environment", {})
        env["python_requirements_txt"] = python_requirements_txt

    if image:
        env = meta.setdefault("environment", {})
        env["image"] = image

    # Create the directory structure and save the callable file and metadata
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if len(list(path.iterdir())) > 0:
        raise EvaluationSaveError(f"The '{str(path)}' directory is not empty. Please provide an empty directory.")

    shutil.copytree(
        code_dir,
        path,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))

    if python_requirements_txt:
        shutil.copy(
            python_requirements_txt,
            path / Path(python_requirements_txt).name
        )

    with open(path / "flow.flex.yaml", "w", encoding=DefaultOpenEncoding.WRITE) as flex:
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.dump(meta, flex)


def load_evaluator(path: Union[str, PathLike], **kwargs: Any) -> LoadedEvaluator:
    """Loads an evaluator from the specified directory. Any kwargs are passed to the evaluator's
    constructor.

    :param Union[str, PathLike] path: The directory to load the evaluator from.
    :return: The loaded evaluator.
    :rtype: LoadedEvaluator
    """
    path = Path(path).resolve()
    if not path.exists():
        raise EvaluationLoadError(f"Path '{path}' does not exist.")

    # TODO ralphe: Support prompty files as well?
    if path.is_file():
        if path.name != YAML_FILE_NAME:
            raise EvaluationLoadError(f"Path '{path}' is not a valid flow flex file.")
    else:
        path = path / YAML_FILE_NAME
        if not path.exists():
            raise EvaluationLoadError(f"Flow flex file '{path}' does not exist.")

    meta: CallableMetadata
    with open(path, encoding=DefaultOpenEncoding.READ) as flex:
        yaml = YAML()
        yaml.preserve_quotes = True
        loaded = yaml.load(flex)
        expected_keys = set(extract_type_metadata(CallableMetadata).keys())
        meta = cast(
            CallableMetadata,
            { k: v for k,v in loaded.items() if k in expected_keys and v is not None }
        )

    # Quick validation checks of loaded metadata
    if "entry" not in meta or not isinstance(meta["entry"], str):
        raise EvaluationLoadError("Missing or invalid 'entry' in flow flex file.")
    # TODO ralphe: More validation checks of inputs, outputs, or init args?

    return LoadedEvaluator(meta, path.parent, **kwargs)